---
aliases:
  - Background Task Supervisor
  - Task Supervisor
  - Background Work Management
tags:
  - sdd
  - spec
  - concurrency
  - background-work
created: 2026-04-11
status: partial
related:
  - "[[MOC-specs]]"
  - "[[002-agent-loop/spec]]"
  - "[[036-prometheus-metrics/spec]]"
  - "[[001-system-invariants/spec#5. Concurrency Contract]]"
---

# Spec: Supervised Background Task Manager

> [!info]
> **Phase 1 (core supervisor, JoinSet, per-class limits, drop policy, metrics)** is implemented as of PR #2816 (commit 81f2d28a).
> This spec documents the Phase 1 implementation and tracks Phase 2 enhancements in GitHub Epic #2883.

**Issue**: #2816  
**Epic**: #2883  
**Status**: Phase 1 complete, Phase 2 in design  
**Crate**: `zeph-core::agent::supervisor`  
**Dependencies**: spec [[002-agent-loop/spec]], [[036-prometheus-metrics/spec]]

---

## 1. Problem Statement

The agent loop spawns background work in multiple places with `tokio::spawn()`:

```rust
// Embedding backfill (memory)
tokio::spawn(async move { backfill_embeddings().await; });

// Skill self-learning
tokio::spawn(async move { learn_from_feedback().await; });

// Metric export
tokio::spawn(async move { export_metrics().await; });

// Hook execution
tokio::spawn(async move { fire_hooks().await; });
```

### 1.1 Current Issues

| Issue | Impact | Example |
|-------|--------|---------|
| **No supervision** | Spawned tasks are dropped and untrackable | Backfill task crashes silently; no log, no metrics |
| **Unbounded spawns** | Can exceed OS limits or exhaust memory | Embedding backfill spawns per message; loop spawns 1000s of tasks without bound |
| **No lifecycle control** | Tasks persist after turn boundary | A slow embedding task from turn 1 is still running at turn 10 |
| **Weak observability** | No count of inflight tasks, dropped work, or completion rate | TUI shows no background work; `bg_inflight` metric unimplemented |
| **Contention with loop** | Background tasks compete for LLM API calls and shared state | Embedding backfill blocks memory access, slowing compaction |
| **Orphaned tasks on shutdown** | Tasks continue after agent exits | Agent closes; embedding backfill task still running, consuming resources |

### 1.2 Business Impact

- **Degraded UX**: Agent feels sluggish because background work starves foreground tasks
- **Incorrect metrics**: Prometheus gaps for `bg_inflight`, `bg_dropped` hamper observability
- **Cost overrun**: Orphaned embeddings continue calling the provider after the agent exits
- **Hard-to-debug bugs**: Silent task failures leave no trace in logs

---

## 2. Solution: BackgroundSupervisor

A lightweight supervisor that:

1. Tracks all background tasks per agent session via `tokio::task::JoinSet<TaskResult>`
2. Enforces per-class concurrency limits (not queue depth; see Phase 2E)
3. Drops work immediately when class limit is reached (drop-on-overflow policy)
4. Exports per-class metrics for observability
5. Cleans up all tasks at agent shutdown with `abort_all()`

### 2.1 Phase 1 Implementation

**Struct**: `BackgroundSupervisor` at `crates/zeph-core/src/agent/supervisor.rs`

**Key design**:
- Owned by `LifecycleState` (single agent per session), accessed via `&mut self` — no locks needed
- Per-class inflight counter using `Arc<AtomicUsize>` (read-only from spawned tasks)
- RAII `InflightGuard` decrements inflight immediately on task completion (not at `reap()` time)
- `reap()` called non-blocking at turn boundary to drain completed tasks
- `abort_all()` called on agent shutdown (no graceful drain — tasks are lossy by design)

**Location in agent loop**:
```
persistence.rs:
  - spawn_summarization()        [line 602]
  - spawn() for enrichment tasks [lines 734, 780, 880, 942]
corrections.rs:
  - spawn() for audit tasks     [lines 122, 173]
mod.rs:
  - reap() at turn boundary     [line 1047]
  - abort_all() on shutdown     [line 646]
```

### 2.2 Architecture

```
BackgroundSupervisor (owned by LifecycleState)
├── JoinSet<TaskResult> (all inflight tasks)
├── class_inflight: [Arc<AtomicUsize>; 2]
│   └── [0] Enrichment (limit 4)
│   └── [1] Telemetry (limit 8)
├── class_metrics: [ClassMetrics; 2]
│   ├── spawned: u64
│   ├── dropped: u64
│   └── completed: u64
└── SummarizationSignal (communicates summarization completion to foreground)
```

---

## 3. Task Priority Classes (Phase 1)

Only two classes are implemented in Phase 1. A proposed `Critical` class is **not needed** — see rationale below.

| Class | Limit | Policy | Examples |
|-------|-------|--------|----------|
| **Enrichment** | 4 concurrent | Drop on limit | Summarization, graph/persona/trajectory extraction, audit logs |
| **Telemetry** | 8 concurrent | Drop on limit | Metrics export, graph count sync |

### 3.1 Rationale

- **Enrichment**: "Nice-to-have" background work that enriches memory and observability. Can be safely dropped when limit is exceeded. Lossy by design.
- **Telemetry**: Faster background metrics/state updates. Larger limit because these are cheap operations.
- **Critical class NOT NEEDED**: Critical work (LLM calls, tool execution, message persistence) runs on the foreground `await` path in `persist_message()` and `execute_tool_calls_batch()`. It is never spawned as background work — concurrency control for critical operations is the responsibility of the foreground loop and timeout guards. Background tasks are explicitly lossy.

---

## 4. Concurrency Limits (Phase 1)

### 4.1 Current Implementation

Limits are **hardcoded** per class (not configurable in Phase 1):

```rust
impl TaskClass {
    fn max_concurrency(self) -> usize {
        match self {
            TaskClass::Enrichment => 4,
            TaskClass::Telemetry => 8,
        }
    }
}
```

When a spawn request arrives for a class at its limit, the task is dropped immediately (not queued):

```rust
let current = self.class_inflight[idx].load(Ordering::Relaxed);
if current >= class.max_concurrency() {
    // Task is dropped, bg_dropped counter incremented
    self.class_metrics[idx].dropped += 1;
    return false;
}
```

### 4.2 Phase 2E: Configurable Depths (#2888)

Future enhancement to move limits to config:

```toml
[agent.supervisor]
enrichment_limit = 4
telemetry_limit = 8
```

### 4.3 Turn-Boundary Cleanup

**Phase 1 status**: Turn-boundary abort does NOT happen automatically. Tasks continue across turn boundaries.

**Phase 2D (#2887)**: Explicit `abort_class(TaskClass::Enrichment)` call to be added at turn boundary in agent loop to prevent backlog buildup.

---

## 5. Integration with Agent Loop (Phase 1)

### 5.1 API

```rust
pub(crate) struct BackgroundSupervisor {
    tasks: JoinSet<TaskResult>,
    class_inflight: [Arc<AtomicUsize>; NUM_CLASSES],
    class_metrics: [ClassMetrics; NUM_CLASSES],
}

impl BackgroundSupervisor {
    /// Create a new supervisor for the agent session.
    pub(crate) fn new() -> Self { ... }
    
    /// Spawn a background task under `class`.
    /// Returns `true` when accepted, `false` when dropped due to class limit.
    pub(crate) fn spawn(
        &mut self,
        class: TaskClass,
        name: &'static str,
        fut: impl Future<Output = ()> + Send + 'static,
    ) -> bool { ... }
    
    /// Variant for summarization tasks that signal completion via `SummarizationSignal`.
    pub(crate) fn spawn_summarization(
        &mut self,
        name: &'static str,
        fut: impl Future<Output = bool> + Send + 'static,
    ) -> bool { ... }
    
    /// Poll all completed tasks without blocking.
    /// Returns `SummarizationSignal` if background summarization completed.
    pub(crate) fn reap(&mut self) -> SummarizationSignal { ... }
    
    /// Abort all inflight tasks immediately (called at agent shutdown).
    pub(crate) fn abort_all(&mut self) { ... }
    
    /// Get total inflight task count across all classes.
    pub(crate) fn inflight(&self) -> usize { ... }
    
    /// Snapshot of current metrics (spawned / dropped / completed per class).
    pub(crate) fn metrics_snapshot(&self) -> SupervisorMetrics { ... }
}
```

### 5.2 Usage Pattern

Spawning from `persist_message()`:

```rust
// persistence.rs:602
self.lifecycle.supervisor.spawn_summarization("summarization", async move {
    let did_summarize = maybe_summarize_older_pairs(...).await?;
    Ok(did_summarize)
});

// persistence.rs:734 — graph extraction
self.lifecycle.supervisor.spawn(
    TaskClass::Enrichment,
    "graph-extract",
    async move {
        extract_and_sync_graph(...).await.ok();
    },
);
```

Reaping at turn boundary (`mod.rs:1047`):

```rust
let bg_signal = self.lifecycle.supervisor.reap();
if bg_signal.did_summarize {
    self.lifecycle.state.msg.unsummarized_count = 0;
}
```

Cleanup at shutdown (`mod.rs:646`):

```rust
self.lifecycle.supervisor.abort_all();
```

---

## 6. Observability & Metrics (Phase 1 & Phase 2)

### 6.1 Phase 1 Metrics (Implemented)

The supervisor tracks per-class counters in `ClassMetrics`:

| Metric | Type | Exported | Unit | Notes |
|--------|------|----------|------|-------|
| `spawned` | Counter | To Prometheus as `bg_spawned` | tasks | Total tasks spawned since agent start |
| `dropped` | Counter | To Prometheus as `bg_dropped` | tasks | Total tasks dropped due to class limit |
| `completed` | Counter | To Prometheus as `bg_completed` | tasks | Total tasks completed (success or panic) |
| `inflight` | Gauge | To Prometheus as `bg_inflight` | tasks | Current count of tasks in flight (not queued — actually running) |

Metrics are snapshottable via `metrics_snapshot()` for logging and TUI display.

### 6.2 Phase 2B: Per-Class Latency Histogram (#2885)

**Not yet implemented**. Future enhancement to track task completion time:

```
bg_latency_seconds histogram
  labels: class (enrichment | telemetry)
  buckets: [0.001, 0.01, 0.1, 0.5, 1.0, 5.0]
```

### 6.3 Phase 2C: TUI Status Display (#2886)

**Not yet implemented**. Future enhancement to show background task counts in TUI status bar:

```
bg: 2 enrich, 1 telem | ↻ summarizing...
```

Meaning: 2 enrichment tasks inflight, 1 telemetry task, with current operation being summarization.

---

## 7. Task Naming (Phase 1)

Each spawned task is tagged with a `name: &'static str` parameter for logging and diagnostics:

```rust
supervisor.spawn(
    TaskClass::Enrichment,
    "graph-extract",    // task name for logs
    async move { ... },
);

supervisor.spawn_summarization(
    "summarization",    // task name for logs
    async { true },
);
```

Task names appear in debug-level logs:

```
TRACE: background task spawned class=enrichment task=graph-extract
TRACE: background task dropped class=enrichment task=graph-extract limit=4
```

**Phase 2 Note**: Task tagging and coalescing (skipping duplicate kinds) are **not implemented** in Phase 1. All tasks are spawned if slot is available.

---

## 8. Key Invariants

### Always
- All spawned tasks are tracked in a `JoinSet<TaskResult>` (never dropped, never orphaned)
- Per-class inflight counters are updated atomically via `Arc<AtomicUsize>`
- When a task completes, its inflight slot is freed immediately (via `InflightGuard` drop)
- `reap()` is non-blocking and idempotent — safe to call every turn
- Enrichment class tasks can be dropped at concurrency limit without data loss
- Telemetry class tasks are dropped when limit is exceeded
- At agent shutdown, `abort_all()` cancels all inflight tasks gracefully
- Metrics snapshots are consistent (spawned ≥ dropped + completed at any point in time)

### Ask First
- Adding new background task spawn sites outside the supervisor (escalate to team lead for decision)
- Changing per-class concurrency limits without testing load behavior

### Never
- Spawn a task with `tokio::spawn()` directly — always use `supervisor.spawn()` or `spawn_summarization()`
- Hold a lock across `supervisor.spawn()` call (deadlock risk with the inflight atomic)
- Allow background tasks to panic — all spawned futures must be wrapped in proper error handling
- Assume a background task completed successfully without checking metrics

---

## 9. Example: Embedding Backfill

Current code (problematic):

```rust
// In memory compaction logic
tokio::spawn(async move {
    match backfill_embeddings(&messages).await {
        Ok(_) => {}, // silently succeeds
        Err(e) => {}, // silently fails, no log
    }
});
```

With supervisor:

```rust
// In memory compaction logic
supervisor.spawn(
    TaskClass::Enrichment,
    async {
        match backfill_embeddings(&messages).await {
            Ok(_) => {
                tracing::debug!("embedding backfill completed");
                Ok(())
            }
            Err(e) => {
                tracing::warn!("embedding backfill failed: {e}");
                Err(TaskError::Backfill(e.to_string()))
            }
        }
    }
);
```

Benefits:

- ✅ Task is counted in `bg_inflight` gauge
- ✅ On completion, `bg_completed` is incremented
- ✅ If queue depth is exceeded, new backfill is dropped, `bg_dropped` incremented
- ✅ At turn boundary, backfill is aborted (prevents stale work blocking new turns)
- ✅ TUI shows background activity: `bg: 1 enrich`
- ✅ At shutdown, backfill is cleanly cancelled

---

## 10. Out of Scope

The following systems are **explicitly excluded** from the supervisor's purview:

- **Infrastructure loops** (~18 process-scoped `tokio::spawn` calls): Memory sweeps, channel watchers, session digest threads, scheduler loops. These have their own `CancellationToken` lifecycle, are NOT turn-scoped, and belong to their own subsystem lifecycle managers. Do NOT wrap these in `BackgroundSupervisor`.
- **Critical path tasks**: LLM calls, tool execution, message persistence. These run on the foreground `await` path with timeout guards and are not background work.
- **Task coalescing and kind tracking**: Deduplication of identical task kinds is a Phase 2 enhancement and not part of Phase 1.
- **Turn-boundary abort**: Automatic cleanup of enrichment tasks at turn boundaries is Phase 2D (#2887).

---

## 11. Open Questions (Resolved)

1. **Turn-boundary abort location** — RESOLVED
   - Chosen: Option A (explicit call in agent loop)
   - Status: Not implemented in Phase 1; see Phase 2D (#2887)

2. **Critical class limits** — RESOLVED
   - Decision: Critical class not needed — all critical work is foreground
   - Rationale: LLM calls, tool execution, message persistence run on the main `await` path with timeout guards. Background tasks are inherently lossy. No background task is critical.

3. **Task error handling** — RESOLVED
   - Policy: Log at debug level on completion, warn if task panics
   - No retry — transient failures are acceptable for lossy background work
   - Implementation: Panics logged via `Err` branch in `reap()` at warn level

---

## 12. Success Criteria

### Phase 1 (Completed)

- [x] `BackgroundSupervisor` struct compiles and integrates with agent loop (PR #2816)
- [x] Five Enrichment task sites use the supervisor: summarization, graph/persona/trajectory extraction, audit logging (persistence.rs, corrections.rs)
- [x] Per-class inflight limits enforced: Enrichment 4, Telemetry 8
- [x] Metrics (`spawned`, `dropped`, `completed`, `inflight`) exported per class
- [x] All background tasks cleaned up on agent shutdown via `abort_all()`
- [x] Five unit tests covering: spawn/reap, drop on overflow, summarization signal, abort all, inflight decrement timing
- [x] `SummarizationSignal` enables foreground reset of `unsummarized_count` without shared state

### Phase 2 (Planned)

- [ ] Phase 2A (#2884): Route remaining 8 fire-and-forget spawns through supervisor
- [ ] Phase 2B (#2885): Per-class `bg_latency` histogram exported
- [ ] Phase 2C (#2886): TUI status bar displays background task counts
- [ ] Phase 2D (#2887): Explicit turn-boundary `abort_class(TaskClass::Enrichment)` call
- [ ] Phase 2E (#2888): Queue depths configurable via `config.toml`
- [ ] Phase 2F (#2889): Tracing span propagation into supervised tasks

---

## 13. Phase 2 Implementation Plan

Roadmap for Phase 2 enhancements coordinated under Epic #2883:

| Issue | Phase | Priority | Title | Description |
|-------|-------|----------|-------|-------------|
| #2884 | 2A | P2 | Route remaining agent-path spawns | Move ~8 fire-and-forget `tokio::spawn()` calls in agent/memory/skills paths through the supervisor (audit logs, session digest, goal extraction, compaction, magic docs, embed backfill) |
| #2885 | 2B | P2 | Add bg_latency per-class histogram | Export task completion time histograms for Enrichment and Telemetry classes to Prometheus |
| #2886 | 2C | P3 | TUI background task display | Show background task counts in TUI status bar with spinner animation |
| #2887 | 2D | P2 | Turn-boundary abort for Enrichment | Add explicit `supervisor.abort_class(TaskClass::Enrichment)` call at end of turn to prevent backlog |
| #2888 | 2E | P3 | Configurable concurrency limits | Move hardcoded limits (4, 8) to config: `[agent.supervisor] enrichment_limit = ... telemetry_limit = ...` |
| #2889 | 2F | P4 | Span propagation (optional) | Propagate tracing spans from parent context into supervised background tasks for better observability |

---

## See Also

- [[MOC-specs]] — all specifications
- [[002-agent-loop/spec]] — agent loop structure and turn lifecycle
- [[036-prometheus-metrics/spec]] — metrics export and schema
- [[001-system-invariants/spec#5. Concurrency Contract]] — concurrency invariants
- GitHub PR #2816 — original implementation (Phase 1)
- GitHub Epic #2883 — Phase 2 coordination
