# zeph-orchestration Crate

Task orchestration engine for Zeph — DAG-based execution, failure propagation, and persistence.

## Purpose

`zeph-orchestration` coordinates complex multi-step tasks via a directed acyclic graph (DAG) execution model. Tasks can be executed in parallel, serially, or with custom failure handling strategies (abort, retry, skip, ask). Results are persisted to SQLite for recovery and audit.

## Key Types

- **TaskGraph** — DAG representation with nodes (tasks) and edges (dependencies)
- **DagScheduler** — Tick-based execution engine with concurrency limits
- **Task** — Unit of work with state (pending, running, completed, failed)
- **AgentRouter** — Routes tasks to appropriate agents/executors
- **LlmPlanner** — Decomposes goals into task DAGs using structured output
- **LlmAggregator** — Synthesizes task results with token budgeting

## Features

- **Dependency DAG** — Express complex workflows with explicit task dependencies
- **Parallel execution** — Execute independent tasks concurrently
- **Failure strategies** — abort / retry / skip / ask on task failure
- **Timeout enforcement** — Per-task and global timeouts with cancellation
- **Persistence** — SQLite storage for task state, recovery, and audit
- **LLM integration** — Goal decomposition via structured LLM calls
- **Result aggregation** — Synthesize multi-task outputs coherently

## Usage

```rust
use zeph_orchestration::{TaskGraph, DagScheduler, Task};

// Define a task DAG
let mut graph = TaskGraph::new();
let task_1 = graph.add_task("fetch_data", vec![]);
let task_2 = graph.add_task("process", vec![task_1]); // depends on task_1
let task_3 = graph.add_task("save", vec![task_2]);    // depends on task_2

// Execute
let mut scheduler = DagScheduler::new(graph);
while scheduler.tick() {
    // Process executor events
}
```

## Feature Flags

- **None** — orchestration is unconditional (always enabled)

## Dependencies

- `zeph-config` — OrchestrationConfig for tuning
- `zeph-subagent` — SubAgentDef for task-to-agent routing
- `zeph-common` — Shared utilities and text truncation
- `zeph-llm` — LlmProvider for decomposition and aggregation
- `zeph-memory` — Graph/RawGraphStore for task context storage
- `zeph-sanitizer` — ContentSanitizer for unsafe task results

## Integration with zeph-core

Re-exported via `zeph-core` as `crate::orchestration::*`:

```rust
use zeph_core::orchestration::{TaskGraph, DagScheduler, Task};
```

All public types are available via the re-export shim in `zeph-core/src/lib.rs`.

## Documentation

Full API documentation: [docs.rs/zeph-orchestration](https://docs.rs/zeph-orchestration/)

mdBook reference: [Orchestration](https://bug-ops.github.io/zeph/concepts/task-orchestration.html)

## License

MIT
