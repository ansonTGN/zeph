# zeph-subagent Crate

Subagent management for Zeph — spawning, grants, transcripts, and lifecycle hooks.

## Purpose

`zeph-subagent` manages autonomous agents spawned from within the main agent. Each subagent has scoped tools, skills, memory, and zero-trust secret delegation. Subagents can operate in the background, produce persistent transcripts, and are managed via TOML definitions or interactive CLI.

## Key Types

- **SubAgentManager** — Manages subagent lifecycle (spawn, pause, resume, stop)
- **SubAgentDef** — YAML/TOML definition of a subagent (tools, skills, grants, memory scope)
- **SubAgentHandle** — Reference to a running subagent with state, stdin/stdout
- **SubAgentGrant** — Fine-grained permission (tool name, input filter, memory scope)
- **SubAgentCommand** — Control commands (pause, resume, cancel, get transcript)

## Features

- **Scoped execution** — Subagents use allowlist of tools/skills, not full access
- **Memory isolation** — User/project/local memory scopes for persistent state
- **Transcript persistence** — Conversation history stored in JSONL for audit and replay
- **Grants system** — Fine-grained permission model with deny/allow lists
- **Lifecycle hooks** — PreToolUse / PostToolUse for monitoring/filtering
- **Fire-and-forget** — Background execution with max_turns limit
- **Session resume** — `/agent resume` to continue completed sessions
- **Interactive UI** — TUI agents panel for real-time management

## Usage

### Define a subagent (YAML)

```yaml
# .zeph/agents/researcher.yaml
name: researcher
tools:
  - web_search
  - file_read
memory: project
max_turns: 20
background: false
permission_mode: accept_edits

tools_except:
  - write_file  # researcher can't write files
```

### Spawn from Markdown

```markdown
# Sub-agent: Code Reviewer

Specialized code reviewer agent with denied write access.

**Definition:**
- **tools**: code_search, read_file, git_show
- **deny**: write_file, shell
- **memory**: project
```

### Manage via CLI

```bash
zeph agents list                    # list all subagents
zeph agents show researcher         # show definition
zeph agents create my-agent.yaml    # create new subagent
zeph agents delete researcher       # delete subagent
```

## Feature Flags

- **None** — subagent is unconditional (always enabled)

## Dependencies

- `zeph-config` — SubAgentConfig for configuration
- `zeph-memory` — SemanticMemory for transcript and memory scope storage
- `zeph-tools` — ToolExecutor for executing subagent tools
- `zeph-skills` — SkillRegistry for subagent skill access
- `zeph-common` — Shared utilities

## Integration with zeph-core

Re-exported via `zeph-core` as `crate::subagent::*`:

```rust
use zeph_core::subagent::{SubAgentManager, SubAgentDef, SubAgentHandle};
```

All public types are available via the re-export shim in `zeph-core/src/lib.rs`.

## Configuration

In `config.toml`:

```toml
[agent.subagents]
enabled = true
default_permission_mode = "accept_edits"

[[agent.subagents.hooks]]
event = "PreToolUse"
# trigger custom logic before tool execution
```

## CLI Commands

- `zeph agents list` — List all defined subagents
- `zeph agents show <name>` — Show subagent definition
- `zeph agents create <path>` — Create new subagent from YAML/Markdown
- `zeph agents edit <name>` — Edit subagent definition interactively
- `zeph agents delete <name>` — Delete a subagent definition
- `/agent resume <id>` — Resume a completed subagent session (TUI)

## Documentation

Full API documentation: [docs.rs/zeph-subagent](https://docs.rs/zeph-subagent/)

mdBook reference: [Sub-agents](https://bug-ops.github.io/zeph/advanced/sub-agents.html)

## License

MIT
