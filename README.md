# 🛠️ PACT Framework Prompts

> **🚀 TL;DR**: Ready-to-use prompts that implement the PACT framework (Prepare, Architect, Code, Test) for principled AI-assisted coding. Works with Claude, Cline, Cursor, Roo Code, and other AI coding assistants. Transforms chaotic "vibe coding" into systematic, secure, maintainable development.

## What is the PACT Framework?

The PACT Framework is a structured approach to **"principled vibe coding"** - a methodology that harnesses the speed and creativity of AI-assisted development while maintaining high standards for code quality, security, and maintainability.

In February 2025, Andrej Karpathy introduced the concept of "vibe coding" - letting AI handle implementation details while you focus on the vision. The PACT Framework ensures that this powerful approach doesn't compromise on software engineering principles.

### The Four Phases

- **📋 Prepare**: Research documentation, gather context, understand requirements and security standards
- **🏗️ Architect**: Design system structure, plan components, define secure interfaces  
- **💻 Code**: Implement systematically with quality principles and security controls
- **🧪 Test**: Verify functionality, validate security, ensure reliability

## 🎯 Available Implementations

### For General AI Assistants (Claude, Cline, Cursor, etc.)
- **File**: `PACT_Prompt.md`
- **Best for**: Single AI assistant workflows
- **Features**: Comprehensive PACT methodology with security focus

### For Roo Code (Specialized Team Workflow)
- **File**: `PACT_Roo_Code.json`
- **Best for**: Complex projects requiring specialized roles
- **Features**: 7 specialist modes including Project Orchestrator, security-focused specialists

## 📚 Learn More About the Framework

For a deep dive into the theory and methodology behind principled vibe coding, read our comprehensive guide:

**[The PACT Framework: A Magical Guide to Principled Vibe Coding](https://blog.synapticlabs.ai/pact-framework-vibe-coding-guide)**

This blog post explains:
- The evolution from traditional coding to vibe coding
- Why structure matters even with AI assistance
- Detailed breakdown of each PACT phase
- Real-world applications and best practices

## 🚀 Quick Start

### Using with LLMs (Web Interface)
1. Copy the contents of `PACT_Prompt.md`
2. Paste into a new GPT/Gem/Project as your System Instructions
3. Start your project with PACT methodology

### Using with Claude Code

#### Basic Setup
1. Copy the contents of `PACT_Prompt.md`
2. Use the command `/init` to create your CLAUDE.md (if you haven't already)
3. Add the prompt to the beginning of your CLAUDE.md

#### Advanced: PACT Sub-Agents for Claude Code
For enhanced workflow automation, use the specialized PACT sub-agents included in this repository:

**Setup Instructions:**
1. Copy the entire `claude-agents/` folder to your project's `.claude/agents/` directory
2. Or copy individual agent files from `claude-agents/` to your global `~/.claude/agents/` directory
3. Restart Claude Code to load the new sub-agents

**Available PACT Sub-Agents:**
- **🎯 PACT Orchestrator** (`CLAUDE.md`): Main coordinator that manages the entire PACT workflow
- **📚 pact-preparer**: Research and documentation specialist for the Prepare phase
- **🏛️ pact-architect**: System design expert for the Architect phase  
- **💻 pact-backend-coder**: Backend implementation specialist for the Code phase
- **🎨 pact-frontend-coder**: Frontend implementation specialist for the Code phase
- **🗄️ pact-database-engineer**: Database design and implementation specialist for the Code phase
- **🧪 pact-test-engineer**: Quality assurance and testing specialist for the Test phase

**Usage:**
- The Orchestrator automatically delegates tasks to appropriate specialists
- Use explicit commands like: "Use the pact-preparer agent to research API documentation"
- Run `/agents` to see all available sub-agents

Learn more about Claude Code sub-agents: [docs.anthropic.com/en/docs/claude-code/sub-agents](https://docs.anthropic.com/en/docs/claude-code/sub-agents)

### Using with Cline (VS Code Extension)
1. Copy the contents of `PACT_Prompt.md`
2. Add to your Cline system prompt or `.clinerules/` directory
3. Cline will automatically apply PACT principles

### Using with Cursor
1. Copy the contents of `PACT_Prompt.md`
2. Add to your Cursor system prompt settings
3. Reference in your coding sessions

### Using with Roo Code (Advanced Team Workflow)
1. Open Roo Code settings
2. Import the custom modes from `PACT_Roo_Code.json`
3. Use the **🎯 PACT Project Orchestrator** mode for complex projects

## 🔧 How It Works

### Traditional Approach
```
Idea → Code → Debug → Ship → 🔥 Problems
```

### PACT Framework Approach
```
Idea → Prepare → Architect → Code → Test → 🚀 Quality Product
```

### Key Benefits

- **🛡️ Security by Design**: Security considerations integrated throughout all phases
- **📏 Code Modularity**: Enforced file size limits (500 lines) and modular design
- **📖 Documentation-Driven**: Maintains comprehensive project documentation
- **🔄 Systematic Progress**: Clear phase transitions with quality gates
- **🎯 Specialist Roles**: Roo Code modes provide focused expertise for each domain
- **🧪 Quality Assurance**: Built-in testing and verification processes

## 🏗️ Framework Principles

### Prepare Phase Principles
- Documentation First
- Context Gathering  
- Dependency Mapping
- Security Research
- Best Practice Investigation

### Architect Phase Principles
- Single Responsibility
- Loose Coupling
- Security by Design
- Modular Design
- Clear Interfaces

### Code Phase Principles
- Clean, Readable Code
- DRY (Don't Repeat Yourself)
- Security Controls Implementation
- Incremental Development
- Comprehensive Error Handling

### Test Phase Principles
- Security Testing
- Edge Case Coverage
- Integration Verification
- Performance Validation
- Regression Prevention

## 🎭 Roo Code Specialist Modes

When using the Roo Code implementation, you get access to specialized AI personas:

- **🎯 PACT Project Orchestrator**: Coordinates the entire workflow
- **📚 PACT Preparer**: Documentation and research specialist
- **🏛️ PACT Architect**: System design and security architecture expert
- **💻 PACT Backend Coder**: Server-side implementation specialist
- **🎨 PACT Frontend Coder**: UI/UX implementation expert
- **🗄️ PACT Database Engineer**: Data modeling and optimization specialist
- **🧪 PACT Tester**: Quality assurance and security testing expert

## 🔒 Security Focus

The PACT Framework emphasizes **"secure by design"** principles:

- Threat modeling during the Architect phase
- Security control implementation during Code phase
- Vulnerability testing during Test phase
- No hardcoded secrets or credentials
- Input validation and output encoding
- Defense-in-depth strategies

## 🤝 Contributing

We welcome contributions to improve the PACT Framework prompts:

1. Fork the repository
2. Create a feature branch
3. Test your changes with your preferred AI assistant
4. Submit a pull request with clear descriptions

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Created by [Professor Synapse](https://synapticlabs.ai) as part of the Vibe Coding Principles series.

Inspired by Andrej Karpathy's concept of "vibe coding" and the need for structured approaches to AI-assisted development.

---

**Ready to transform your AI-assisted coding?** Choose your implementation above and start building better software with the PACT Framework! 🚀
