# PACT Skills

This directory contains Claude Code Skills that PACT agents can invoke to access reference knowledge on-demand.

## What Are Skills?

Skills are knowledge libraries that agents invoke during execution. Instead of embedding all reference material in agent prompts, agents stay lean and pull knowledge from skills when needed.

**Benefits:**
- **60-85% context savings** vs embedded knowledge
- **Progressive disclosure** - only loads what's needed
- **Shared knowledge** - multiple agents can use same skill
- **Easy updates** - change skill without touching agents

## Available Skills

| Skill | Phase | Purpose | Used By |
|-------|-------|---------|---------|
| `pact-prepare-research` | Prepare | Research methodologies, source evaluation | pact-preparer |
| `pact-architecture-patterns` | Architect | C4 diagrams, system design patterns | pact-architect |
| `pact-api-design` | Cross-cutting | REST/GraphQL patterns, versioning | pact-architect, pact-backend-coder |
| `pact-backend-patterns` | Code | Service patterns, error handling | pact-backend-coder |
| `pact-frontend-patterns` | Code | Component patterns, state management | pact-frontend-coder |
| `pact-database-patterns` | Code | Schema design, query optimization | pact-database-engineer |
| `pact-testing-patterns` | Test | Test strategies, coverage guidelines | pact-test-engineer |
| `pact-security-patterns` | Cross-cutting | OWASP Top 10, auth patterns | All coders, tester |

## Installation

### Option 1: Copy to Personal Skills Directory (Recommended)

Copy skills to your Claude Code personal skills directory:

```bash
# Create the skills directory if it doesn't exist
mkdir -p ~/.claude/skills

# Copy PACT skills
cp -r skills/* ~/.claude/skills/
```

Skills are auto-discovered from `~/.claude/skills/` - no registration needed.

### Option 2: Symlink (For Development)

If you're developing or testing skills, symlink to avoid copying:

```bash
# Symlink individual skill
ln -s /path/to/PACT-prompt/skills/pact-architecture-patterns ~/.claude/skills/pact-architecture-patterns
```

### Option 3: Project-Level Skills

Skills can also live in your project directory. Claude Code auto-discovers from:
- `~/.claude/skills/` (personal - recommended)
- `./skills/` (project-level)
- `./.claude/skills/` (project-level alternative)

## Verifying Installation

After installation, verify skills are discovered:

1. Start a Claude Code session
2. Ask: "What skills are available?"
3. Confirm `pact-architecture-patterns` appears in the list

## Using Skills with PACT Agents

Once installed, PACT agents automatically invoke skills when appropriate. For example, `pact-architect` will invoke `pact-architecture-patterns` when:
- Creating C4 diagrams
- Defining API contracts
- Reviewing architecture for anti-patterns

You can also manually invoke skills:
```
Use the pact-architecture-patterns skill to help me design this API
```

## Skill Structure

Each skill follows this structure:

```
skill-name/
├── SKILL.md              # Main skill definition (required)
├── LICENSE.txt           # License file
└── references/           # Reference materials (loaded on-demand)
    ├── topic-1.md
    ├── topic-2.md
    └── topic-3.md
```

**Progressive Disclosure:**
- `SKILL.md` body loads when skill activates (~2,800 tokens)
- Reference files load only when specifically needed (~5,000 tokens each)

## Creating New Skills

See [Skills as Agent Knowledge Libraries](../docs/skills-as-agent-knowledge-libraries.md) for the architectural pattern and guidelines for creating new PACT skills.

## Troubleshooting

**Skill not discovered:**
- Verify skill directory name matches `name` field in SKILL.md frontmatter
- Check YAML frontmatter is valid (no syntax errors)
- Ensure skill is in an auto-discovery location

**Skill not activating:**
- Check the `description` field includes relevant trigger terms
- Try manual invocation to test: "Use the [skill-name] skill"

**References not loading:**
- Verify reference files exist in `references/` directory
- Check file paths in SKILL.md match actual file names
