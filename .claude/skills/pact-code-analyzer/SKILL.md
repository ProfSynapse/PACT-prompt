---
name: pact-code-analyzer
description: |
  ALL PHASES: Executable Python scripts for automated code analysis.

  Provides computational code analysis including cyclomatic complexity calculation,
  dependency mapping, coupling detection, and file statistics. Scripts output JSON
  for easy parsing and integration with agent workflows.

  Use when: analyzing codebase complexity, detecting circular dependencies,
  measuring coupling between modules, generating dependency graphs, identifying
  high-complexity functions requiring refactoring or testing, assessing PACT
  compliance (600-line file limit), prioritizing test coverage, planning
  architectural refactoring.

  DO NOT use for: semantic code understanding, architectural pattern recognition,
  code quality assessment (use native reading for these). Scripts provide metrics,
  not insights. For small codebases (<10 files), native reading is often faster.

  EXPERIMENTAL: Version 0.1.0 - Testing executable code in skills pattern.
allowed-tools:
  - Read
  - Bash
  - Grep
metadata:
  phase: "All"
  version: "0.1.0-experimental"
  status: "experimental"
  primary-agents:
    - pact-architect
    - pact-test-engineer
    - pact-backend-coder
    - pact-frontend-coder
  related-skills:
    - pact-architecture-patterns
    - pact-backend-patterns
    - pact-frontend-patterns
    - pact-testing-patterns
---

# pact-code-analyzer

**EXPERIMENTAL SKILL** - Executable Python scripts for computational code analysis.

## Overview

This skill provides four Python scripts that perform quantitative analysis of codebases:

1. **complexity_analyzer.py** - Calculate cyclomatic complexity per function
2. **dependency_mapper.py** - Map module dependencies and detect circular references
3. **coupling_detector.py** - Measure module coupling (fan-in/fan-out)
4. **file_metrics.py** - Calculate lines of code, function counts, PACT compliance

### What Computational Analysis Provides vs. Native Reading

**Use scripts when you need**:
- Precise quantitative metrics (complexity scores, coupling counts)
- Large-scale analysis (100+ files) faster than reading individually
- Deterministic measurements across multiple runs
- Dependency graphs (circular dependency detection)
- Automated threshold detection (complexity > 10, files > 600 lines)

**Use native reading when you need**:
- Semantic understanding ("What does this code do?")
- Architectural pattern identification
- Code quality assessment (naming, structure, maintainability)
- Small codebase analysis (<10 files)
- Context and intent comprehension

**Best Practice**: Combine both - scripts for metrics, reading for insights.

### Security Considerations

All scripts include:
- Path validation (reject `..`, symlinks, paths outside CWD)
- File size limits (1MB per file)
- Timeout handling (60 seconds total)
- Graceful error handling (partial results on errors)
- Read-only analysis (no code modification)

## Quick Reference: Available Scripts

### 1. complexity_analyzer.py

**Purpose**: Calculate cyclomatic complexity for Python, JavaScript, TypeScript files.

**Invocation**:
```bash
# Single file
python ~/.claude/skills/pact-code-analyzer/scripts/complexity_analyzer.py \
  --file src/services/user_service.py \
  --threshold 10

# Entire directory
python ~/.claude/skills/pact-code-analyzer/scripts/complexity_analyzer.py \
  --directory src/ \
  --threshold 8 \
  --output-format json
```

**Arguments**:
- `--file <path>`: Analyze single file
- `--directory <path>`: Analyze all files recursively
- `--threshold <int>`: Flag functions exceeding complexity (default: 10)
- `--output-format <json|summary>`: Output format (default: json)

**Output Format** (JSON):
```json
{
  "summary": {
    "total_files": 15,
    "total_functions": 127,
    "average_complexity": 4.2,
    "files_exceeding_threshold": 3,
    "functions_exceeding_threshold": 8
  },
  "files": [
    {
      "path": "src/services/user_service.py",
      "language": "python",
      "analysis_method": "python_ast",
      "total_complexity": 45,
      "average_complexity": 7.5,
      "functions": [
        {
          "name": "create_user",
          "line": 23,
          "complexity": 5,
          "exceeds_threshold": false
        },
        {
          "name": "update_permissions",
          "line": 67,
          "complexity": 12,
          "exceeds_threshold": true,
          "recommendation": "Consider breaking into smaller functions"
        }
      ]
    }
  ]
}
```

**Analysis Methods** (`analysis_method` field):
- `python_ast` - Python AST parsing (always used for .py files)
- `nodejs_ast` - Node.js AST parsing via typhonjs-escomplex (JS/TS when available)
- `regex_fallback` - Regex pattern matching (JS/TS fallback when Node.js unavailable)

**Use Cases**:
- Identify high-complexity functions requiring refactoring
- Prioritize test coverage for complex code
- Assess codebase maintainability before architecture changes
- Track complexity trends over time

---

### 2. dependency_mapper.py

**Purpose**: Map import/require dependencies, detect circular dependencies and orphan modules.

**Invocation**:
```bash
# Map Python dependencies
python ~/.claude/skills/pact-code-analyzer/scripts/dependency_mapper.py \
  --directory src/ \
  --language python \
  --detect-circular

# Generate DOT graph for visualization
python ~/.claude/skills/pact-code-analyzer/scripts/dependency_mapper.py \
  --directory src/ \
  --language javascript \
  --output-graph dot > dependencies.dot
```

**Arguments**:
- `--directory <path>`: Root directory to analyze (required)
- `--language <python|javascript|typescript>`: Language (required)
- `--output-graph <json|dot>`: Output format (default: json)
- `--detect-circular`: Enable circular dependency detection

**Output Format** (JSON):
```json
{
  "summary": {
    "total_modules": 42,
    "total_dependencies": 156,
    "circular_dependencies": 2,
    "orphan_modules": 3,
    "max_depth": 7
  },
  "modules": [
    {
      "path": "src/services/user_service.py",
      "imports": ["src/models/user.py", "src/utils/validation.py"],
      "imported_by": ["src/api/users.py", "src/api/auth.py"],
      "is_orphan": false
    }
  ],
  "circular_dependencies": [
    {
      "cycle": [
        "src/services/user_service.py",
        "src/services/auth_service.py",
        "src/services/user_service.py"
      ],
      "severity": "medium"
    }
  ],
  "orphan_modules": ["src/utils/deprecated_helper.py"]
}
```

**Use Cases**:
- Detect circular dependencies before they cause problems
- Identify orphan modules (dead code candidates)
- Understand module dependency structure
- Plan microservice boundaries for refactoring
- Generate dependency graphs for documentation

---

### 3. coupling_detector.py

**Purpose**: Detect tight coupling by measuring fan-in (incoming) and fan-out (outgoing) dependencies.

**Invocation**:
```bash
# Detect tightly coupled modules
python ~/.claude/skills/pact-code-analyzer/scripts/coupling_detector.py \
  --directory src/ \
  --threshold 15 \
  --show-details
```

**Arguments**:
- `--directory <path>`: Root directory to analyze (required)
- `--threshold <int>`: Flag modules exceeding total coupling (default: 10)
- `--show-details`: Show detailed fan-in/fan-out lists

**Output Format** (JSON):
```json
{
  "summary": {
    "total_modules": 42,
    "average_coupling": 3.7,
    "tightly_coupled_modules": 5,
    "coupling_threshold": 10,
    "top_coupled_modules": [
      {"path": "src/services/user_service.py", "coupling": 20}
    ]
  },
  "modules": [
    {
      "path": "src/services/user_service.py",
      "outgoing_dependencies": 8,
      "incoming_dependencies": 12,
      "total_coupling": 20,
      "exceeds_threshold": true,
      "fan_out": ["src/models/user.py", "src/repositories/user_repository.py"],
      "fan_in": ["src/api/users.py", "src/api/auth.py"],
      "recommendation": "High coupling (20 dependencies). Consider splitting into smaller services or using events to decouple."
    }
  ]
}
```

**Use Cases**:
- Identify tightly coupled modules before refactoring
- Assess architectural health (high coupling = high risk)
- Prioritize decoupling efforts
- Guide microservice boundary design

---

### 4. file_metrics.py

**Purpose**: Calculate basic file statistics and PACT compliance (600-line limit).

**Invocation**:
```bash
# Single file metrics
python ~/.claude/skills/pact-code-analyzer/scripts/file_metrics.py \
  --file src/services/user_service.py \
  --language python

# Directory analysis
python ~/.claude/skills/pact-code-analyzer/scripts/file_metrics.py \
  --directory src/ \
  --language python
```

**Arguments**:
- `--file <path>`: Analyze single file
- `--directory <path>`: Analyze all files in directory
- `--language <python|javascript|typescript>`: Language filter (optional)

**Output Format** (JSON):
```json
{
  "summary": {
    "total_files": 127,
    "total_lines": 18543,
    "total_code_lines": 14320,
    "total_comment_lines": 2145,
    "total_blank_lines": 2078,
    "total_functions": 892,
    "total_classes": 147,
    "average_file_size": 146,
    "files_exceeding_limit": 3
  },
  "files": [
    {
      "path": "src/services/user_service.py",
      "language": "python",
      "total_lines": 245,
      "code_lines": 189,
      "comment_lines": 34,
      "blank_lines": 22,
      "functions": 18,
      "classes": 2,
      "imports": 12,
      "exceeds_size_limit": false,
      "size_limit": 600,
      "recommendation": "File size is acceptable"
    }
  ]
}
```

**Use Cases**:
- Identify files exceeding PACT 600-line limit
- Assess codebase size and maintainability
- Track comment density (documentation quality)
- Find candidates for splitting/refactoring

## Common Workflows

### Workflow 1: Pre-Architecture Codebase Assessment

**Scenario**: Architect planning new feature, needs to understand existing complexity.

**Steps**:
1. Run complexity analysis to identify complex modules
2. Run dependency mapping to understand module structure
3. Run coupling detection to find tightly coupled areas
4. Synthesize findings: Avoid adding to already complex/coupled areas

**Example**:
```bash
# Step 1: Find complex code
python ~/.claude/skills/pact-code-analyzer/scripts/complexity_analyzer.py \
  --directory src/services/ --threshold 10

# Step 2: Map dependencies
python ~/.claude/skills/pact-code-analyzer/scripts/dependency_mapper.py \
  --directory src/ --language python --detect-circular

# Step 3: Detect coupling
python ~/.claude/skills/pact-code-analyzer/scripts/coupling_detector.py \
  --directory src/services/ --threshold 15 --show-details
```

**Interpretation**:
- High complexity (>10): Avoid adding features here, create new modules
- Circular dependencies: Design to prevent new cycles
- High coupling (>15): Use dependency injection or events to decouple

---

### Workflow 2: Test Coverage Prioritization

**Scenario**: Test engineer identifying high-risk code needing test coverage.

**Steps**:
1. Run complexity analysis to find complex functions
2. Cross-reference with existing test coverage data
3. Prioritize: High complexity + Low coverage = High priority

**Example**:
```bash
# Identify complex functions
python ~/.claude/skills/pact-code-analyzer/scripts/complexity_analyzer.py \
  --directory src/ --threshold 10 --output-format json > complexity.json

# Parse JSON to identify functions with complexity > 10
# Cross-reference with coverage report
# Write tests for high-complexity, low-coverage functions
```

**Decision Matrix**:
| Complexity | Coverage | Priority |
|------------|----------|----------|
| High (>10) | Low (<80%) | **CRITICAL** |
| High (>10) | High (>80%) | Medium |
| Low (<10) | Low (<80%) | Low |
| Low (<10) | High (>80%) | Maintain |

---

### Workflow 3: Refactoring Planning

**Scenario**: Planning to split monolithic service into microservices.

**Steps**:
1. Generate dependency graph to visualize module relationships
2. Identify circular dependencies (must break before splitting)
3. Detect coupling hotspots (service boundaries)
4. Design microservices with minimal cross-service coupling

**Example**:
```bash
# Generate dependency graph
python ~/.claude/skills/pact-code-analyzer/scripts/dependency_mapper.py \
  --directory src/ --language python --detect-circular --output-graph dot > deps.dot

# Visualize with Graphviz (if installed)
dot -Tpng deps.dot -o dependencies.png

# Identify coupling
python ~/.claude/skills/pact-code-analyzer/scripts/coupling_detector.py \
  --directory src/ --threshold 10 --show-details > coupling.json
```

**Refactoring Strategy**:
- Break circular dependencies first (prerequisite)
- Group tightly coupled modules into same microservice
- High fan-in modules become shared services
- High fan-out modules need dependency injection

---

### Workflow 4: PACT Compliance Check

**Scenario**: Ensure codebase follows PACT 600-line file limit.

**Steps**:
1. Run file metrics across entire codebase
2. Identify files exceeding 600 lines
3. Prioritize splitting largest/most complex files

**Example**:
```bash
# Check PACT compliance
python ~/.claude/skills/pact-code-analyzer/scripts/file_metrics.py \
  --directory src/ --output-format json > metrics.json

# Parse to find files with exceeds_size_limit: true
# Combine with complexity analysis for splitting priorities
```

**Splitting Criteria**:
- File > 600 lines + High complexity: **Immediate refactor**
- File > 600 lines + Low complexity: Refactor when touching file
- File < 600 lines: Acceptable

## Script Integration Guide

### Invoking Scripts from Agent Prompts

**Pattern**:
```
I'll analyze the codebase complexity using the pact-code-analyzer skill.

[Invoke Bash tool with script command]

[Parse JSON output]

[Make decisions based on metrics]
```

**Example Agent Workflow**:
```markdown
I'll assess the existing user service complexity before recommending where to add the new feature.

```bash
python ~/.claude/skills/pact-code-analyzer/scripts/complexity_analyzer.py \
  --file src/services/user_service.py --threshold 10
```

[Script outputs JSON showing complexity of 15, exceeding threshold]

The user_service.py has complexity of 15, exceeding the recommended threshold of 10.
I recommend implementing the new feature as a separate service module to avoid
increasing complexity in an already complex file.
```

### Parsing JSON Output

**Python Example**:
```python
import json

# Run script and capture output
result = subprocess.run([...], capture_output=True, text=True)
data = json.loads(result.stdout)

# Extract metrics
summary = data['summary']
high_complexity = [
    f for f in data['files']
    if any(func['exceeds_threshold'] for func in f['functions'])
]
```

**Agent Interpretation**:
- `summary.functions_exceeding_threshold > 0`: Flag for refactoring
- `circular_dependencies` length > 0: Critical architectural issue
- `total_coupling > threshold`: High coupling risk
- `exceeds_size_limit: true`: PACT compliance violation

### Error Handling

Scripts return partial results on errors with `errors` array in JSON:

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

**Agent Error Handling**:
1. Check for `errors` key in output
2. If critical file failed, warn user
3. If non-critical, proceed with partial results
4. Log errors for troubleshooting

## Reference Files

For detailed algorithm explanations and integration guidance, see:

- **references/complexity-calculation.md** - McCabe's cyclomatic complexity algorithm, decision point counting methodology, interpretation guidelines
- **references/coupling-metrics.md** - Fan-in/fan-out calculation, coupling patterns (God Objects, utility modules), refactoring strategies to reduce coupling
- **references/dependency-analysis.md** - Dependency graph construction, circular dependency detection (DFS), orphan module identification
- **references/script-integration.md** - Detailed agent workflow examples, JSON parsing patterns, combining multiple script outputs

## Example Workflows

For worked examples demonstrating real-world usage, see:

- **examples/pre-refactoring-analysis.md** - Complete workflow for analyzing codebase before microservice extraction (combining complexity + coupling + dependency analysis)
- **examples/test-prioritization.md** - Using metrics to prioritize test coverage in legacy codebase (risk-based testing strategy)

## Experimental Status and Feedback

**This is an experimental skill (v0.1.0)** testing executable code in skills pattern.

### Known Limitations

**JavaScript/TypeScript Complexity Analysis**:
The complexity analyzer supports two analysis methods:

1. **Node.js AST Analysis** (High Accuracy) - Used when Node.js and npm dependencies are installed:
   - Uses `acorn` parser for accurate AST-based analysis
   - Supports modern ES6+ JavaScript (.js files)
   - Accurate cyclomatic complexity calculation matching McCabe's methodology
   - **Limitation**: Currently only supports .js files (not .jsx, .ts, .tsx)

2. **Regex Fallback** (Best-Effort) - Used when Node.js is unavailable or for TypeScript files:
   - Pattern-based function detection
   - Supports .js, .ts, .tsx files
   - May miss or miscount edge cases (some arrow function patterns, minified code)
   - Suitable for rough estimates

**When Regex Fallback is Used**:

The analyzer automatically falls back to regex-based analysis when any of these conditions occur:

| Condition | `analysis_method` Value | Notes |
|-----------|------------------------|-------|
| Node.js not installed on system | `regex_fallback` | Check with `node --version` |
| npm dependencies not installed | `regex_fallback` | Run `npm install` in scripts/ directory |
| Node.js analyzer script fails | `regex_fallback` | Script syntax error or runtime exception |
| Node.js analyzer times out | `regex_fallback` | 30-second timeout per file |
| Node.js returns invalid JSON | `regex_fallback` | Parsing error in Node.js output |
| File is .ts or .tsx | `regex_fallback` | TypeScript not yet supported in Node.js analyzer |

**Checking Which Method Was Used**:

The output JSON always includes an `analysis_method` field for each file:

```json
{
  "path": "src/utils/helper.js",
  "language": "javascript",
  "analysis_method": "nodejs_ast",  // or "regex_fallback"
  "functions": [...]
}
```

**Installing Node.js Dependencies for High-Accuracy JS Analysis**:
```bash
cd ~/.claude/skills/pact-code-analyzer/scripts/
npm install
```

After installation, .js files will automatically use `nodejs_ast` method. TypeScript files (.ts, .tsx) will continue using `regex_fallback` until TypeScript support is added.

**Import Resolution**:
- Limited to local project files (no node_modules analysis)
- Path aliases (e.g., `@/components` in webpack/vite configs) not resolved
- Relative imports fully supported; absolute imports best-effort

**coupling_detector.py**:
- Python-only (does not support JavaScript/TypeScript)
- Uses simplified dependency graph (not full dependency_mapper.py algorithm)

**Comment Detection Edge Cases**:
- Python docstrings counted as comments (may affect comment density metrics)
- JS/TS inline comments after code may be miscounted
- Comments inside strings may be incorrectly detected

### Platform Considerations

**macOS/Linux**: Full functionality including 60-second timeout enforcement via `signal.SIGALRM`.

**Windows**:
- Scripts run without timeout enforcement (`signal.SIGALRM` not available)
- Potential for long-running processes on very large codebases
- Workaround: Manually interrupt with Ctrl+C if script hangs
- Recommendation: Limit analysis scope (e.g., specific directories vs entire project)

**Feedback Needed**:
1. Do scripts provide value over native reading for your use cases?
2. Which scripts are most/least useful?
3. What additional metrics would be valuable?
4. Accuracy issues or false positives?

**Future Enhancements** (post-MVP):
- Ruby, Go, Java language support
- Code churn analysis (git history)
- Comment density metrics
- Duplication detection
- Interactive HTML reports

## Installation and Requirements

**Requirements**:
- Python 3.11+ (standard library only, no pip dependencies)
- Unix-like OS for timeout handling (macOS, Linux; Windows best-effort)
- **Optional**: Node.js 18+ for high-accuracy JS/TS complexity analysis

**Installation**:
Scripts are included in this skill directory. No additional installation needed for basic functionality.

**Optional: Enable High-Accuracy JS/TS Complexity Analysis**:
```bash
# Install Node.js dependencies for AST-based JS/TS analysis
cd ~/.claude/skills/pact-code-analyzer/scripts/
npm install
```

Without Node.js dependencies, JS/TS files are analyzed using regex patterns (less accurate but functional).

**Verification**:
```bash
# Test complexity analyzer (Python)
python ~/.claude/skills/pact-code-analyzer/scripts/complexity_analyzer.py \
  --file ~/.claude/skills/pact-code-analyzer/scripts/complexity_analyzer.py

# Test file metrics
python ~/.claude/skills/pact-code-analyzer/scripts/file_metrics.py \
  --directory ~/.claude/skills/pact-code-analyzer/scripts/

# Test JS/TS analysis (if Node.js installed)
python ~/.claude/skills/pact-code-analyzer/scripts/complexity_analyzer.py \
  --file path/to/javascript-file.js
# Output will show "analysis_method": "nodejs_ast" if Node.js is working
```

## Quick Reference Summary

| Script | Purpose | Key Arguments | Output |
|--------|---------|---------------|--------|
| **complexity_analyzer.py** | Cyclomatic complexity | --file/--directory, --threshold | Complexity per function |
| **dependency_mapper.py** | Dependency graph | --directory, --language, --detect-circular | Module dependencies, cycles |
| **coupling_detector.py** | Module coupling | --directory, --threshold, --show-details | Fan-in/fan-out metrics |
| **file_metrics.py** | File statistics | --file/--directory, --language | LOC, functions, PACT compliance |

### Language Support Matrix

| Script | Python | JavaScript | TypeScript | Notes |
|--------|--------|------------|------------|-------|
| **complexity_analyzer.py** | ✅ Full (AST) | ✅ Full (AST)* | ⚠️ Regex | *JS uses Node.js+acorn when available; TS uses regex fallback |
| **dependency_mapper.py** | ✅ Full | ✅ Full | ✅ Full | Path aliases (e.g., `@/components`) not resolved |
| **coupling_detector.py** | ✅ Full | ❌ Not supported | ❌ Not supported | Python-only; uses simplified dependency analysis |
| **file_metrics.py** | ✅ Full | ✅ Full | ✅ Full | Comment detection may miss edge cases |

**Legend**: ✅ Full support (AST-based) | ⚠️ Best-effort (regex-based) | ❌ Not supported

\* JavaScript complexity uses Node.js AST parsing via `acorn` when `npm install` has been run, with automatic regex fallback for .ts/.tsx files or when Node.js is unavailable.

**Common Thresholds**:
- Complexity: 10 (warn), 15 (critical)
- Coupling: 10 (warn), 15 (critical)
- File size: 600 lines (PACT limit)

**All scripts**:
- Output JSON by default
- Include error arrays for partial results
- Enforce security (path validation, size limits, timeouts)
- Return exit code 0 on success, 1 on error
