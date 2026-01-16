# PACT Framework Plugin

> **Version**: 2.0.0
> **License**: MIT

VSM-enhanced orchestration framework for AI-assisted software development with Claude Code.

## Installation

### Option 1: Local Marketplace (Recommended for Development)

If you've cloned the PACT-prompt repository:

```bash
# Add the plugin directory as a local marketplace
/plugin marketplace add /path/to/PACT-prompt/pact-plugin

# Install the plugin (user scope = available in all projects)
/plugin install pact-framework@pact-marketplace
```

### Option 2: Let Claude Set It Up

Give Claude this prompt in any project:

```
Set up the PACT plugin from my local clone. The plugin is located at:
/path/to/PACT-prompt/pact-plugin

Add it as a marketplace and install pact-framework to user scope so it's
available in all my projects.
```

### Option 3: Interactive UI

```
/plugin
```
1. Go to **Marketplaces** tab → **Add** → paste the path to `pact-plugin/`
2. Go to **Discover** tab → find `pact-framework` → **Install**

### Updating the Plugin

After pulling updates to the repo:

```
/plugin marketplace update pact-marketplace
```

Or reinstall:
```
/plugin uninstall pact-framework@pact-marketplace
/plugin install pact-framework@pact-marketplace
```

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
