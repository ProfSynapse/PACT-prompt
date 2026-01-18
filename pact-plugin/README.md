# PACT Framework Plugin

> **Version**: 2.0.0
> **License**: MIT

VSM-enhanced orchestration framework for AI-assisted software development with Claude Code.

## Installation

### Option 1: GitHub (Recommended - Auto-Updates)

```bash
# Add the marketplace from GitHub
/plugin marketplace add ProfSynapse/PACT-prompt

# Install the plugin
/plugin install PACT@pact-marketplace
```

Enable auto-updates via `/plugin` → **Marketplaces** → select marketplace → **Enable auto-update**

### Option 2: Local Clone

If you've cloned the repository locally:

```bash
# Add from local path
/plugin marketplace add /path/to/PACT-prompt

# Install the plugin
/plugin install PACT@pact-marketplace
```

### Option 3: Let Claude Set It Up

Give Claude this prompt:

```
Set up the PACT plugin from GitHub. Add ProfSynapse/PACT-prompt as a
marketplace and install PACT to user scope so it's available
in all my projects. Enable auto-updates.
```

### Updating the Plugin

**With auto-update enabled**: Updates happen automatically on Claude Code startup.

**Manual update**:
```
/plugin marketplace update pact-marketplace
```

### Set Up the Orchestrator

After installing the plugin, set up the PACT Orchestrator identity:

**If you don't have an existing ~/.claude/CLAUDE.md:**
```bash
# The SessionStart hook will show you the exact path, or use:
cp ~/.claude/plugins/cache/pact-marketplace/PACT/*/CLAUDE.md ~/.claude/CLAUDE.md
```

**If you already have a ~/.claude/CLAUDE.md:**
```bash
# Back up your existing file first
cp ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.backup

# Then either:
# Option A: Replace with PACT (add your customizations after)
cp ~/.claude/plugins/cache/pact-marketplace/PACT/*/CLAUDE.md ~/.claude/CLAUDE.md

# Option B: Prepend PACT content to your existing file
cat ~/.claude/plugins/cache/pact-marketplace/PACT/*/CLAUDE.md ~/.claude/CLAUDE.md.backup > ~/.claude/CLAUDE.md
```

Start a new session — the plugin handles symlinks and protocol references automatically.

---

## What's Included

| Component | Description |
|-----------|-------------|
| **7 Specialist Agents** | Preparer, Architect, Backend/Frontend/Database Coders, n8n, Test Engineer |
| **8 Commands** | orchestrate, comPACT, rePACT, plan-mode, imPACT, peer-review, pin-memory, wrap-up |
| **14 Skills** | Domain knowledge for architecture, coding, testing, security, n8n workflows |
| **Protocols** | VSM-based coordination, algedonic signals, variety management |

## Quick Start

After installing this plugin, use these commands:

```
/PACT:orchestrate <task>     # Full multi-agent workflow
/PACT:comPACT <domain> <task> # Single specialist, light ceremony
/PACT:plan-mode <task>        # Strategic planning before implementation
```

## Key Features (v2.0)

- **Variety Management**: Tasks scored on complexity; ceremony scales accordingly
- **Viability Sensing**: Agents emit HALT/ALERT signals for security, data, ethics issues
- **Adaptive Workflow**: From quick fixes to full orchestration based on task complexity
- **Continuous Audit**: Parallel quality feedback during implementation

## Documentation

For full documentation, visit the main repository:
https://github.com/ProfSynapse/PACT-prompt

## Reference

- pact-protocols.md - Source of truth (see granular pact-*.md files for imports)
- `algedonic.md` - Emergency signal protocol
- `vsm-glossary.md` - VSM terminology in PACT context
