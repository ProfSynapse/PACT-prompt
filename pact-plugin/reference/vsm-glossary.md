# VSM Glossary for PACT

> **Purpose**: Define Viable System Model terminology in the context of the PACT framework.
>
> **Usage**: Reference when reading VSM-enhanced PACT documentation or when VSM terms appear in protocols, agents, or commands.
>
> **Created**: 2026-01-10

---

## Core Systems

### S1 — Operations

**VSM Definition**: The primary activities that produce value. The "muscles and organs" of the organization—the parts that do the actual work.

**In PACT**: The specialist agents that execute development tasks:
- `pact-preparer` — Research and requirements gathering
- `pact-architect` — System design and component planning
- `pact-backend-coder` — Server-side implementation
- `pact-frontend-coder` — Client-side implementation
- `pact-database-engineer` — Data layer implementation
- `pact-test-engineer` — Testing and quality assurance
- `pact-n8n` — Workflow automation

**Key Point**: S1 units need autonomy to respond to their local environment while remaining part of the coherent whole.

---

### S2 — Coordination

**VSM Definition**: The coordination function that resolves conflicts between S1 units, establishes shared language, and dampens oscillations. Acts as a communication conduit between S1 and S3.

**In PACT**: Coordination mechanisms including:
- `pact-protocols.md` — Shared protocols and handoff formats
- Decision logs — Standardized documentation
- Pre-parallel conflict detection — Identifying shared resources before parallel execution
- Resolution authority — Who decides when agents disagree

**Key Point**: S2 enables S1 autonomy by handling inter-unit coordination so each unit doesn't need to negotiate directly with every other unit.

---

### S3 — Control (Operations Management)

**VSM Definition**: Manages the ongoing business of S1-S2-S3. Allocates resources, sets performance expectations, optimizes operational efficiency. Focuses on "inside and now."

**In PACT**: The Orchestrator's operational control function:
- Task execution management
- Agent coordination and sequencing
- Resource allocation (which agents, how many)
- Progress tracking
- Blocker resolution (via `imPACT`)

**Key Point**: S3 asks "Are we doing things right?" — focused on efficient execution of the current plan.

---

### S3* — Audit Channel

**VSM Definition**: A sporadic audit channel that allows S3 to directly monitor S1, bypassing S2's filters. Catches what routine coordination might miss.

**In PACT**: Continuous quality signals:
- Test engineer in parallel audit mode (not just sequential phase)
- Automated checks (lint, type, security scan)
- Early testability feedback during CODE phase
- Direct quality signals to orchestrator

**Key Point**: S3* provides ground truth when S2's coordination might be filtering or missing important signals.

---

### S4 — Intelligence (Development)

**VSM Definition**: Looks at the outside world, scans for threats and opportunities, creates plans for long-term viability. Focuses on "outside and future."

**In PACT**: The intelligence and planning function:
- `plan-mode` — Strategic planning before implementation
- `pact-preparer` — Environment scanning, requirements research
- Adaptation checks — "Should we change course?"
- Risk assessment — "What could go wrong?"

**Key Point**: S4 asks "Are we doing the right things?" — focused on whether the plan still makes sense given external reality.

---

### S5 — Policy (Identity)

**VSM Definition**: Embodies the identity of the organization—values, norms, ethics, culture. The highest decision-making authority. Provides ground rules and enforces them. Balances the tension between S3 and S4.

**In PACT**: The governance layer:
- User as ultimate authority
- CLAUDE.md principles (formalized)
- Non-negotiables (SACROSANCT rules)
- Policy checkpoints
- Arbiter when S3/S4 conflict

**Key Point**: S5 doesn't manage operations—it defines what the system IS and what it will NOT do, regardless of operational pressure.

---

## Key Concepts

### Algedonic Signal

**VSM Definition**: An emergency signal (from Greek *algos* = pain, *hedos* = pleasure) that bypasses the normal management hierarchy. Like pain signals going straight to the brain, these indicate something requiring immediate attention.

**In PACT**: Critical signals that bypass normal orchestration:
- **HALT signals**: Security vulnerabilities, data exposure, ethical violations → immediate stop
- **ALERT signals**: Repeated failures, fundamental misunderstandings → immediate attention

**Contrast with imPACT**: `imPACT` is S3's exception handling (triage within normal flow). Algedonic signals bypass S3 entirely, going direct to S5 (user).

**Key Point**: Not every problem is algedonic. Reserve for viability-threatening situations where normal channels are too slow or might filter the signal.

---

### Autonomy

**VSM Definition**: The capacity of an S1 unit to adapt its behavior based on local conditions without requiring permission from higher systems for every action.

**In PACT**: Specialist agents' authority to:
- Adjust implementation approach based on discoveries
- Request additional context from other specialists
- Recommend scope changes
- Invoke nested PACT cycles for complex sub-tasks

**Bounded by**: Escalation requirements (contradicts architecture, exceeds scope, security implications)

**Key Point**: Autonomy isn't independence—it's the freedom to adapt within defined boundaries while remaining part of the coherent whole.

---

### Cohesion

**VSM Definition**: The property of the whole system acting as a unified entity despite autonomous parts. Achieved through S2-S5 functions, not through eliminating S1 autonomy.

**In PACT**: Maintained through:
- S5 policy constraints (non-negotiables)
- S2 coordination protocols (shared language, conflict resolution)
- S3 operational management (sequencing, resource allocation)
- Common goals and identity

**Key Point**: The goal is autonomy WITH cohesion, not autonomy OR cohesion.

---

### Cybernetic Isomorphism

See: **Recursion**

---

### Homeostasis

**VSM Definition**: The dynamic equilibrium maintained by a viable system. Not static balance, but continuous adjustment to maintain stability.

**In PACT**: Maintained through:
- S3/S4 tension (operations vs adaptation) balanced by S5
- Feedback loops (test results, blocker reports, audit signals)
- Variety management (matching response capacity to task complexity)

**Key Point**: Homeostasis isn't the absence of change—it's stability through continuous adaptation.

---

### Recursion (Cybernetic Isomorphism)

**VSM Definition**: Viable systems contain viable systems. Each S1 unit can be modeled using the identical VSM structure. A department is a viable system within a company, which is a viable system within an industry.

**In PACT**: Nested PACT cycles:
- A complex feature can contain sub-features, each with own P→A→C→T cycle
- A specialist can invoke nested PACT for complex sub-tasks
- The same structure applies at every level

**Nesting Limit**: 2 levels in PACT (to prevent infinite recursion)

**Key Point**: Recursion means the same principles and structure apply at every scale—you don't need different management theories for different levels.

---

### Requisite Variety (Ashby's Law)

**VSM Definition**: "Only variety can absorb variety." A controller must have at least as much variety (range of possible responses) as the system it's trying to control. If the environment has 100 possible states, the controller needs at least 100 possible responses.

**In PACT**: Variety management:
- **Task variety**: Novelty, scope, uncertainty, risk
- **Response capacity**: Available specialists, parallelization, tools, precedent
- **Attenuators**: Reduce incoming complexity (standards, templates, decomposition)
- **Amplifiers**: Increase response capacity (more agents, nested cycles, research)

**Key Point**: You can't control a complex situation with a simple response. Either simplify the situation (attenuate) or increase your response capacity (amplify).

---

### Variety

**VSM Definition**: The number of possible states a system can be in. A measure of complexity. High variety = many possible states = more complex.

**In PACT**: Task complexity dimensions:
- **Novelty**: Routine → Familiar → Novel → Unprecedented
- **Scope**: Single concern → Cross-cutting
- **Uncertainty**: Clear → Ambiguous → Unknown
- **Risk**: Low → Critical

**Key Point**: Variety isn't good or bad—it's a measure that helps you match your response appropriately.

---

### Variety Amplifier

**VSM Definition**: Something that increases the variety (response capacity) of a controller. Allows the system to handle more complex situations.

**In PACT Examples**:
- Invoking additional specialists
- Enabling parallel execution
- Running nested PACT cycles
- Research phase to build understanding
- AI-assisted tools

---

### Variety Attenuator

**VSM Definition**: Something that reduces the variety (complexity) coming into a system. Simplifies what the controller has to deal with.

**In PACT Examples**:
- Applying existing patterns/templates
- Decomposing into smaller sub-tasks
- Constraining scope to well-understood territory
- Using standards to reduce decision space
- Bounded contexts

---

### Viability

**VSM Definition**: The capacity of a system to maintain a separate existence—to survive and thrive in a changing environment. Not just current survival, but ongoing adaptability.

**In PACT**: A development workflow that can:
- Complete current tasks successfully
- Adapt when requirements change
- Handle unexpected complexity
- Recover from failures
- Maintain quality under pressure
- Evolve over time

**Key Point**: Viability isn't efficiency—a highly efficient but brittle system isn't viable. Viability includes resilience and adaptability.

---

## Quick Reference Table

| Term | One-Line Definition | PACT Equivalent |
|------|--------------------| ----------------|
| S1 | Primary operations | Specialist agents |
| S2 | Coordination between S1 units | Protocols, conflict resolution |
| S3 | Operational control (inside-now) | Orchestrator execution mode |
| S3* | Audit channel bypassing S2 | Continuous testing signal |
| S4 | Intelligence (outside-future) | plan-mode, adaptation checks |
| S5 | Policy/identity/values | User + CLAUDE.md principles |
| Algedonic | Emergency bypass signal | HALT/ALERT to user |
| Autonomy | Local adaptation authority | Agent autonomy charter |
| Cohesion | System unity despite autonomy | Shared protocols, policy |
| Homeostasis | Dynamic equilibrium | S3/S4 balance via S5 |
| Recursion | Viable systems within viable systems | Nested PACT cycles |
| Requisite Variety | Controller needs matching complexity | Variety budget assessment |
| Variety | Measure of complexity/possible states | Task complexity dimensions |
| Viability | Capacity for ongoing existence | Adaptive, resilient workflow |

---

## Further Reading

- Beer, Stafford. *Diagnosing the System for Organizations* (1985) — Most accessible introduction
- Beer, Stafford. *Brain of the Firm* (1972) — Original VSM formulation
- Beer, Stafford. *The Heart of Enterprise* (1979) — Detailed theoretical treatment
- [Metaphorum VSM Resources](https://metaphorum.org/staffords-work/viable-system-model)
