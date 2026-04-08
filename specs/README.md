# Zeph Specs

Feature principle documents — key invariants for coding agents.
See `constitution.md` for project-wide non-negotiable rules.

## System Invariants

| Doc | Contents |
|---|---|
| `001-system-invariants/spec.md` | Cross-cutting architectural invariants |

## Feature Docs

| Doc | Feature | Crate |
|---|---|---|
| `002-agent-loop/spec.md` | Agent loop, turn lifecycle, context pressure, HiAgent subgoal-aware compaction | `zeph-core` |
| `003-llm-providers/spec.md` | LlmProvider trait, AnyProvider, prompt caching | `zeph-llm` |
| `004-memory/spec.md` | SQLite + Qdrant, compaction, semantic response cache, anchored summarization, compaction probe, importance scoring, **A-MAC admission control**, **MemScene consolidation**; v0.18.1: Kumiho, D-MEM, cost-sensitive store routing, CraniMem, RL admission, Memex, ACON; v0.18.2: StoreRoutingConfig wired, goal_text propagated, AsyncMemoryRouter, SA timeout, tier promotion retry, orphan soft-delete, **multi-vector chunking** (real-time + batch), **GAAMA episode nodes**, **BATS budget hints + 5-way utility action policy**, **Focus compression + contextual tool embeddings + density-aware budgets**, **SleepGate forgetting pass + compression predictor**; v0.18.3: no new memory features; v0.18.4: **persona memory** (PR #2649), **trajectory memory** (PR #2689), **category-aware memory** (PR #2689), **TiMem tree** (PR #2689), **microcompact** (PR #2699), **autoDream** (PR #2697), **MagicDocs** (PR #2702); v0.18.6: **embed backfill micro-batches** (32 per batch, concurrency 4), **`embed_concurrency` config field**, **128k context budget fallback** | `zeph-memory` |
| `005-skills/spec.md` | SKILL.md format, registry, matching, hot-reload, **skill trust governance**; v0.18.1: two-stage matching, confusability report; v0.18.2: `disambiguation_threshold` 0.20, `min_injection_score` 0.20, **D2Skill** step-level error correction, **SkillOrchestra** LinUCB RL routing head (cold-start fallback), **channel allowlist** (`channels` frontmatter), **NL skill generation** + GitHub mining, SKILL.md injection sanitization + input hard block, trust fallback fix (Provisional not Trusted), `/skill create` dedup (Qdrant gap noted); v0.18.3: no new skill features | `zeph-skills` |
| `006-tools/spec.md` | ToolExecutor, CompositeExecutor, TAFC, schema filter, result cache, dependency graph, compress_context; v0.18.1: transactional ShellExecutor, utility-guided dispatch gate, adversarial policy gate; v0.18.2: structured shell output envelope, per-path file read sandbox, claim_source in audit, extract_paths relative path detection; v0.18.0: **tool invocation phase taxonomy** (Planner/Executor/Verifier/Autonomous), **reasoning model hallucination detection**; v0.18.3: no new tool features; v0.18.6: **legacy tool path removed** — all execution via native `tool_use`; `supports_tool_use()` default changed to `true`; `tool_use` bool field removed from provider configs | `zeph-tools` |
| `007-channels/spec.md` | Channel trait, AnyChannel dispatch, streaming, channel feature parity | `zeph-channels` |
| `008-mcp/spec.md` | MCP client, server lifecycle, semantic tool discovery, per-message pruning cache; v0.18.1: Roots, injection detection feedback, per-tool security metadata; v0.18.2: elicitation (Phase 1+2, bounded channel, sandboxed-server block, drain fix), tool collision detection, tool-list snapshot locking, per-server stdio env isolation, intent-anchor nonce wrapper; v0.18.3: **server instructions injection** (PR #2639); v0.18.4: **caller identity propagation** (`caller_id`), **tool quota** (`max_tool_calls_per_session`), **structured error codes** (`McpErrorCode` enum), **OAP authorization** (`[tools.authorization]`) | `zeph-mcp` |
| `009-orchestration/spec.md` | DAG planner, DagScheduler, AgentRouter, /plan, plan template cache, **VMAO adaptive replanning**; v0.18.1: **cascade-aware DAG routing** (`CascadeDetector`, `[orchestration] cascade_routing`), **tree-optimized dispatch** (`tree_optimized_dispatch`) | `zeph-orchestration` |
| `010-security/spec.md` | Vault, shell sandbox, content isolation, SSRF; v0.18.0: **IPI defense** (DeBERTa soft-signal, AlignSentinel 3-class, TurnCausalAnalyzer); v0.18.2: **PII NER circuit breaker + allowlist**, **cross-tool injection correlation**, **AgentRFC protocol audit**, **MCP→ACP confused-deputy boundary enforcement**, **SMCP lifecycle + IBCT tokens**, credential env-var scrubbing, **MCP tool input schema injection scan** (`flagged_parameters`); v0.18.3: no new security features | cross-cutting |
| `011-tui/spec.md` | ratatui dashboard, spinner rule, TuiChannel; v0.18.6: **RenderCache** (`clear()` releases memory, `shift()` for leading eviction), **embed backfill progress** in status bar | `zeph-tui` |
| `012-graph-memory/spec.md` | Entity graph, BFS recall, community detection, MAGMA typed edges, SYNAPSE spreading activation | `zeph-memory` |
| `013-acp/spec.md` | ACP transports, sessions, permissions, fork/resume; v0.18.2: **session/close handler**, **capability advertisement**, **/agent.json endpoint**, `agent-client-protocol 0.10.3`, `current_model` in SessionInfoUpdate | `zeph-acp` |
| `014-a2a/spec.md` | A2A protocol, agent discovery, JSON-RPC 2.0; v0.18.2: **IBCT** (Invocation-Bound Capability Tokens, HMAC-SHA256, `key_id` rotation, `X-Zeph-IBCT` header, `ibct` feature) | `zeph-a2a` |
| `015-self-learning/spec.md` | FeedbackDetector (multi-language), Wilson score, trust model, SAGE RL cross-session reward; v0.18.1: ARISE trace improvement, STEM pattern-to-skill (migration 057), ERL experiential learning (migration 058); v0.18.2: SkillOrchestra RL routing head and D2Skill step-correction documented in `005-skills/spec.md`; v0.18.3: **learning.rs split into 11 focused submodules** (no behavioral change, PR #2633) | `zeph-skills` |
| `016-output-filtering/spec.md` | FilterPipeline, CommandMatcher, SecurityPatterns | `zeph-tools` |
| `017-index/spec.md` | AST indexing, semantic retrieval, repo map | `zeph-index` |
| `018-scheduler/spec.md` | Cron scheduler, SQLite persistence; PERF-SC-04 FIXED; v0.18.4: **CLI subcommand** (`zeph schedule list/add/remove/show`) | `zeph-scheduler` |
| `019-gateway/spec.md` | HTTP webhook ingestion, bearer auth | `zeph-gateway` |
| `020-config-loading/spec.md` | Config resolution order, mode-agnostic defaults | `zeph-core` |
| `021-architecture-audit/spec.md` | Post-PR#1972 comprehensive audit: type safety, DRY, dead code, abstractions, channels | cross-cutting |
| `022-config-simplification/spec.md` | **Provider Registry Architecture**: canonical `[[llm.providers]]` format, `ProviderEntry` schema, routing strategies, **PILOT LinUCB bandit routing**; v0.18.1: **BaRP** cost-weight dial (`cost_weight` in `[llm.router.bandit]`), **MAR** memory-augmented routing (`memory_confidence_threshold`) | `zeph-config`, `zeph-core` |
| `023-complexity-triage-routing/spec.md` | Pre-inference complexity classification routing: ComplexityTier, TriageRouter, context escalation, metrics | `zeph-llm`, `zeph-config`, `zeph-core` |
| `024-multi-model-design/spec.md` | Multi-model design principle: complexity tiers, `*_provider` subsystem reference pattern, STT unification, known issues #2173/#2174/#2175 | cross-cutting |
| `025-classifiers/spec.md` | Candle-backed ML classifiers: injection detection (CandleClassifier), PII detection (CandlePiiClassifier), LlmClassifier for feedback, unified regex+NER sanitization pipeline | `zeph-classifiers` |
| `database-abstraction/spec.md` | **PostgreSQL backend (v0.18.0 Phase 1-3 implemented)**: `zeph-db` crate, `DatabaseDriver` trait, `Dialect` trait, `sql!()` macro, 52 PostgreSQL migrations, `MemoryConfig::database_url`, `zeph db migrate` CLI, `--init` backend selection, docker-compose env vars | `zeph-db`, cross-cutting |
| `026-tui-subagent-management/spec.md` | **Implemented (v0.18.0)**: Interactive TUI subagent sidebar (`a` key), j/k navigation, Enter loads JSONL transcript (last 200 entries), Esc returns, Tab cycling includes SubAgents | `zeph-tui` |
| `027-runtime-layer/spec.md` | **Implemented (v0.18.0); updated v0.18.1**: `RuntimeLayer` middleware — `before_chat`/`after_chat`/`before_tool`/`after_tool` hooks, `NoopLayer`, `LayerContext`; v0.18.1 adds `catch_unwind` guard for all hook invocations | `zeph-core` |
| `028-hooks/spec.md` | Reactive hooks: `cwd_changed` / `file_changed` events, `set_working_directory` tool, `FileChangeWatcher`, `ZEPH_*` env vars in hook shells | `zeph-core` |
| `029-feature-flags/spec.md` | Feature flag decision rules, surviving flag inventory (22 flags post-PR#2583), bundle definitions, NEVER section | `Cargo.toml`, cross-cutting |
| `030-tui-slash-autocomplete/spec.md` | Inline autocomplete dropdown in TUI Insert mode when user types `/`; reuses `filter_commands` registry, Tab/Enter accepts, Esc dismisses | `zeph-tui` |
| `handoff-skill-system/spec.md` | Skill-based YAML handoff protocol for inter-agent communication | `zeph-orchestration` |
| `subagent-context-propagation/report.md` | Gap analysis: `/agent spawn` context vs Claude Code reference — 12 gaps (P1–P4), phase-based fix plan; GAP-07 (cwd) and GAP-08b (loop exits on text-only) resolved in PR #2585 | `zeph-subagent`, `zeph-core` |
