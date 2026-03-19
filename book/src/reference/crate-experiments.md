# zeph-experiments

Autonomous experiment engine for adaptive agent behavior testing and hyperparameter tuning.

Extracted from `zeph-core` in epic #1973 (Phase 1d). Gated behind the `experiments` feature flag.

## Purpose

`zeph-experiments` implements a closed-loop system that automatically tests agent behavior variations and selects configurations that maximize LLM-judged quality. It is used by the agent's self-improvement loop to discover better hyperparameters (temperature, context budget, skill prompt mode, etc.) without human intervention.

The engine operates on a **search space** of discrete and continuous parameter ranges. It explores the space using three strategies: grid search, random sampling, and neighborhood (hill-climbing). For each variation it runs a set of benchmark cases, scores them with an LLM judge, and persists the results.

## Key Types

| Type | Description |
|------|-------------|
| `ExperimentEngine` | Top-level orchestrator: runs a full experiment session, writes snapshots, returns a report |
| `ExperimentSessionReport` | Session summary: best variation found, score delta, number of cases run |
| `SearchSpace` | Defines the hyperparameter ranges to explore (`ParameterRange` per parameter) |
| `ParameterRange` | Single dimension: `Float(min, max, step)` or `Enum(Vec<String>)` |
| `VariationGenerator` | Trait implemented by `GridStep`, `Random`, `Neighborhood` — produces candidate variations |
| `GridStep` | Systematic grid traversal over the search space |
| `Random` | Random sampling using a `SmallRng` for reproducible runs |
| `Neighborhood` | Hill-climbing: perturb the current best by one step in each dimension |
| `Evaluator` | Runs benchmark cases against the agent using a variation's config, scores with `JudgeOutput` |
| `BenchmarkSet` | Collection of `BenchmarkCase` entries: prompt + expected behavior description |
| `BenchmarkCase` | Single test: input prompt and a human-readable quality criterion |
| `EvalReport` | Aggregated scores across all cases for a single variation |
| `CaseScore` | Per-case score (0.0–1.0) with judge rationale |
| `ConfigSnapshot` | Serializable snapshot of the current agent config used as the experiment baseline |
| `GenerationOverrides` | Delta overrides applied on top of `ConfigSnapshot` for a variation |
| `ExperimentResult` | Persisted result record: variation, score, timestamp, session ID |
| `EvalError` | Typed error enum for evaluation failures |

## Search Strategies

### Grid Search (`GridStep`)

Exhaustively iterates over the Cartesian product of all parameter ranges. Suitable for small search spaces (e.g., 3 temperature values × 2 skill modes = 6 candidates).

### Random Sampling (`Random`)

Samples parameter combinations uniformly at random. Efficient for large search spaces where exhaustive search is too slow.

### Neighborhood / Hill-Climbing (`Neighborhood`)

Starts from the current best variation and generates all single-parameter perturbations. Runs those candidates, adopts the best as the new starting point, and repeats. Converges quickly but may find local optima.

## Feature Flag

All modules in `zeph-experiments` are gated behind `#[cfg(feature = "experiments")]`. The crate compiles to an empty library when the feature is off.

To enable:

```toml
# root Cargo.toml (or workspace member)
[features]
experiments = ["zeph-experiments/experiments"]
```

Or build with the `full` or `experiments` feature:

```bash
cargo build --features experiments
```

## Integration with zeph-core

When the `experiments` feature is enabled, `zeph-core` constructs an `ExperimentEngine` from `ExperimentConfig` during `AppBuilder::build()`. The engine is scheduled via `zeph-scheduler` for periodic automated runs (when both `experiments` and `scheduler` features are active).

```toml
# config.toml
[experiments]
enabled = true
schedule = "0 3 * * *"   # Run at 03:00 every night
cases_per_run = 10
```

The agent exposes `/experiments` TUI commands to manually trigger runs and inspect results.

## Benchmark Dataset

`BenchmarkSet` is loaded from TOML files in the skills directory or defined inline in the config. Each case contains a prompt and a quality criterion string that the LLM judge uses to score the agent's response.

```toml
# Example benchmark case
[[experiments.cases]]
prompt = "Summarize the last three git commits in one sentence."
criterion = "The summary must mention commit count and be a single sentence."
```

## LLM-as-Judge

The `Evaluator` sends each (prompt, response) pair to an LLM along with the quality criterion and asks it to return a `JudgeOutput` with a score (0.0–1.0) and a brief rationale. The judge model is typically a small, fast model separate from the agent's main provider.

```rust
// JudgeOutput schema (simplified)
struct JudgeOutput {
    score: f64,       // 0.0 = fail, 1.0 = perfect
    rationale: String,
}
```

## Source Code

[`crates/zeph-experiments/`](https://github.com/bug-ops/zeph/tree/main/crates/zeph-experiments)

## See Also

- [Experiments concept guide](../concepts/experiments.md) — end-user documentation with config examples
- [Feature Flags](feature-flags.md) — the `experiments` and `scheduler` feature flags
