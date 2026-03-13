---
created_at: "2026-03-12T04:00:00+00:00"
updated_at: "2026-03-12T04:00:00+00:00"
summary: A practical guide to Claude Code — covering modes, slash commands, CLAUDE.md, MCP, skills, memory, and more.
tags: Claude Code, AI Tools, Productivity, Developer Tools
title: Claude Code Essentials — What You Need to Know
---

# Claude Code Essentials — What You Need to Know

Claude Code is Anthropic's official CLI and IDE integration for working with Claude on real software projects. It goes far beyond a chat interface — it can read, write, and run code, manage files, call tools, and remember context across sessions. This article covers the core concepts you'll use every day.

---

## The Three Edit Modes

One of the first things to configure is how aggressively Claude acts on your codebase. There are three modes:

### Auto-edit (Edit Automatically)
Claude reads files, makes changes, and runs commands without asking for approval each time. This is the fastest workflow — great once you trust the task scope. You can still review every change via git diff after the fact.

### Ask Before Edits
Claude plans what it wants to do, then asks for confirmation before writing to files or running shell commands. A good middle ground for larger refactors where you want veto power on each step.

### Plan Mode
Claude *only* thinks and plans — it cannot take any actions. It will explore the codebase, reason about the problem, and produce a written plan for you to review and approve before any code is touched. Use this for risky or complex changes where you want full alignment before anything moves.

You can switch between modes at any time during a session.

### How to switch between modes

**In the CLI:** The current mode is shown at the bottom of the Claude Code interface. Click on it to open the mode selector, or press **Shift+Tab** to cycle through modes without leaving the keyboard.

**In VS Code:** Use the mode dropdown in the Claude Code panel sidebar — it appears as a selector above the chat input.

You can switch at any point mid-session — you don't need to restart.

### How to use these modes together

A reliable workflow for non-trivial tasks:

**1. Start in Plan Mode to align on the approach**

Before any code is touched, use Plan Mode to have Claude explore the codebase, surface design questions, and propose an approach. This is your chance to catch misunderstandings early — ask questions, push back on the plan, and iterate until you're satisfied. Claude will write out its plan in the chat (you can also ask it to save the plan to a file for reference).

**2. Approve the plan, then switch to auto-edit**

Once you're happy with the direction, switch to Auto-edit and let Claude execute. Because the design questions are already resolved, Claude can work quickly without needing to stop and ask.

**3. Use Ask Before Edits for extra caution**

If you're working in a sensitive area — production config, database migrations, shared infrastructure — switch to Ask Before Edits instead. Claude will pause before each file write or command, giving you a chance to review each action individually.

A useful rule: the higher the blast radius of a mistake, the more conservatively you should configure the mode. Start in Plan Mode, finish in Auto-edit, and use Ask Before Edits when you need fine-grained control in between.

---

## Popular Slash Commands

Slash commands are shortcuts you type directly in the Claude Code prompt. Here are the most useful ones:

| Command | What it does |
|---|---|
| `/help` | Show all available commands and keyboard shortcuts |
| `/clear` | Clear the current conversation context (start fresh) |
| `/compact` | Summarize the conversation to reclaim context window space |
| `/review` | Ask Claude to do a code review of recent changes |
| `/commit` | Generate a git commit message and commit staged changes |
| `/memory` | Open the memory file for the current project |
| `/init` | Initialize Claude Code in a new project (creates `CLAUDE.md`) |
| `/doctor` | Check your Claude Code installation for issues |
| `/fast` | Toggle fast mode (optimized for speed) |

---

## CLAUDE.md — Your Persistent Instructions

`CLAUDE.md` is a Markdown file that Claude reads at the start of every session. It's how you give Claude standing instructions that persist across conversations, without having to re-explain things each time.

**Two levels:**

- `~/.claude/CLAUDE.md` — global, applies to every project on your machine
- `<project-root>/CLAUDE.md` — project-specific, checked into git so your whole team shares it

**What to put in CLAUDE.md:**

- Preferred languages, frameworks, and libraries
- Code style rules (f-strings, early returns, no clever one-liners, etc.)
- How to run the app and tests
- Architecture notes that aren't obvious from the code
- Things Claude should never do (e.g. "don't mock the database in tests")

The more specific your `CLAUDE.md`, the less you need to repeat yourself. Think of it as an onboarding doc written for Claude.

### Which CLAUDE.md files get read — and where should you launch?

Claude Code reads CLAUDE.md files in this order:

1. `~/.claude/CLAUDE.md` — always read, regardless of where you launch
2. The directory where you run `claude` (your project root)
3. All **parent directories** up the tree — it walks upward and reads any CLAUDE.md it finds
4. **Subdirectories** it explores during the session

So launching from `~/projects/myapp/` would load:

- `~/.claude/CLAUDE.md`
- `~/projects/myapp/CLAUDE.md`
- `~/projects/CLAUDE.md` (if it exists)
- `~/CLAUDE.md` (if it exists)

**Always launch Claude from your project root, not your home folder.** Starting from `~` gives Claude your entire home directory as context and may cause it to wander into unrelated projects. Starting from the project root scopes git context, file searches, and tool calls to just that project.

```bash
cd ~/my-project
claude
```

---

## Skills

Skills extend what Claude can do. Each skill is a `SKILL.md` file with instructions — Claude follows them when the skill is invoked, either automatically when relevant or manually via `/skill-name`.

> Skills replaced the older `.claude/commands/` system. Existing command files still work, but skills are recommended — they support supporting files, subagent execution, and finer invocation control.

### Bundled skills

These ship with Claude Code and are available in every session:

| Command | What it does |
|---|---|
| `/simplify` | Reviews recently changed files for code reuse, quality, and efficiency issues, then fixes them. Spawns three parallel review agents. |
| `/batch <instruction>` | Decomposes large-scale changes into independent units, runs one background agent per unit in an isolated git worktree, then opens PRs. Useful for mass migrations. |
| `/debug [description]` | Troubleshoots your current Claude Code session by reading the session debug log. |
| `/loop [interval] <prompt>` | Runs a prompt repeatedly on an interval while the session stays open. E.g. `/loop 5m check if the deploy finished`. |
| `/claude-api` | Loads Claude API and Agent SDK reference material into context. Also activates automatically when your code imports `anthropic`. |

### Creating your own skill

Skills live in a directory named after the skill, with `SKILL.md` as the entrypoint:

```
~/.claude/skills/my-skill/
└── SKILL.md
```

A minimal `SKILL.md`:

```yaml
---
name: explain-code
description: Explains code with visual diagrams and analogies. Use when explaining how code works or when the user asks "how does this work?"
---

When explaining code, always include:

1. **Start with an analogy**: Compare the code to something from everyday life
2. **Draw a diagram**: Use ASCII art to show flow or structure
3. **Walk through the code**: Explain step-by-step what happens
```

The `description` field is the most important part — Claude uses it to decide when to load the skill automatically. Make it specific and include phrases users would naturally say.

### Where skills live

| Location | Path | Scope |
|---|---|---|
| Personal | `~/.claude/skills/<name>/SKILL.md` | All your projects |
| Project | `.claude/skills/<name>/SKILL.md` | This project only |
| Enterprise | Managed settings | All org users |

When names conflict, personal takes precedence over project.

### Invoking skills

- **Automatically**: Claude reads all skill descriptions at startup and decides when to apply them based on what you're asking.
- **Manually**: Type `/skill-name` to invoke directly, with optional arguments: `/fix-issue 42`.

### Key frontmatter options

```yaml
---
name: deploy
description: Deploy the application to production
disable-model-invocation: true   # Only YOU can trigger this, not Claude
context: fork                    # Run in an isolated subagent context
allowed-tools: Bash(git *)       # Tools Claude can use without asking
---
```

| Field | What it controls |
|---|---|
| `disable-model-invocation: true` | Prevents Claude from auto-triggering the skill. Use for side-effect actions like deploy, commit, or send-message. |
| `user-invocable: false` | Hides the skill from the `/` menu. Use for background knowledge Claude should apply silently. |
| `context: fork` | Runs the skill in an isolated subagent — no access to conversation history. Good for research or one-shot tasks. |
| `allowed-tools` | Tools the skill can use without per-call permission prompts. |
| `argument-hint` | Hint shown in autocomplete, e.g. `[issue-number]`. |

### Passing arguments

Use `$ARGUMENTS` in skill content — it's replaced with whatever follows the skill name when invoked:

```yaml
---
name: fix-issue
description: Fix a GitHub issue by number
disable-model-invocation: true
---

Fix GitHub issue $ARGUMENTS following our coding standards.
Read the issue, implement the fix, write tests, and commit.
```

Running `/fix-issue 123` sends Claude "Fix GitHub issue 123 following our coding standards..."

For positional arguments, use `$0`, `$1`, `$2`:

```yaml
Migrate the $0 component from $1 to $2.
```

`/migrate-component SearchBar React Vue` → Claude sees `Migrate the SearchBar component from React to Vue.`

### Supporting files

Skills can include additional files alongside `SKILL.md` — templates, examples, scripts:

```
my-skill/
├── SKILL.md
├── examples.md
└── scripts/
    └── validate.sh
```

Reference them from `SKILL.md` so Claude knows when to load them. Keep `SKILL.md` under 500 lines and move detailed reference material into separate files.

For example:

```markdown
## Additional resources

- For usage examples, see [examples.md](examples.md)

Run `scripts/validate.sh` after making changes.
```

Claude won't load `examples.md` on every invocation — it reads the reference in `SKILL.md` and decides whether to fetch it based on what the task requires.

### Popular skills and how to install them

Skills are distributed as **plugins** through marketplaces. The official Anthropic marketplace is available by default — browse it by running `/plugin` and opening the **Discover** tab.

Some commonly used plugins from the official marketplace:

| Plugin | What it adds |
|---|---|
| `commit-commands` | Git commit, push, and PR creation workflows |
| `pr-review-toolkit` | Specialized agents for reviewing pull requests |
| `github` / `gitlab` | MCP-backed access to issues, PRs, and repos |
| `linear` / `atlassian` | Connect Claude to your project management tools |
| `pyright-lsp` / `typescript-lsp` | Real-time type errors and code navigation for Python / TypeScript |
| `agent-sdk-dev` | Reference material for building with the Claude Agent SDK |

**Installing a plugin:**

```shell
/plugin install commit-commands@claude-plugins-official
```

Or use the interactive UI: run `/plugin`, go to **Discover**, select a plugin, and choose an installation scope:

- **User** — available across all your projects (default)
- **Project** — shared with your whole team via `.claude/settings.json`
- **Local** — just this project, not committed

After installing, run `/reload-plugins` to activate without restarting. Plugin skills are namespaced, so `commit-commands` shows up as `/commit-commands:commit`.

**Adding third-party marketplaces:**

The demo marketplace from Anthropic's GitHub has additional example plugins:

```shell
/plugin marketplace add anthropics/claude-code
```

Any GitHub repo, Git URL, or local path can be a marketplace — useful for sharing team-specific skills across projects.

> Only install plugins from sources you trust. Plugins can execute arbitrary code on your machine.

---

## MCP — Model Context Protocol

MCP (Model Context Protocol) is an open standard that lets Claude connect to external tools and data sources. Instead of copy-pasting content into the chat, MCP gives Claude direct, structured access.

**What MCP can connect Claude to:**

- **Databases** — query Postgres, SQLite, or other databases directly
- **APIs** — GitHub, Linear, Jira, Slack, and more
- **File systems** — read files outside the current project directory
- **Custom tools** — anything you build and expose as an MCP server

MCP servers are configured in `.mcp.json` at the project or user level. Each server runs as a local process and exposes a set of named tools Claude can call.

**Example use cases:**

- Ask Claude to look up a GitHub issue and fix the bug it describes
- Have Claude query your database and write a migration based on the current schema
- Let Claude read your Linear tickets and prioritize which to tackle next

### Simple example: connecting Claude to GitHub

Add this to your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-token-here"
      }
    }
  }
}
```

Once configured, you can ask Claude things like:

> "Look at issue #42 in this repo and fix the bug it describes."

Claude will call the GitHub MCP server directly to fetch the issue, read the relevant code, and make the fix — no copy-pasting required.

### How MCP actually works

MCP servers are separate programs that need to be installed once, then configured in `.mcp.json`. When you start a Claude Code session, Claude automatically launches all configured MCP servers in the background — you never start them manually.

From there, just ask naturally:

> "How many users signed up last week?"

Claude decides when to call the MCP server and does it invisibly. You don't need to tell it to "use MCP" — it figures that out from context.

**Do you need to mention MCP in `CLAUDE.md` or `SKILL.md`?** Only if you want to guide specific behavior — for example, "always query the `analytics` database for user metrics, never estimate." For basic use, no extra config is needed.

---


## Memory — Remembering Across Sessions

Claude Code has a file-based memory system stored in `~/.claude/projects/<project>/memory/`. This is separate from `CLAUDE.md` — it's for things Claude *learns* during conversations that should persist.

**Types of memory:**

- **User** — your role, expertise, preferences (e.g. "senior Go engineer, new to React")
- **Feedback** — corrections and rules Claude should apply going forward (e.g. "don't use mocks in tests")
- **Project** — ongoing work, decisions, deadlines (e.g. "merge freeze starts Thursday")
- **Reference** — where to find things in external systems (e.g. "bugs tracked in Linear project INGEST")

### Do you need to maintain it?

Mostly no — Claude writes memories automatically during conversations when it learns something worth keeping. Zero maintenance required to get value from it.

- **Auto-written**: Claude decides on its own when something is worth saving — e.g. if you say "always use f-strings", it saves that without you asking
- **Manually triggered**: Say "remember that..." to force a save on something specific
- **You can read/edit/delete**: Memory files are plain Markdown, so you can open them anytime and clean up outdated or wrong entries
- **It can go stale**: Claude won't automatically remove old memories. If a project decision changes, the old memory stays until you update it

> Occasional review is good hygiene on long-lived projects, but you don't need to actively manage it day-to-day.

---

## Hooks — Automating Responses to Events

Hooks are shell commands that Claude Code runs automatically when certain events happen. They're configured in `settings.json` and run locally on your machine.

**Common hook triggers:**

- `pre-tool-call` — before Claude calls a tool (useful for logging or approval gates)
- `post-tool-call` — after a tool completes (useful for auto-formatting or running linters)
- `on-submit` — when you submit a prompt

Hooks let you enforce team rules automatically — for example, running `black` after every file write, or blocking certain shell commands entirely.

### Example: auto-format Python files after every edit

```json
{
  "hooks": {
    "post-tool-call": [
      {
        "matcher": "Edit|Write",
        "command": "black $CLAUDE_TOOL_RESULT_PATH 2>/dev/null || true"
      }
    ]
  }
}
```

Add this to `~/.claude/settings.json`. After every file edit, Claude will automatically run `black` to format the file — no need to remember to do it manually.

---

## Permissions & Safety

Claude Code operates in a sandboxed permission model. You control what it can do via `~/.claude/settings.json` (global) or `.claude/settings.json` (project-level).

The `permissions` key has two lists:

```json
{
  "permissions": {
    "allow": [
      "Bash(git log:*)",
      "Bash(npm run test:*)"
    ],
    "deny": [
      "Bash(rm:*)",
      "Bash(git push --force:*)"
    ]
  }
}
```

- **`allow`** — commands Claude can run without asking for your approval each time
- **`deny`** — commands Claude will never run, regardless of what you ask

### What the patterns look like

| Pattern | What it allows/blocks |
|---|---|
| `Bash(git log:*)` | Any `git log` command |
| `Bash(npm run test:*)` | Any `npm run test` variant |
| `Bash(rm:*)` | Any `rm` command |
| `Read` | All file reads |
| `Edit` | All file edits |
| `mcp__github__*` | All tools from the GitHub MCP server |

### Two levels of settings

- `~/.claude/settings.json` — global, applies to all projects on your machine
- `<project-root>/.claude/settings.json` — project-specific, can be checked into git

Project-level settings take precedence over global ones.

For destructive or hard-to-reverse actions (force-push, dropping tables, deleting branches), Claude will ask for explicit confirmation even in auto-edit mode — regardless of your allow list. This is intentional.

---

## Keyboard Shortcuts

A few that save time in the CLI:

| Shortcut | Action |
|---|---|
| `Escape` | Cancel current generation |
| `Ctrl+C` | Hard stop (exits Claude) |
| `Up arrow` | Recall previous prompt |
| `Ctrl+L` | Clear screen |
| `Shift+Enter` | Newline in prompt (without submitting) |

---

## Tips for Getting the Most Out of Claude Code

**Be specific about scope.** "Fix the bug in checkout" is harder to act on than "the `calculate_total()` function in `cart.py` returns the wrong value when discount codes are applied."

**Use Plan Mode for big changes.** Before touching anything significant — a refactor, a new feature, a migration — switch to Plan Mode first. Let Claude map out the approach, then approve before it touches code.

**Keep CLAUDE.md updated.** Every time you correct Claude on something, consider whether that correction should live in `CLAUDE.md` so you never have to say it again.

**Review diffs, not individual edits.** Claude can make many file changes in one go. Use `git diff` to review the full change set rather than watching each edit happen line by line.

**Ask Claude to explain before changing.** If you're unsure about a piece of code, ask Claude to explain it *before* asking it to modify it. This builds shared understanding and catches misassumptions early.
