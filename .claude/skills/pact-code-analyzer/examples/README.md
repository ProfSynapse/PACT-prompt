# Code Analyzer Examples

This directory contains worked examples demonstrating how to use the pact-code-analyzer skill scripts in real-world scenarios.

## Available Examples

### 1. Pre-Refactoring Analysis
**File**: `pre-refactoring-analysis.md`

Demonstrates how to analyze a codebase before a major refactoring project. Shows how to combine multiple scripts (complexity analyzer, coupling detector, dependency mapper) to build a comprehensive risk assessment and refactoring plan.

**Use Case**: Planning to split monolithic service into microservices

**Key Learnings**:
- Using multiple scripts together for holistic analysis
- Interpreting metrics to identify refactoring priorities
- Creating risk matrix based on coupling and complexity
- Building phased refactoring roadmap

### 2. Test Coverage Prioritization
**File**: `test-prioritization.md`

Shows how to use complexity metrics to prioritize test coverage efforts. Demonstrates creating a risk-based testing strategy that focuses on high-complexity, high-coupling modules first.

**Use Case**: Improving test coverage in legacy codebase with limited time/resources

**Key Learnings**:
- Combining complexity scores with coupling metrics
- Creating priority matrix for test coverage
- Estimating test effort based on complexity
- Identifying critical paths requiring integration tests

## Example Format

Each example follows this structure:

1. **Scenario**: Real-world context and goals
2. **Initial State**: Description of codebase being analyzed
3. **Analysis Steps**: Actual script invocations with commands
4. **Output Interpretation**: How to read and understand the results
5. **Decisions Made**: Concrete actions based on metrics
6. **Outcome**: Results and lessons learned

## Running the Examples

The examples use fictitious but realistic codebases. You can apply the same analysis patterns to your own projects by:

1. Copy the script invocations from the examples
2. Replace the directory paths with your project paths
3. Adjust thresholds based on your team's standards
4. Interpret results using the guidelines provided

## Related Documentation

For algorithm details and metric definitions, see:

- **references/complexity-calculation.md** - How complexity is calculated
- **references/coupling-metrics.md** - Fan-in/fan-out metrics explained
- **references/dependency-analysis.md** - Dependency graph construction
- **references/script-integration.md** - Agent workflow patterns

## Contributing Examples

If you have additional real-world use cases that would benefit other users, consider documenting them following the same structure as existing examples.
