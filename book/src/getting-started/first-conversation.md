# First Conversation

This guide takes you from a fresh install to your first productive interaction with Zeph in under 5 minutes.

## Prerequisites

- Zeph [installed](installation.md) and `zeph init` completed
- Either Ollama running locally (`ollama serve`), or a Claude/OpenAI/Gemini API key configured

## Start the Agent

```bash
zeph
```

You see a `You:` prompt. Type a message and press Enter.

For the TUI dashboard with side panels showing skills, memory, and metrics:

```bash
zeph --tui
```

## Ask About Files

```
You: What files are in the current directory?
```

Behind the scenes:

1. Zeph embeds your query and matches the `file-ops` skill by cosine similarity
2. The skill's instructions are injected into the prompt
3. The agent calls the `list_directory` or `find_path` tool
4. You get a structured answer with the directory listing

You did not tell Zeph which skill to use — it figured it out from context.

## Run a Command

```
You: Check disk usage on this machine
```

Zeph matches the `system-info` skill and runs `df -h` via the `bash` tool. Destructive commands (`rm`, `git push --force`, `drop table`) require confirmation:

```
Execute: rm -rf /tmp/old-cache? [y/N]
```

## See Memory in Action

```
You: What files did we just look at?
```

Zeph remembers the full conversation and answers from context without re-running any commands. With [semantic memory](../guides/semantic-memory.md) enabled, Zeph recalls relevant context from past sessions too.

## Project Instructions

Drop a `zeph.md` file in your project root to give Zeph standing context — coding conventions, domain knowledge, project rules. The content is injected into every prompt automatically.

```markdown
# Project Instructions

- Language: TypeScript, strict mode
- Test framework: vitest
- Commit messages follow Conventional Commits
- Never modify files under `generated/`
```

See [Instruction Files](../concepts/instruction-files.md) for provider-specific files and hot-reload behavior.

## Useful Slash Commands

| Command | Description |
|---------|-------------|
| `/skills` | Show active skills and usage statistics |
| `/mcp` | List connected MCP tool servers |
| `/new` | Start a fresh conversation without restarting |
| `/image <path>` | Attach an image for visual analysis |
| `/debug-dump` | Enable debug dump for the current session |

Type `exit`, `quit`, or press Ctrl-D to stop the agent.

## Next Steps

- [Configuration Wizard](wizard.md) — customize providers, memory, and channels
- [Configuration Recipes](../guides/config-recipes.md) — copy-paste configs for common setups
- [Skills](../concepts/skills.md) — how skill matching works
- [Tools](../concepts/tools.md) — shell, files, web, and MCP tools
