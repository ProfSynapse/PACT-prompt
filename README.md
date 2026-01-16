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

Choose the approach that fits your workflow:

### Option A: Fork as Project Starter (Recommended for New Projects)

Use PACT as the foundation for a new project:

```bash
# Clone and rename to your project
git clone https://github.com/ProfSynapse/PACT-prompt.git my-project
cd my-project

# Optional: Start fresh git history
rm -rf .git
git init
git add .
git commit -m "Initial commit with PACT Framework"

# Start Claude Code
claude
```

**What you get:**
- Full PACT framework in your project
- `.claude/` folder with all agents, commands, skills
- `CLAUDE.md` configured as the orchestrator
- Ready to customize for your needs

### Option B: Ask Claude to Install It (Easiest)

Let Claude set up PACT for you in any new project:

1. **Create a new project folder** in your IDE (VS Code, Cursor, etc.)
2. **Open the terminal** in that folder
3. **Run `claude`** to start Claude Code
4. **Paste this prompt:**

```
Install the PACT framework from https://github.com/ProfSynapse/PACT-prompt

Clone it, copy the .claude folder and CLAUDE.md to this project,
initialize git, and set up the docs folder structure.
```

That's it! Claude handles the rest.

### Option C: Install as Plugin (For Existing Projects)

Add PACT capabilities to an existing project:

```bash
# Navigate to your existing project
cd your-existing-project

# Install PACT as a plugin (when available on plugin store)
claude plugins install PACT

# Or manually: clone and link
git clone https://github.com/ProfSynapse/PACT-prompt.git ~/.claude/plugins/PACT
```

**What you get:**
- PACT agents and commands available in any project
- Skills loaded on-demand
- Your existing project structure unchanged

### Option D: Manual Setup

Copy the essentials into any project:

```bash
# Copy the .claude folder to your project
cp -r /path/to/PACT-prompt/.claude /path/to/your-project/

# Copy CLAUDE.md (the orchestrator)
cp /path/to/PACT-prompt/CLAUDE.md /path/to/your-project/
```

### ⚠️ Important: Restart Required

After installing PACT (any method), you must **restart Claude Code** for changes to take effect:

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

```
your-project/
├── .claude/                    # Claude Code configuration
│   ├── agents/                 # 7 specialist agents
│   ├── commands/               # 8 PACT workflow commands
│   ├── skills/                 # 13 domain knowledge skills
│   ├── hooks/                  # Automation hooks
│   └── protocols/              # Coordination protocols
├── CLAUDE.md                   # Orchestrator configuration
└── docs/
    ├── plans/                  # Implementation plans
    ├── architecture/           # Design documents
    ├── decision-logs/          # Implementation decisions
    └── preparation/            # Research outputs
```

### For Plugin Installation

```
~/.claude/
├── plugins/
│   └── PACT/         # Plugin location
│       ├── agents/
│       ├── commands/
│       ├── skills/
│       └── hooks/
└── pact-memory/                # Memory database (shared)
    ├── memory.db
    └── models/
        └── all-MiniLM-L6-v2.gguf
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

1. **Add project-specific context** to `CLAUDE.md`
2. **Create custom skills** in `.claude/skills/`
3. **Add custom hooks** in `.claude/hooks/`
4. **Modify agents** in `.claude/agents/` for your domain

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
