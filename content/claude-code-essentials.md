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

Skills are **model-invoked** capabilities — Claude decides when to use them based on context, rather than you calling them explicitly. They're defined with a `SKILL.md` file and bundled inside a **plugin**.

### Installing plugins

Plugins are installed via the CLI:

```bash
claude plugins install <plugin-name>
```

Installed plugins are available globally across all your projects. Some plugins are scoped to a specific project when installed from within that project's directory. You can browse available plugins from the official marketplace or install from a local path.

### Where do SKILL.md files live?

Skills are not per-project. They live inside a plugin directory, which is installed globally (or scoped to a specific project). The structure looks like this:

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json       # Plugin metadata
├── commands/
│   └── my-command.md     # A slash command (user-invoked)
└── skills/
    ├── skill-one/
    │   └── SKILL.md      # One skill
    └── skill-two/
        └── SKILL.md      # Another skill
```

Yes — a single plugin can contain **multiple skills**, each in its own subdirectory under `skills/`.

### How does Claude know when to use a skill?

The `description` field in the skill's frontmatter acts as the trigger. You write it as a natural-language condition:

```yaml
---
name: python-style
description: This skill should be used when the user asks to write or review Python code, or mentions PEP8, type hints, or code style.
version: 1.0.0
---
```

Claude reads all installed skill descriptions and automatically applies the relevant ones based on what you're asking. You never invoke a skill with a slash command — it just activates silently in the background.

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

## Custom Commands

Custom commands are personal slash commands you define as Markdown files in `~/.claude/commands/`. Each file becomes a `/command-name` you can invoke directly in the prompt.

When you type `/commit`, Claude loads `~/.claude/commands/commit.md` and executes the prompt inside it. Great for repetitive tasks:

- `/commit` — generate a conventional commit message
- `/review` — run a structured code review checklist
- `/deploy` — walk through your deployment steps
- `/standup` — summarize recent git activity into a standup update

Commands can include frontmatter to restrict which tools Claude is allowed to use, and can embed live shell output with `!` backtick syntax (e.g. `` !`git status` `` injects the current git status into the prompt at run time).

### Example: `standup.md`

Here's what `~/.claude/commands/standup.md` might look like:

```markdown
---
description: Summarize recent git activity as a standup update
allowed-tools: Bash(git log:*), Bash(git diff:*)
---

## Context

- Recent commits by me: !`git log --oneline --author="$(git config user.name)" --since="yesterday"`
- Current branch: !`git branch --show-current`
- Files changed: !`git diff --stat HEAD~5`

## Your task

Based on the git activity above, write a short standup update in this format:

**Yesterday:** What I worked on (based on commits)
**Today:** What I plan to continue or finish next
**Blockers:** None (unless you see signs of something unresolved)

Keep it concise — 3 bullet points max per section. Write in first person.
```

When you type `/standup`, Claude runs the embedded `git log` and `git diff` commands live, then uses the real output to write your standup. No manual copy-pasting.

### Skills vs. Commands — quick comparison

| | Commands | Skills |
|---|---|---|
| Invoked by | You (`/command-name`) | Claude (automatically) |
| File | `commands/my-command.md` | `skills/my-skill/SKILL.md` |
| Lives in | Plugin or `~/.claude/commands/` | Plugin only |
| Use for | Repetitive tasks you trigger | Domain knowledge Claude applies silently |

**Choose a command when:**

- You consciously trigger the workflow (e.g. "generate my commit message now")
- The task is tied to a specific moment — before a commit, before a deploy, at standup time
- You want to control exactly when it runs

**Choose a skill when:**

- You want Claude to apply it automatically, every time, without asking
- It's domain knowledge or a coding standard (e.g. "always use FastAPI patterns when writing Python APIs")
- Forgetting to invoke it would quietly hurt quality

> Rule of thumb: if you'd have to remember to ask for it, make it a command. If you'd want it silently enforced every time, make it a skill.

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
