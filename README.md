# 🛠️ PACT Framework for Claude Code

> **🚀 TL;DR**: This is a "starter kit" for building software with AI. It turns **Claude Code** into a team of expert developers. Download this, rename it to your project name, and you're ready to go!

## ⚠️ Prerequisites

This kit is designed specifically for **Claude Code**. It will not work the same way with other tools.

If you haven't installed Claude Code yet, run this in your terminal:
```bash
npm install -g @anthropic-ai/claude-code
```
*(Or visit the [Claude Code documentation](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview) for installation help)*

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

### 📚 Knowledge Skills

Your agents come pre-loaded with deep knowledge libraries:

- **API Design**: REST/GraphQL best practices and contract definitions.
- **Architecture Patterns**: System design templates and C4 diagrams.
- **Security Patterns**: OWASP guidelines and secure coding practices.
- **Testing Patterns**: Strategies for unit, integration, and E2E testing.
- **Backend/Frontend/Database Patterns**: Language-agnostic best practices for each domain.

### 🛠️ Custom Commands

- **`/pact orchestrate`**: Coordinate the workflow between different agents.
- **`/pact peer-review`**: Have one agent review another's work.
- **`/pact update-context`**: Refresh the project context and documentation.

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
.claude/           # The brain: Agents, Commands, and Skills configuration
CLAUDE.md          # Main entry point and mission for Claude
```
