# Script Integration Guide

**How PACT Agents Invoke and Use pact-code-analyzer Scripts**

## Overview

This guide explains how PACT agents (pact-architect, pact-test-engineer, pact-backend-coder, pact-frontend-coder) integrate code analysis scripts into their workflows.

## General Integration Pattern

### Step 1: Identify Need for Quantitative Analysis

**Agent Decision Point**: When should an agent invoke scripts vs. read code directly?

**Use Scripts When**:
- Need precise metrics (complexity scores, coupling counts)
- Analyzing large codebase (50+ files)
- Detecting patterns (circular dependencies, orphans)
- Automated threshold checking (complexity > 10)

**Use Native Reading When**:
- Understanding code semantics ("What does this do?")
- Assessing code quality (naming, structure)
- Small codebase (<10 files)
- Need context and intent

### Step 2: Invoke Script via Bash Tool

**Pattern**:
```markdown
I'll analyze the codebase complexity before proceeding.

[Use Bash tool to run script]

[Parse JSON output]

[Make decisions based on metrics]
```

### Step 3: Parse JSON Output

All scripts output structured JSON that agents can parse programmatically.

### Step 4: Interpret Metrics and Make Decisions

Use metrics to guide architecture, testing, or implementation decisions.

### Step 5: Document Findings

Include metric-based insights in phase outputs (architecture specs, test plans, implementation notes).

## Agent-Specific Workflows

### pact-architect Integration

**Use Cases**:
1. Pre-architecture codebase assessment
2. Refactoring planning (identify coupling hotspots)
3. Microservice boundary design
4. Circular dependency identification

**Example Workflow**:

```markdown
I'll assess the existing codebase structure before designing the new notification service.

**Step 1: Analyze Complexity**

I'll identify which existing services have high complexity to avoid adding to them.
```

**Agent invokes**:
```bash
python ~/.claude/skills/pact-code-analyzer/scripts/complexity_analyzer.py \
  --directory src/services/ \
  --threshold 10 \
  --output-format json
```

**JSON Output**:
```json
{
  "summary": {
    "total_files": 8,
    "total_functions": 67,
    "average_complexity": 6.3,
    "files_exceeding_threshold": 2,
    "functions_exceeding_threshold": 5
  },
  "files": [
    {
      "path": "src/services/user_service.py",
      "total_complexity": 45,
      "average_complexity": 9.2,
      "functions": [...]
    }
  ]
}
```

**Agent Interpretation**:
```markdown
**Complexity Analysis Results**:
- user_service.py: Average complexity 9.2 (approaching threshold)
- payment_service.py: Average complexity 12.1 (exceeds threshold)

**Recommendation**: Implement notification service as separate module rather than
extending user_service or payment_service. Both are already complex.

**Step 2: Check Dependencies**

I'll map dependencies to ensure the new service won't create circular references.
```

**Agent invokes**:
```bash
python ~/.claude/skills/pact-code-analyzer/scripts/dependency_mapper.py \
  --directory src/ \
  --language python \
  --detect-circular
```

**JSON Output**:
```json
{
  "summary": {
    "circular_dependencies": 1
  },
  "circular_dependencies": [
    {
      "cycle": ["src/services/user_service.py", "src/services/auth_service.py"],
      "severity": "high"
    }
  ]
}
```

**Agent Interpretation**:
```markdown
**Dependency Analysis Results**:
- Found circular dependency: user_service ↔ auth_service
- Severity: High (2-node cycle)

**Architectural Decision**: Design notification_service to depend only on event bus,
not directly on user_service or auth_service. This avoids introducing new circular
dependencies and sets up for future decoupling of existing cycle.

**Architecture Specification**:
```yaml
notification_service:
  depends_on:
    - event_bus (events from user_service, auth_service)
    - database (notification storage)
  does_not_depend_on:
    - user_service (prevent circular dependency)
    - auth_service (prevent circular dependency)
```
```

### pact-test-engineer Integration

**Use Cases**:
1. Test coverage prioritization (test high-complexity code first)
2. Identifying brittle code (high complexity + high coupling)
3. Orphan module detection (dead code cleanup)

**Example Workflow**:

```markdown
I'll prioritize test coverage based on complexity analysis.

**Step 1: Identify High-Complexity Functions**
```

**Agent invokes**:
```bash
python ~/.claude/skills/pact-code-analyzer/scripts/complexity_analyzer.py \
  --directory src/ \
  --threshold 10 \
  --output-format json
```

**Agent Parses Output**:
```markdown
**High-Complexity Functions Requiring Tests**:

| Function | File | Complexity | Current Coverage |
|----------|------|------------|------------------|
| process_payment | payment_service.py | 15 | 45% |
| validate_order | order_service.py | 12 | 60% |
| calculate_discount | pricing_service.py | 11 | 70% |

**Test Prioritization Matrix**:

1. **CRITICAL**: process_payment (complexity 15, coverage 45%)
   - Required coverage: 95%+ (high complexity)
   - Test cases needed: ~15 (cover all decision paths)
   - Focus: Edge cases, error handling, payment gateway failures

2. **HIGH**: validate_order (complexity 12, coverage 60%)
   - Required coverage: 90%+
   - Test cases needed: ~12
   - Focus: Validation rules, boundary conditions

3. **MEDIUM**: calculate_discount (complexity 11, coverage 70%)
   - Required coverage: 85%+
   - Test cases needed: ~6 additional
   - Focus: Pricing tiers, promotional rules

**Step 2: Identify Coupling for Integration Tests**
```

**Agent invokes**:
```bash
python ~/.claude/skills/pact-code-analyzer/scripts/coupling_detector.py \
  --directory src/services/ \
  --threshold 10 \
  --show-details
```

**Agent Interpretation**:
```markdown
**Coupling Analysis Results**:

Tightly coupled modules (total coupling > 10):
- payment_service.py: 18 (fan-in: 6, fan-out: 12)
- order_service.py: 15 (fan-in: 8, fan-out: 7)

**Integration Test Strategy**:

High coupling indicates integration risk. Prioritize integration tests for:

1. payment_service interactions (12 dependencies)
   - Test with mocked: user_service, inventory_service, notification_service
   - Integration test: Full payment flow with real dependencies

2. order_service interactions (7 dependencies)
   - Test order creation flow across services
   - Verify correct service communication
```

### pact-backend-coder Integration

**Use Cases**:
1. Pre-implementation dependency check (avoid circular dependencies)
2. Coupling assessment before adding features
3. File size compliance (PACT 600-line limit)

**Example Workflow**:

```markdown
I'll implement the new shipping calculator feature. First, let me assess where to add it.

**Step 1: Check Current File Sizes**
```

**Agent invokes**:
```bash
python ~/.claude/skills/pact-code-analyzer/scripts/file_metrics.py \
  --directory src/services/ \
  --language python
```

**JSON Output**:
```json
{
  "summary": {
    "files_exceeding_limit": 2
  },
  "files": [
    {
      "path": "src/services/order_service.py",
      "total_lines": 687,
      "exceeds_size_limit": true,
      "recommendation": "File exceeds PACT 600-line limit. Consider splitting."
    }
  ]
}
```

**Agent Decision**:
```markdown
**File Size Analysis**:
- order_service.py: 687 lines (exceeds 600-line PACT limit)

**Implementation Decision**: Do NOT add shipping calculator to order_service.py.
Instead, create new shipping_service.py module.

**Step 2: Check Dependencies to Avoid Circular Imports**
```

**Agent invokes**:
```bash
python ~/.claude/skills/pact-code-analyzer/scripts/dependency_mapper.py \
  --directory src/services/ \
  --language python \
  --detect-circular
```

**Agent Plan**:
```markdown
**Dependency Analysis**:
- No existing circular dependencies in services/ directory
- order_service currently imports: user_service, inventory_service

**Implementation Plan**:
```python
# src/services/shipping_service.py
# New module - will import order models but NOT order_service
# This prevents circular dependency (order_service will import shipping_service)

from src.models.order import Order
from src.models.address import Address

class ShippingService:
    def calculate_shipping_cost(self, order: Order) -> float:
        # Implementation
        pass
```

**Dependency Design**:
```
order_service.py → shipping_service.py → models/
                                        ↗
                    ✗ NO circular dependency
```
```

### pact-frontend-coder Integration

**Use Cases**:
1. Component complexity assessment
2. Module dependency mapping (component imports)
3. File size compliance

**Example Workflow** (similar to backend):

```markdown
I'll implement the new user profile component. Checking complexity first.

**Step 1: Analyze Existing Component Complexity**
```

**Agent invokes**:
```bash
python ~/.claude/skills/pact-code-analyzer/scripts/complexity_analyzer.py \
  --file src/components/UserProfile.tsx \
  --threshold 10
```

**Note**: TypeScript complexity uses regex (less accurate), so treat as estimate.

## Combining Multiple Script Outputs

### Multi-Metric Analysis Pattern

**Goal**: Combine complexity, coupling, and file metrics for comprehensive assessment.

**Workflow**:

```markdown
I'll perform comprehensive codebase health assessment.

**Step 1: Run all analysis scripts**
```

**Agent invokes in parallel** (if tool supports batch):
```bash
# Complexity
python ~/.claude/skills/pact-code-analyzer/scripts/complexity_analyzer.py \
  --directory src/ --threshold 10 > complexity.json

# Dependencies
python ~/.claude/skills/pact-code-analyzer/scripts/dependency_mapper.py \
  --directory src/ --language python --detect-circular > dependencies.json

# Coupling
python ~/.claude/skills/pact-code-analyzer/scripts/coupling_detector.py \
  --directory src/ --threshold 10 --show-details > coupling.json

# File metrics
python ~/.claude/skills/pact-code-analyzer/scripts/file_metrics.py \
  --directory src/ > metrics.json
```

**Agent Synthesizes Results**:

```markdown
**Codebase Health Assessment**

**Overall Statistics**:
- Total files: 127
- Average complexity: 6.2 (acceptable)
- Total modules: 42
- Circular dependencies: 2 (needs attention)

**High-Risk Modules** (combine metrics):

| Module | Complexity | Coupling | LOC | Risk Level |
|--------|------------|----------|-----|------------|
| user_service.py | 12.3 avg | 18 total | 687 | **CRITICAL** |
| payment_service.py | 9.8 avg | 15 total | 543 | **HIGH** |
| order_service.py | 7.2 avg | 12 total | 498 | **MEDIUM** |

**Risk Classification**:
- **CRITICAL**: High complexity + High coupling + Exceeds size limit
  → Immediate refactoring required
- **HIGH**: 2 of 3 metrics exceed thresholds
  → Refactor before adding features
- **MEDIUM**: 1 of 3 metrics exceeds threshold
  → Monitor, refactor opportunistically

**Recommendations**:

1. **user_service.py** (Critical):
   - Split into user_service.py (core CRUD) and user_permissions_service.py
   - Break circular dependency with auth_service (use events)
   - Reduce coupling (currently depends on 12 modules)

2. **Circular Dependencies** (2 found):
   - user_service ↔ auth_service: Extract shared code to user_auth_models.py
   - payment_service → order_service → payment_service: Use dependency injection

3. **PACT Compliance** (3 files exceed 600 lines):
   - Prioritize splitting based on complexity (high complexity first)
```

## Error Handling Patterns

### Partial Results

Scripts continue on errors and return partial results:

```json
{
  "summary": {...},
  "files": [...],
  "errors": [
    {
      "file": "src/broken_syntax.py",
      "error": "SyntaxError: invalid syntax (line 23)",
      "severity": "warning",
      "action": "Skipped file, continuing with analysis"
    }
  ]
}
```

**Agent Handling**:

```markdown
**Analysis completed with warnings**:
- Skipped src/broken_syntax.py (syntax error)
- All other files analyzed successfully

**Note**: Fix syntax errors before running full analysis.
```

### Script Failures

If script exits with error code 1:

```json
{"error": "Path /invalid/path is outside allowed directory /Users/user/project"}
```

**Agent Handling**:

```markdown
**Error**: Script failed with security error. Path validation rejected directory.

**Resolution**: Use relative path or path within current working directory:
```bash
python ~/.claude/skills/pact-code-analyzer/scripts/complexity_analyzer.py \
  --directory ./src/  # Relative path
```
```

## Performance Considerations

### Large Codebases

For codebases with 500+ files:

1. **Timeout handling**: Scripts enforce 60-second timeout
2. **Sampling**: Analyze critical directories first
3. **Incremental analysis**: Analyze changed files only

**Agent Strategy**:

```markdown
**Large codebase detected (1200+ files)**

I'll analyze critical paths first:
1. src/services/ (business logic)
2. src/api/ (external interfaces)
3. src/models/ (data structures)

For full codebase analysis, consider running scripts offline and loading results.
```

### Caching Results

For repeated analysis during development:

```bash
# Save results for later reference
python [...]/complexity_analyzer.py --directory src/ > analysis/complexity_$(date +%Y%m%d).json
```

**Agent can reference cached results**:
```markdown
Based on complexity analysis from 2025-12-07 (see docs/analysis/complexity_20251207.json):
- payment_service.py: Complexity 15 (high)
- ...
```

## JSON Parsing Examples

### Python Parsing Example

```python
import json
import subprocess

# Run script
result = subprocess.run(
    ['python', 'complexity_analyzer.py', '--directory', 'src/', '--threshold', '10'],
    capture_output=True,
    text=True
)

# Parse JSON
data = json.loads(result.stdout)

# Extract high-complexity functions
high_complexity_funcs = []
for file_data in data['files']:
    for func in file_data['functions']:
        if func['exceeds_threshold']:
            high_complexity_funcs.append({
                'file': file_data['path'],
                'function': func['name'],
                'complexity': func['complexity'],
                'line': func['line']
            })

# Sort by complexity
high_complexity_funcs.sort(key=lambda f: f['complexity'], reverse=True)

# Report
print(f"Found {len(high_complexity_funcs)} high-complexity functions:")
for func in high_complexity_funcs[:5]:  # Top 5
    print(f"  {func['file']}:{func['line']} - {func['function']} (complexity: {func['complexity']})")
```

### JavaScript Parsing Example

```javascript
const { execSync } = require('child_process');

// Run script
const output = execSync(
  'python complexity_analyzer.py --directory src/ --threshold 10',
  { encoding: 'utf-8' }
);

// Parse JSON
const data = JSON.parse(output);

// Extract summary
console.log(`Total functions: ${data.summary.total_functions}`);
console.log(`Average complexity: ${data.summary.average_complexity}`);
console.log(`Functions exceeding threshold: ${data.summary.functions_exceeding_threshold}`);

// Find files needing refactoring
const needsRefactoring = data.files.filter(file =>
  file.functions.some(func => func.exceeds_threshold)
);

console.log(`\nFiles needing refactoring: ${needsRefactoring.length}`);
needsRefactoring.forEach(file => {
  console.log(`  - ${file.path} (avg complexity: ${file.average_complexity})`);
});
```

## Best Practices

### 1. Run Scripts Early

**Before Architecture**: Understand existing complexity before designing new features.

**Before Implementation**: Check file sizes and dependencies before adding code.

**Before Testing**: Identify high-complexity areas needing thorough tests.

### 2. Combine with Native Reading

Scripts provide metrics, reading provides understanding. Use both:

```markdown
**Complexity Analysis**: payment_service.py has complexity 15 (high).

**Code Review** (native reading of payment_service.py):
- High complexity due to multiple payment provider integrations (Stripe, PayPal, Square)
- Logic is clear but could benefit from Strategy pattern to reduce branching
- Recommendation: Extract each provider to separate PaymentProvider implementation
```

### 3. Document Metric-Based Decisions

Include script outputs in architecture specs and implementation notes:

```markdown
## Architecture Decision: New Service Module

**Rationale**:
- Existing order_service.py complexity: 9.8 (approaching threshold 10)
- File size: 687 lines (exceeds PACT 600-line limit)
- Coupling: 12 total dependencies (high)

**Decision**: Create shipping_service.py as separate module.

**Supporting Evidence**:
```json
{
  "file": "src/services/order_service.py",
  "complexity": 9.8,
  "total_lines": 687,
  "total_coupling": 12
}
```
```

### 4. Set Project-Specific Thresholds

Adjust thresholds based on project context:

```bash
# Strict project (high quality requirements)
--threshold 8

# Legacy project (gradual improvement)
--threshold 15  # Don't make it worse
```

### 5. Integrate into CI/CD

For production projects, run scripts in CI to prevent regressions:

```yaml
# .github/workflows/code-quality.yml
- name: Check complexity
  run: |
    python complexity_analyzer.py --directory src/ --threshold 10
    if [ $? -ne 0 ]; then
      echo "Complexity threshold exceeded"
      exit 1
    fi
```

## Summary

Script integration follows this pattern:

1. **Identify need** for quantitative analysis
2. **Invoke script** via Bash tool with appropriate arguments
3. **Parse JSON output** to extract metrics
4. **Interpret metrics** in context of agent's phase (architecture, testing, coding)
5. **Make decisions** based on metrics combined with code understanding
6. **Document findings** in phase outputs

**Key Principles**:
- Scripts provide **metrics**, reading provides **insights**
- Combine multiple scripts for **comprehensive assessment**
- Handle **errors gracefully** with partial results
- **Cache results** for large codebases
- **Document** metric-based architectural decisions

Effective script integration amplifies agent capabilities by adding precise, quantitative analysis to their qualitative code understanding.
