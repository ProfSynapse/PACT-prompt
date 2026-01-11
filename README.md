# 🛠️ PACT Framework for Claude Code

> **🚀 TL;DR**: This is a "starter kit" for building software with AI. It turns **Claude Code** into a coordinated team of expert developers using VSM-enhanced orchestration. Download this, rename it to your project name, and you're ready to go!

## ⚠️ Prerequisites

This kit is designed specifically for **Claude Code**. It will not work the same way with other tools.

If you haven't installed Claude Code yet, run this in your terminal:
```bash
npm install -g @anthropic-ai/claude-code
```
*(Or visit the [Claude Code documentation](https://code.claude.com/docs/en/quickstart) for installation help)*

## ⚡ How to Start Your New Project

Follow these simple steps to use this kit as the foundation for your next big idea.

### 1. Download & Rename
You are going to download this code and rename the folder to match your project.

**Option A: Using Git (Recommended)**
Open your terminal and run this command (replace `my-new-project` with your actual project name):
```bash
git clone https://github.com/ProfSynapse/PACT-prompt.git my-new-project
```

**Option B: Download ZIP**
1. Click the green **<> Code** button at the top of this GitHub page.
2. Select **Download ZIP**.
3. Extract the ZIP file to your computer.
4. **Rename the folder** from `PACT-prompt` to your project name (e.g., `my-awesome-app`).

### 2. Initialize Your Repository
Now, let's make this folder *yours*. Open your IDE (like VS Code) and navigate into your new folder:

Optionally, remove the old git history and start a fresh one for your project:

**For Mac/Linux/Git Bash:**
```bash
rm -rf .git
git init
git add .
git commit -m "Initial commit using PACT Framework"
```

**For Windows PowerShell:**
```powershell
Remove-Item -Recurse -Force .git
git init
git add .
git commit -m "Initial commit using PACT Framework"
```

### 3. Boot Up Claude
You are ready! While still inside your project folder, run:

```bash
claude
```

Claude will detect the `.claude` folder and automatically load your team of agents. You can now say things like:
> *"I want to build a Todo app with React. Please start the PACT process."*

---

## 🧠 What's Inside?

This repository transforms Claude from a general assistant into a coordinated team of specialists.

### 🤖 Specialized Agents

Instead of one generalist, you get a team of experts:

- **🕵️ PACT Preparer** (`pact-preparer`): Research specialist. Gathers context, reads docs, and validates requirements before a single line of code is written.
- **🏛️ PACT Architect** (`pact-architect`): System designer. Creates comprehensive architectural specs, diagrams, and blueprints based on the Preparer's research.
- **⚙️ PACT Backend Coder** (`pact-backend-coder`): Implementation expert. Writes clean, secure, and efficient backend code following the Architect's blueprints.
- **🎨 PACT Frontend Coder** (`pact-frontend-coder`): UI/UX specialist. Implements responsive and accessible interfaces.
- **🗄️ PACT Database Engineer** (`pact-database-engineer`): Data specialist. Designs schemas, optimizes queries, and manages data integrity.
- **🧪 PACT Test Engineer** (`pact-test-engineer`): QA expert. Writes comprehensive test suites to verify functionality and security.

### 🎛️ VSM-Enhanced Orchestration

PACT 2.0 uses principles from the **Viable System Model** (VSM) to coordinate agents intelligently:

- **Variety Management**: Tasks are scored on complexity (novelty, scope, uncertainty, risk). Simple tasks get lightweight workflows; complex tasks get full ceremony with planning phases.
- **Adaptive Workflow**: The orchestrator selects the right level of process—from quick single-agent fixes (`/PACT:comPACT`) to multi-agent orchestration (`/PACT:orchestrate`) to strategic planning (`/PACT:plan-mode`).
- **Viability Sensing**: Agents can emit emergency signals (HALT/ALERT) that bypass normal workflow when they detect security issues, data risks, or ethical concerns—ensuring critical problems reach you immediately.
- **Continuous Audit**: The test engineer provides parallel quality feedback during implementation, not just at the end.

This means less ceremony for simple tasks, more rigor for complex ones, and automatic escalation when something goes wrong.

### 🛠️ Custom Commands

- **`/PACT:orchestrate`**: Delegate a task to specialist agents (multi-agent, full ceremony).
- **`/PACT:comPACT`**: Delegate a focused task to a single specialist (light ceremony).
- **`/PACT:plan-mode`**: Multi-agent planning consultation before implementation (no code changes).
- **`/PACT:rePACT`**: Recursive nested PACT cycle for complex sub-tasks.
- **`/PACT:imPACT`**: Triage when blocked (Redo prior phase? Additional agents needed?).
- **`/PACT:peer-review`**: Commit, create PR, and run multi-agent code review.
- **`/PACT:log-changes`**: Update `CLAUDE.md` to reflect recent significant changes.
- **`/PACT:wrap-up`**: End-of-session cleanup and documentation sync.

#### comPACT Examples

```
/PACT:comPACT backend Fix the null pointer in auth middleware
/PACT:comPACT frontend Add loading spinner to submit button
/PACT:comPACT database Add index to users.email column
/PACT:comPACT test Add unit tests for payment module
/PACT:comPACT architect Is singleton the right pattern for this config manager?
/PACT:comPACT prepare Research OAuth2 best practices for our use case
```

comPACT auto-selects the specialist when the task is clear, or asks for clarification when ambiguous:

```
/PACT:comPACT Fix the login bug
→ Claude asks: "Which specialist should handle this? Backend / Frontend / Database"
```

## 🎯 Why Use This?

**"Principled Vibe Coding"**
We all love the speed of "vibe coding" (letting AI handle the implementation), but it often leads to chaotic, unmaintainable code. The PACT framework brings **engineering discipline** to AI speed.

By starting with this repository, you ensure that:
1. **Preparation** happens before coding.
2. **Architecture** is designed, not guessed.
3. **Code** follows strict standards.
4. **Testing** is integral, not an afterthought.

## 📂 Project Structure

```
.claude/                  # Claude Code configuration (auto-loaded)
  agents/                 # Specialist agent definitions
  commands/PACT/          # PACT workflow commands
  protocols/              # Coordination protocols (algedonic, pact-protocols)
pact-plugin/              # Plugin distribution (for sharing)
  .claude-plugin/         # Plugin manifest (plugin.json, marketplace.json)
  reference/              # Reference docs (VSM glossary)
  skills/                 # Dynamic knowledge skills
docs/                     # Development documentation
CLAUDE.md                 # Mission and orchestrator configuration
```
