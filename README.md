# PACT Framework for Claude Code

> **Principled AI-assisted Coding through Teamwork** — Transform Claude Code into a coordinated team of specialist developers using the Prepare → Architect → Code → Test methodology.

## What is PACT?

PACT turns a single AI assistant into **7 specialist agents** that work together systematically:

| Agent | Role |
|-------|------|
| **Preparer** | Research, gather requirements, read docs |
| **Architect** | Design systems, create blueprints |
| **Backend Coder** | Implement server-side logic |
| **Frontend Coder** | Build user interfaces |
| **Database Engineer** | Design schemas, optimize queries |
| **n8n Specialist** | Build workflow automations |
| **Test Engineer** | Write comprehensive tests |

Instead of "vibe coding" (letting AI guess), PACT ensures **preparation before coding**, **architecture before implementation**, and **testing as integral**.

---

## Installation

### Option A: Install as Plugin (Recommended)

Install PACT as a plugin to use across all your projects:

```bash
# Add the marketplace from GitHub
/plugin marketplace add ProfSynapse/PACT-prompt

# Install the plugin
/plugin install PACT@pact-marketplace
```

**Set up the Orchestrator:**

```bash
# Copy the CLAUDE.md file to your global config
cp ~/.claude/plugins/cache/pact-marketplace/PACT/*/CLAUDE.md ~/.claude/CLAUDE.md
```

If you already have a `~/.claude/CLAUDE.md`, back it up first and either replace it or prepend the PACT content.

Enable auto-updates via `/plugin` → **Marketplaces** → select marketplace → **Enable auto-update**

**What you get:**
- PACT agents, commands, and skills available in all projects
- Automatic symlink setup for protocol references
- Plugin updates via marketplace

### Option B: Clone for Development

If you want to contribute or customize PACT:

```bash
# Clone the repository
git clone https://github.com/ProfSynapse/PACT-prompt.git
cd PACT-prompt

# Start Claude Code
claude
```

The `pact-plugin/` directory contains the full framework source for local development.

### ⚠️ Important: Restart Required

After installing PACT, **restart Claude Code** for changes to take effect:

1. **Close** your current Claude Code session (type `exit` or close the terminal)
2. **Reopen** Claude Code with `claude`

This ensures all agents, hooks, and skills are loaded properly.

---

## Quick Start

Once installed, start Claude Code in your project:

```bash
claude
```

Then use natural language or commands:

```
# Natural language
"I want to build a REST API for user management. Start the PACT process."

# Or use commands directly
/PACT:orchestrate Build user authentication with JWT
/PACT:comPACT backend Fix the null pointer in auth middleware
/PACT:plan-mode Design a caching strategy for our API
```

---

## Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/PACT:orchestrate` | Full multi-agent workflow | New features, complex tasks |
| `/PACT:comPACT` | Single specialist, light process | Quick fixes, focused tasks |
| `/PACT:plan-mode` | Planning consultation (no code) | Before complex implementations |
| `/PACT:rePACT` | Nested PACT cycle for sub-tasks | Complex sub-problems during CODE |
| `/PACT:imPACT` | Triage when blocked | Hit a blocker, need help deciding |
| `/PACT:peer-review` | Commit, PR, multi-agent review | Ready to merge |
| `/PACT:pin-memory` | Pin critical context permanently | Gotchas, key decisions to preserve |
| `/PACT:wrap-up` | End-of-session cleanup | Ending a work session |

### comPACT Examples

```bash
/PACT:comPACT backend Fix the authentication bug
/PACT:comPACT frontend Add loading spinner to submit button
/PACT:comPACT database Add index to users.email column
/PACT:comPACT test Add unit tests for payment module
/PACT:comPACT architect Should we use microservices here?
/PACT:comPACT prepare Research OAuth2 best practices
```

---

## Skills (13 Domain Knowledge Modules)

Skills provide specialized knowledge that loads on-demand:

### PACT Phase Skills
| Skill | Triggers On |
|-------|-------------|
| `pact-prepare-research` | Research, requirements, API exploration |
| `pact-architecture-patterns` | System design, C4 diagrams, patterns |
| `pact-coding-standards` | Clean code, error handling, conventions |
| `pact-testing-strategies` | Test pyramid, coverage, mocking |
| `pact-security-patterns` | Auth, OWASP, credential handling |

### n8n Workflow Skills
| Skill | Triggers On |
|-------|-------------|
| `n8n-workflow-patterns` | Workflow architecture, webhooks |
| `n8n-node-configuration` | Node setup, field dependencies |
| `n8n-expression-syntax` | Expressions, `$json`, `$node` |
| `n8n-code-javascript` | JavaScript in Code nodes |
| `n8n-code-python` | Python in Code nodes |
| `n8n-validation-expert` | Validation errors, debugging |
| `n8n-mcp-tools-expert` | MCP tool usage |

### Context Management Skills
| Skill | Triggers On |
|-------|-------------|
| `pact-memory` | Save/search memories, lessons learned |

---

## Memory System (New!)

PACT includes a persistent memory system for cross-session learning:

```python
# Save context, decisions, lessons learned
memory.save({
    "context": "Building authentication system",
    "goal": "Add JWT refresh tokens",
    "lessons_learned": ["Always hash passwords with bcrypt"],
    "decisions": [{"decision": "Use Redis", "rationale": "Fast TTL"}],
    "entities": [{"name": "AuthService", "type": "component"}]
})

# Semantic search across all memories
memory.search("rate limiting")
```

**Features:**
- Local SQLite database with vector embeddings
- Graph network linking memories to files
- Semantic search across sessions
- Auto-prompts to save after significant work

**Storage:** `~/.claude/pact-memory/` (persists across projects)

---

## Project Structure

### Plugin Installation (Recommended)

When installed as a plugin, PACT lives in your plugin cache:

```
~/.claude/
├── CLAUDE.md                   # Orchestrator (copy from plugin)
├── plugins/
│   └── cache/
│       └── pact-marketplace/
│           └── PACT/
│               └── 2.0.0/      # Plugin version
│                   ├── agents/
│                   ├── commands/
│                   ├── skills/
│                   ├── hooks/
│                   └── protocols/
├── protocols/
│   └── pact-plugin/            # Symlink to plugin protocols
└── pact-memory/                # Memory database (shared)
    ├── memory.db
    └── models/
        └── all-MiniLM-L6-v2.gguf
```

### Your Project

```
your-project/
├── CLAUDE.md                   # Project-specific config (optional)
└── docs/
    ├── plans/                  # Implementation plans
    ├── architecture/           # Design documents
    ├── decision-logs/          # Implementation decisions
    └── preparation/            # Research outputs
```

### Development Clone

If you cloned this repo for development/contribution:

```
PACT-prompt/
├── pact-plugin/                # Plugin source (canonical)
│   ├── agents/                 # 7 specialist agents
│   ├── commands/               # 8 PACT workflow commands
│   ├── skills/                 # 13 domain knowledge skills
│   ├── hooks/                  # Automation hooks
│   └── protocols/              # Coordination protocols
├── CLAUDE.md                   # Orchestrator configuration
└── docs/
```

---

## How It Works

### The PACT Cycle

```
┌─────────────────────────────────────────────────────────────┐
│                    /PACT:orchestrate                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   PREPARE ──► ARCHITECT ──► CODE ──► TEST                   │
│      │            │           │         │                   │
│      ▼            ▼           ▼         ▼                   │
│   Research    Design      Implement   Verify                │
│   Docs        Blueprint   Backend     Unit tests            │
│   APIs        Contracts   Frontend    Integration           │
│   Context     Schema      Database    E2E tests             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### VSM-Enhanced Orchestration

PACT uses the **Viable System Model** for intelligent coordination:

- **Variety Management**: Simple tasks get light process; complex tasks get full ceremony
- **Adaptive Workflow**: Orchestrator selects the right level of rigor
- **Viability Sensing**: Agents emit emergency signals (HALT/ALERT) for critical issues
- **Continuous Audit**: Quality feedback during implementation, not just at the end

### Hooks (Automation)

| Hook | Trigger | Purpose |
|------|---------|---------|
| `session_init.py` | Session start | Load active plans, check memory |
| `phase_completion.py` | Agent completes | Remind about decision logs |
| `validate_handoff.py` | Agent handoff | Verify output quality |
| `track_files.py` | File edit/write | Track files for memory graph |
| `memory_prompt.py` | Session end | Prompt to save learnings |

---

## Configuration

### CLAUDE.md

The `CLAUDE.md` file configures the orchestrator. Key sections:

```markdown
# MISSION
Act as PACT Orchestrator...

## S5 POLICY (Non-Negotiables)
- Security: Never expose credentials
- Quality: Tests must pass before merge
- Ethics: No deceptive content
- Delegation: Always delegate to specialists

## PACT AGENT ORCHESTRATION
- When to use each command
- How to delegate effectively
```

### Customization

1. **Add project-specific context** to your project's `CLAUDE.md`
2. **Create project-local skills** in your project's `.claude/skills/` (Claude Code feature)
3. **Create global skills** in `~/.claude/skills/` for use across all projects
4. **Fork the plugin** if you need to modify agents or hooks for your domain

---

## Requirements

- **Claude Code** (the CLI tool): `npm install -g @anthropic-ai/claude-code`
- **Python 3.9+** (for memory system and hooks)
- **macOS or Linux** (Windows support coming soon)

### Optional Dependencies

```bash
# For memory system with embeddings
pip install sqlite-vec

# For n8n workflows
# Requires n8n-mcp MCP server
```

---

## Examples

### Start a New Feature

```
User: I need user authentication with JWT tokens

Claude: I'll use /PACT:orchestrate to coordinate this...

[PREPARE] Researching JWT best practices, library options...
[ARCHITECT] Designing auth flow, token structure, middleware...
[CODE] Backend coder implementing AuthService, middleware...
[TEST] Test engineer verifying login, refresh, edge cases...
```

### Quick Fix

```
User: /PACT:comPACT backend Fix the null check in validateToken

Claude: Invoking backend specialist for focused fix...
[Backend Coder] Fixed null check, added test, verified build passes.
```

### Planning Before Building

```
User: /PACT:plan-mode Design a caching strategy for our API

Claude: [S4 Intelligence Mode] Consulting specialists...
[Preparer] Researching Redis vs Memcached vs in-memory...
[Architect] Designing cache invalidation strategy...
[Database] Considering query patterns for cache keys...

Plan saved to docs/plans/api-caching-plan.md
```

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following PACT principles
4. Run `/PACT:peer-review` for multi-agent code review
5. Submit PR

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Links

- [Claude Code Documentation](https://code.claude.com/docs)
- [Report Issues](https://github.com/ProfSynapse/PACT-prompt/issues)
- [VSM Background](https://en.wikipedia.org/wiki/Viable_system_model)
