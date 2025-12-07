# Phase 5: pact-code-analyzer Skill Design Specification

**Status**: EXPERIMENTAL - Implementation Complete (Phases 1-3), Phase 4 Partial
**Created**: 2025-12-07
**Updated**: 2025-12-07
**Architect**: PACT Architect
**Phase**: Implementation Complete, Pending Real-World Validation

---

## Executive Summary

This document specifies the design for `pact-code-analyzer`, an experimental Claude Code Skill that provides executable Python scripts for automated code analysis. Unlike traditional skills that contain only reference knowledge, this skill includes executable code that agents can invoke via the Bash tool to perform computational analysis of codebases.

**Experimental Nature**: This skill explores a new capability for Claude Code Skills - executable code. The implementation will validate whether this approach provides sufficient value over Claude's native code reading and analysis capabilities.

**Key Design Decisions**:
1. **Executable Scripts**: Python scripts in `scripts/` directory, invoked via Bash tool
2. **Pre-installed Dependencies Only**: Use Python 3.11 standard library to avoid dependency management
3. **JSON Output Format**: All scripts output structured JSON for easy parsing by agents
4. **Read-Only Analysis**: Scripts analyze existing code without modification
5. **Security-First Design**: Input validation, sandboxing considerations, clear file access boundaries

---

## 1. Skill Overview

### 1.1 Purpose and Scope

**Purpose**: Provide computational code analysis capabilities that complement Claude's natural language understanding of code.

**In Scope**:
- Cyclomatic complexity calculation for Python, JavaScript, TypeScript files
- Module dependency mapping and circular dependency detection
- Coupling metrics between modules and files
- Basic file statistics (lines of code, function/class counts)
- Abstract syntax tree (AST) based analysis

**Out of Scope**:
- Code modification or refactoring (read-only analysis)
- Language-specific linting (use dedicated linters instead)
- Performance profiling or runtime analysis
- Binary file analysis or compiled code inspection

### 1.2 Target Users

**Primary Users**:
- **pact-architect**: Analyze existing codebase architecture before designing new components
- **pact-test-engineer**: Identify high-complexity functions requiring additional test coverage
- **pact-backend-coder**: Detect tight coupling before implementing new features
- **pact-frontend-coder**: Analyze component dependency graphs

**Secondary Users**:
- **PACT Orchestrator**: High-level codebase health assessment before delegating work

### 1.3 Value Proposition

**What computational analysis provides that native Claude reading doesn't**:

1. **Quantitative Metrics**: Precise complexity scores, coupling counts, LOC measurements
2. **Large-Scale Analysis**: Process entire directories faster than reading file-by-file
3. **Consistency**: Deterministic metrics across multiple analysis runs
4. **Graph Structures**: Dependency graphs difficult to construct from sequential file reading
5. **Threshold Detection**: Automatically flag files/functions exceeding complexity budgets

**When to use this skill vs. native reading**:
- **Use scripts**: When you need precise metrics, large-scale analysis, or dependency graphs
- **Use native reading**: When you need semantic understanding, architectural patterns, or code quality assessment

---

## 2. SKILL.md Structure

### 2.1 Frontmatter Configuration

```yaml
name: pact-code-analyzer
description: |
  ALL PHASES: Executable Python scripts for automated code analysis.

  Provides computational code analysis including cyclomatic complexity calculation,
  dependency mapping, coupling detection, and file statistics. Scripts output JSON
  for easy parsing and integration with agent workflows.

  Use when: analyzing codebase complexity, detecting circular dependencies,
  measuring coupling between modules, generating dependency graphs, identifying
  high-complexity functions requiring refactoring or testing.

  DO NOT use for: semantic code understanding, architectural pattern recognition,
  code quality assessment (use native reading for these). Scripts provide metrics,
  not insights.
allowed-tools:
  - Read
  - Bash
  - Grep
metadata:
  phase: "All"
  version: "0.1.0-experimental"
  status: "experimental"
  primary-agents: ["pact-architect", "pact-test-engineer", "pact-backend-coder", "pact-frontend-coder"]
  related-skills:
    - pact-architecture-patterns
    - pact-backend-patterns
    - pact-frontend-patterns
    - pact-testing-patterns
```

### 2.2 Core Content Structure

The SKILL.md body will include:

1. **Overview Section** (100-150 lines)
   - What computational analysis provides vs native reading
   - When to use scripts vs reading code directly
   - Security considerations and file access boundaries

2. **Quick Reference: Available Scripts** (150-200 lines)
   - Brief description of each script
   - Input/output format for each
   - Common invocation patterns
   - Example use cases

3. **Script Invocation Guide** (100-150 lines)
   - General invocation pattern via Bash tool
   - JSON output parsing examples
   - Error handling guidance
   - Performance considerations

4. **Common Workflows** (100-150 lines)
   - Pre-architecture codebase analysis
   - Identifying refactoring candidates
   - Test coverage prioritization
   - Dependency health assessment

5. **Reference Files Guide** (50-100 lines)
   - Detailed script documentation in references/
   - Algorithm explanations
   - Metric interpretation guidelines

**Total SKILL.md Target**: 500-750 lines

---

## 3. Script Specifications

### 3.1 Script 1: complexity_analyzer.py

**Purpose**: Calculate cyclomatic complexity for Python, JavaScript, and TypeScript files

**Inputs**:
- `--file <path>`: Analyze single file
- `--directory <path>`: Analyze all files in directory recursively
- `--threshold <int>`: Flag functions exceeding complexity threshold (default: 10)
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
          "name": "update_user_permissions",
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

**Implementation Approach**:
- **Python**: Use `ast` module to parse and analyze control flow
- **JavaScript/TypeScript**: Use simple regex-based parsing (control keywords: if, for, while, case, catch, &&, ||)
  - Note: Regex approach is less accurate than full AST but avoids external dependencies
  - Alternative: If esprima or similar is available, use proper AST parsing
- **Complexity Calculation**: Count decision points per function (if, for, while, case, logical operators)

**Dependencies**: Python 3.11 standard library only
- `ast` (Python AST parsing)
- `json` (output formatting)
- `argparse` (CLI argument parsing)
- `pathlib` (file path handling)
- `re` (JavaScript/TypeScript parsing)

**Security Considerations**:
- Validate file paths are within allowed directory boundaries
- Reject symbolic links to prevent directory traversal
- Limit file size (max 1MB per file to prevent memory issues)
- Timeout after 60 seconds to prevent infinite loops on malformed code

**Example Invocation**:
```bash
# Analyze single file
python ~/.claude/skills/pact-code-analyzer/scripts/complexity_analyzer.py \
  --file src/services/user_service.py \
  --threshold 10

# Analyze entire directory
python ~/.claude/skills/pact-code-analyzer/scripts/complexity_analyzer.py \
  --directory src/ \
  --threshold 8 \
  --output-format json
```

**Success Criteria**:
- Accurate complexity calculation matching established tools (within ±1 for 90% of functions)
- Handles syntax errors gracefully without crashing
- Processes 100-file codebase in under 30 seconds

---

### 3.2 Script 2: dependency_mapper.py

**Purpose**: Map import/require dependencies between files to detect circular dependencies and orphan modules

**Inputs**:
- `--directory <path>`: Root directory to analyze
- `--language <python|javascript|typescript>`: Language to analyze
- `--output-graph <dot|json>`: Output format (default: json)
- `--detect-circular`: Flag circular dependencies

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
      "imports": [
        "src/models/user.py",
        "src/utils/validation.py",
        "src/repositories/user_repository.py"
      ],
      "imported_by": [
        "src/api/users.py",
        "src/api/auth.py"
      ],
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
  "orphan_modules": [
    "src/utils/deprecated_helper.py"
  ]
}
```

**Implementation Approach**:
- **Python**: Parse `import` and `from ... import` statements using AST
- **JavaScript/TypeScript**: Parse `import`, `require()`, and `export` statements using regex
- **Graph Construction**: Build directed graph of module dependencies
- **Circular Detection**: Depth-first search (DFS) to detect cycles
- **Orphan Detection**: Find modules with zero `imported_by` references (excluding entry points)

**Dependencies**: Python 3.11 standard library only
- `ast` (Python import parsing)
- `json` (output formatting)
- `argparse` (CLI)
- `pathlib` (file handling)
- `re` (JavaScript/TypeScript parsing)

**Security Considerations**:
- Same as complexity_analyzer.py (path validation, size limits, timeouts)
- Handle missing files gracefully (imported modules may not exist in analyzed directory)

**Example Invocation**:
```bash
# Map Python dependencies
python ~/.claude/skills/pact-code-analyzer/scripts/dependency_mapper.py \
  --directory src/ \
  --language python \
  --detect-circular

# Generate dependency graph in DOT format (for visualization)
python ~/.claude/skills/pact-code-analyzer/scripts/dependency_mapper.py \
  --directory src/ \
  --language javascript \
  --output-graph dot > dependencies.dot
```

**Success Criteria**:
- Correctly identifies all import statements in supported languages
- Detects all circular dependencies (no false negatives)
- Low false positive rate for orphan modules (<5%)

---

### 3.3 Script 3: coupling_detector.py

**Purpose**: Detect tight coupling between modules by counting cross-module dependencies

**Inputs**:
- `--directory <path>`: Root directory to analyze
- `--threshold <int>`: Flag modules exceeding dependency count (default: 10)
- `--show-details`: Show which specific modules are coupled

**Output Format** (JSON):
```json
{
  "summary": {
    "total_modules": 42,
    "average_dependencies": 3.7,
    "tightly_coupled_modules": 5,
    "coupling_threshold": 10
  },
  "modules": [
    {
      "path": "src/services/user_service.py",
      "outgoing_dependencies": 8,
      "incoming_dependencies": 12,
      "total_coupling": 20,
      "exceeds_threshold": true,
      "fan_out": [
        "src/models/user.py",
        "src/repositories/user_repository.py",
        "src/services/auth_service.py",
        "src/utils/validation.py",
        "src/services/notification_service.py",
        "src/services/email_service.py",
        "src/config/settings.py",
        "src/utils/logging.py"
      ],
      "fan_in": [
        "src/api/users.py",
        "src/api/auth.py",
        "src/api/admin.py",
        "src/workers/user_sync.py",
        "src/workers/cleanup.py",
        "src/services/admin_service.py",
        "src/services/report_service.py",
        "src/tests/test_user_service.py",
        "src/tests/test_auth.py",
        "src/tests/integration/test_user_flow.py",
        "src/scripts/migrate_users.py",
        "src/scripts/seed_data.py"
      ],
      "recommendation": "High coupling (20 dependencies). Consider splitting into smaller services or using events to decouple."
    }
  ]
}
```

**Implementation Approach**:
- Reuses dependency mapping logic from `dependency_mapper.py`
- Calculates fan-out (dependencies this module has on others)
- Calculates fan-in (dependencies others have on this module)
- Total coupling = fan-out + fan-in
- Flags modules exceeding threshold
- Provides recommendations based on coupling patterns

**Dependencies**: Python 3.11 standard library only (same as dependency_mapper.py)

**Security Considerations**: Same as dependency_mapper.py

**Example Invocation**:
```bash
# Detect tightly coupled modules
python ~/.claude/skills/pact-code-analyzer/scripts/coupling_detector.py \
  --directory src/ \
  --threshold 15 \
  --show-details
```

**Success Criteria**:
- Accurately counts dependencies (validated against manual inspection)
- Provides actionable recommendations for decoupling
- Handles large codebases (500+ files) efficiently

---

### 3.4 Script 4: file_metrics.py

**Purpose**: Calculate basic file statistics (LOC, functions, classes, comments)

**Inputs**:
- `--file <path>`: Analyze single file
- `--directory <path>`: Analyze all files in directory
- `--language <python|javascript|typescript>`: Target language

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
    "average_file_size": 146
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

**Implementation Approach**:
- **Python**: Use `ast` module to count functions, classes
- **JavaScript/TypeScript**: Use regex to count function/class declarations
- **Line counting**: Simple line-by-line analysis
  - Code lines: Non-blank, non-comment lines
  - Comment lines: Lines starting with `#` (Python) or `//`, `/*` (JS/TS)
  - Blank lines: Empty or whitespace-only lines
- **PACT compliance check**: Flag files exceeding 600-line limit

**Dependencies**: Python 3.11 standard library only

**Security Considerations**: Same as complexity_analyzer.py

**Example Invocation**:
```bash
# Analyze single file metrics
python ~/.claude/skills/pact-code-analyzer/scripts/file_metrics.py \
  --file src/services/user_service.py \
  --language python

# Analyze entire directory
python ~/.claude/skills/pact-code-analyzer/scripts/file_metrics.py \
  --directory src/ \
  --language python
```

**Success Criteria**:
- Accurate line counts (matches `wc -l` for total lines)
- Correctly identifies functions and classes (within 95% accuracy)
- Fast execution (entire codebase in under 10 seconds)

---

## 4. Security Considerations

### 4.1 Input Validation

**File Path Validation**:
- Reject paths containing `..` (parent directory traversal)
- Reject absolute paths outside the current working directory
- Reject symbolic links (potential for escaping sandbox)
- Validate file extensions match expected languages

**Example validation code**:
```python
import os
from pathlib import Path

def validate_file_path(file_path: str, allowed_root: str) -> Path:
    """Validate file path is within allowed directory."""
    path = Path(file_path).resolve()
    root = Path(allowed_root).resolve()

    # Check if path is within allowed root
    try:
        path.relative_to(root)
    except ValueError:
        raise SecurityError(f"Path {file_path} is outside allowed directory {allowed_root}")

    # Reject symbolic links
    if path.is_symlink():
        raise SecurityError(f"Symbolic links not allowed: {file_path}")

    # Check file exists
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return path
```

### 4.2 Resource Limits

**File Size Limits**:
- Max individual file size: 1MB (prevent memory exhaustion)
- Max total analyzed size: 50MB (prevent long-running processes)
- Reject files larger than limits with clear error message

**Execution Timeouts**:
- Per-file timeout: 5 seconds
- Total script timeout: 60 seconds
- Use `signal.alarm()` on Unix systems for timeout enforcement

**Example timeout implementation**:
```python
import signal

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Script execution exceeded timeout")

# Set 60-second timeout
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(60)

try:
    # Run analysis
    analyze_codebase()
finally:
    signal.alarm(0)  # Cancel alarm
```

### 4.3 Sandboxing Considerations

**File System Access**:
- Scripts operate in read-only mode (no file writes except stdout)
- No network access required or allowed
- No subprocess execution (all analysis in-process)

**Code Execution**:
- Scripts parse code using AST, NOT `eval()` or `exec()`
- Never execute analyzed code
- Handle parsing errors gracefully without exposing internal state

### 4.4 Error Handling

**Graceful Degradation**:
- Syntax errors in analyzed code: Skip file and continue
- Malformed files: Log error and continue with remaining files
- Partial results: Return results for successfully analyzed files

**Error Output Format**:
```json
{
  "summary": { ... },
  "files": [ ... ],
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

---

## 5. Use Case Validation

### 5.1 Architecture Phase Use Cases

**Use Case 1: Pre-Architecture Complexity Assessment**

**Scenario**: Architect needs to understand existing codebase complexity before designing new features

**Workflow**:
1. pact-architect invoked for new feature design
2. Architect loads pact-code-analyzer skill
3. Runs complexity_analyzer.py on existing codebase
4. Identifies high-complexity modules (threshold > 10)
5. Designs new architecture to avoid adding to already complex areas
6. Documents complexity hotspots in architecture spec

**Value**: Quantitative data guides architectural decisions, preventing complexity accumulation

**Success Metric**: Architect references complexity metrics in 80%+ of architecture specs

---

**Use Case 2: Dependency Analysis Before Refactoring**

**Scenario**: Architect planning to split monolithic service into microservices

**Workflow**:
1. pact-architect analyzes current monolith structure
2. Runs dependency_mapper.py to generate module dependency graph
3. Identifies circular dependencies preventing clean separation
4. Runs coupling_detector.py to find tightly coupled modules
5. Designs microservice boundaries that minimize cross-service dependencies
6. Documents dependency refactoring plan in architecture spec

**Value**: Data-driven microservice boundary decisions reduce post-split coupling

**Success Metric**: Circular dependencies reduced by 50%+ in refactored architecture

---

### 5.2 Testing Phase Use Cases

**Use Case 3: Test Coverage Prioritization**

**Scenario**: Test engineer needs to prioritize which functions require additional test coverage

**Workflow**:
1. pact-test-engineer analyzing test coverage gaps
2. Runs complexity_analyzer.py to identify high-complexity functions
3. Compares complexity scores with existing test coverage data
4. Prioritizes writing tests for high-complexity, low-coverage functions
5. Documents testing priorities in test plan

**Value**: Focus testing effort on highest-risk code (complex, untested functions)

**Success Metric**: 90%+ of high-complexity functions (>10) achieve 80%+ coverage

---

**Use Case 4: Identifying Brittle Code**

**Scenario**: Test engineer wants to identify code likely to break during changes

**Workflow**:
1. Runs coupling_detector.py to find tightly coupled modules
2. Runs complexity_analyzer.py to find complex functions
3. Cross-references: high coupling + high complexity = brittle code
4. Recommends integration tests for brittle areas
5. Flags modules for refactoring consideration

**Value**: Proactive identification of technical debt and testing gaps

**Success Metric**: Brittle code (high coupling + complexity) covered by integration tests

---

### 5.3 Code Phase Use Cases

**Use Case 5: Pre-Implementation Dependency Check**

**Scenario**: Backend coder implementing new feature, wants to avoid introducing circular dependencies

**Workflow**:
1. pact-backend-coder planning new service implementation
2. Runs dependency_mapper.py to understand current dependency graph
3. Identifies potential circular dependency if new service imports existing module X
4. Designs implementation to avoid circular dependency (dependency injection, events)
5. Documents dependency design decision

**Value**: Prevent circular dependencies before they're introduced

**Success Metric**: Zero new circular dependencies introduced during implementation

---

### 5.4 Value vs. Native Reading

**When scripts provide clear value**:
- Large codebases (100+ files): Faster than reading file-by-file
- Quantitative analysis: Precise metrics for decision-making
- Graph structures: Dependency visualization difficult via reading
- Automated checks: Threshold detection (complexity > 10, coupling > 15)

**When native reading is superior**:
- Semantic understanding: "What does this code do?" requires comprehension
- Architectural patterns: Identifying design patterns requires context
- Code quality: Assessing naming, structure, maintainability requires judgment
- Small codebases: Reading 5-10 files is faster than running scripts

**Recommendation**: Use scripts for quantitative analysis; use reading for qualitative assessment. Combine both for comprehensive codebase understanding.

---

## 6. Dependencies and Environment

### 6.1 Python Version Requirement

**Target**: Python 3.11+
**Rationale**: Leverages modern AST features and pathlib improvements

**Verification**:
```python
import sys
if sys.version_info < (3, 11):
    print("Error: Python 3.11+ required")
    sys.exit(1)
```

### 6.2 Standard Library Dependencies

All scripts use **only** Python standard library modules:

- `ast`: Abstract syntax tree parsing (Python code)
- `json`: JSON output formatting
- `argparse`: Command-line argument parsing
- `pathlib`: Cross-platform file path handling
- `re`: Regular expression parsing (JavaScript/TypeScript)
- `sys`: System-specific parameters
- `os`: Operating system interfaces
- `signal`: Timeout handling (Unix systems)
- `typing`: Type annotations for code clarity

**No external dependencies required** - scripts work with fresh Python 3.11 installation.

### 6.3 Platform Considerations

**Supported Platforms**:
- macOS (primary target for Claude Code)
- Linux (common development environment)
- Windows (best-effort support via pathlib cross-platform paths)

**Platform-Specific Handling**:
- Use `pathlib.Path` for all file path operations (cross-platform)
- Timeout implementation: `signal.alarm()` on Unix, fallback to no timeout on Windows
- Line endings: Handle both `\n` (Unix) and `\r\n` (Windows) automatically

---

## 7. Reference Files Structure

### 7.1 references/ Directory

**references/complexity-calculation.md**: Deep dive into cyclomatic complexity
- Algorithm explanation (McCabe's cyclomatic complexity)
- Decision point counting methodology
- Language-specific nuances (Python vs JavaScript)
- Interpretation guidelines (what scores mean)
- Threshold recommendations by context

**references/dependency-analysis.md**: Dependency mapping algorithms
- Import statement parsing techniques
- Directed graph construction
- Circular dependency detection (DFS algorithm)
- Orphan module identification
- Visualization recommendations (DOT format, Graphviz)

**references/coupling-metrics.md**: Coupling measurement theory
- Fan-in vs fan-out definitions
- Coupling severity classification
- Decoupling strategies by pattern
- Common coupling anti-patterns

**references/script-integration.md**: Agent workflow integration
- How to invoke scripts from agent prompts
- Parsing JSON output for decision-making
- Combining multiple script outputs
- Error handling and fallback strategies

### 7.2 examples/ Directory

**examples/architecture-assessment.md**: Complete workflow example
- Pre-architecture codebase analysis
- Running all scripts in sequence
- Synthesizing results into architecture decisions
- Sample JSON outputs with interpretation

**examples/test-prioritization.md**: Testing workflow example
- Identifying high-complexity, low-coverage code
- Cross-referencing complexity with coverage reports
- Building test prioritization matrix

---

## 8. Testing and Validation Strategy

### 8.1 Script Unit Testing

**Test Data**:
- Create `scripts/tests/fixtures/` directory with sample code files
  - `simple.py`: Low complexity Python file (baseline)
  - `complex.py`: High complexity Python file (edge cases)
  - `circular_a.py`, `circular_b.py`: Circular dependency test
  - `simple.js`: JavaScript baseline
  - `malformed.py`: Syntax error handling test

**Test Script**: `scripts/tests/test_all_scripts.sh`
```bash
#!/bin/bash
# Test all scripts with fixture data

echo "Testing complexity_analyzer.py..."
python scripts/complexity_analyzer.py --file scripts/tests/fixtures/simple.py
python scripts/complexity_analyzer.py --file scripts/tests/fixtures/complex.py

echo "Testing dependency_mapper.py..."
python scripts/dependency_mapper.py --directory scripts/tests/fixtures/

echo "Testing coupling_detector.py..."
python scripts/coupling_detector.py --directory scripts/tests/fixtures/

echo "Testing file_metrics.py..."
python scripts/file_metrics.py --directory scripts/tests/fixtures/

echo "All tests passed!"
```

### 8.2 Validation Criteria

**Accuracy Validation**:
- Compare complexity scores with established tools (radon for Python, complexity-report for JS)
- Acceptable variance: ±1 complexity point for 90% of functions
- Dependency mapping: 100% accuracy for import detection (no missed imports)
- Coupling metrics: Manual validation on 20-file sample codebase

**Performance Validation**:
- 100-file codebase: Complete analysis in <30 seconds
- 500-file codebase: Complete analysis in <2 minutes
- Memory usage: <100MB for typical analysis

**Robustness Validation**:
- Syntax errors: Graceful degradation, partial results
- Missing files: Clear error messages, continue processing
- Large files: Reject gracefully with size limit message
- Timeouts: Enforced without crashes

### 8.3 Agent Integration Testing

**Test Scenarios**:

1. **pact-architect + pact-code-analyzer**
   - Task: "Analyze the complexity of the existing user service module"
   - Expected: Architect loads skill, runs complexity_analyzer.py, interprets results

2. **pact-test-engineer + pact-code-analyzer**
   - Task: "Identify functions that need more test coverage based on complexity"
   - Expected: Engineer runs complexity_analyzer.py, cross-references with coverage data

3. **Error Handling**
   - Task: "Analyze a directory with syntax errors"
   - Expected: Scripts return partial results with error details in JSON

**Success Criteria**:
- Agents correctly invoke scripts 100% of the time
- Agents parse JSON output and make decisions based on data
- Agents handle errors gracefully and provide user feedback

---

## 9. Implementation Roadmap

### Phase 1: Core Script Development (Week 1) ✅ COMPLETE

**Deliverables**:
- [x] `complexity_analyzer.py`: Python and JavaScript support
- [x] `dependency_mapper.py`: Python support
- [x] `file_metrics.py`: Python support
- [x] Basic error handling and input validation
- [x] JSON output formatting

**Validation**: Run on small test codebase (10-20 files) ✅

---

### Phase 2: Skill Integration (Week 2) ✅ COMPLETE

**Deliverables**:
- [x] `SKILL.md`: Complete skill definition with usage guide
- [x] `references/complexity-calculation.md`
- [x] `references/dependency-analysis.md`
- [x] `references/script-integration.md`
- [ ] Test fixtures in `scripts/tests/fixtures/` *(deferred)*

**Validation**: Manual testing with pact-architect agent ✅

---

### Phase 3: Robustness and Security (Week 3) ✅ COMPLETE

**Deliverables**:
- [x] Security hardening (path validation, timeouts, size limits)
- [x] Enhanced error handling (partial results, detailed error messages)
- [x] `coupling_detector.py`: Add as advanced feature
- [x] Performance optimization (target: 100 files in <30 seconds)

**Validation**: Agent integration testing with all scripts ✅

---

### Phase 4: Expansion and Refinement (Week 4) ⚠️ PARTIAL

**Deliverables**:
- [x] JavaScript/TypeScript support via Node.js AST analyzer (`js-complexity-analyzer.js`)
- [ ] DOT format output for dependency graphs *(not implemented)*
- [ ] Additional metrics (code churn, comment density) *(not implemented)*
- [ ] Examples in `examples/` directory *(deferred)*

**Validation**: Real-world usage on production codebase *(pending)*

---

### Phase 5: Evaluation and Decision (Week 5+)

**Evaluation Questions**:
1. Do agents actually use the scripts? (Track invocation frequency)
2. Do scripts provide value vs. native reading? (User feedback)
3. Are results accurate and actionable? (Validation against manual analysis)
4. Is maintenance burden acceptable? (Time spent fixing vs. value provided)

**Go/No-Go Decision Criteria**:
- **GO**: Agents use scripts in 50%+ of relevant tasks, user feedback positive, accuracy >90%
- **NO-GO**: Agents use scripts <25% of time, native reading faster/better, accuracy issues

**Outcomes**:
- **GO**: Promote to production, expand language support, add more analysis types
- **NO-GO**: Deprecate skill, document learnings, focus effort on proven skills

---

## 10. Success Metrics

### 10.1 Adoption Metrics

**Target Metrics**:
- Script invocation rate: 50%+ of architecture/testing tasks involving codebase analysis
- Agent adoption: 4+ agents use scripts regularly
- User feedback: 4.0+ / 5.0 satisfaction rating

**Tracking Approach**:
- Log script invocations (optional telemetry in scripts)
- User surveys after 1 month of availability
- GitHub issues tracking feedback and feature requests

### 10.2 Quality Metrics

**Accuracy Targets**:
- Complexity calculation: ±1 point for 90% of functions (validated against radon)
- Dependency detection: 100% recall (no missed imports)
- Coupling metrics: 95%+ accuracy (manual validation sample)

**Performance Targets**:
- 100 files: <30 seconds
- 500 files: <2 minutes
- Memory: <100MB

**Robustness Targets**:
- Error handling: 100% of scripts handle errors gracefully
- Partial results: Scripts return useful data even with some failures
- Security: Zero path traversal vulnerabilities

### 10.3 Value Metrics

**Quantitative Value**:
- Time saved: Scripts 5x faster than manual file-by-file reading for large codebases
- Consistency: 100% deterministic results (same input = same output)

**Qualitative Value**:
- Data-driven decisions: Architecture specs reference complexity metrics
- Proactive issue detection: Circular dependencies found before causing problems
- Test prioritization: High-complexity code receives appropriate test coverage

---

## 11. Risk Assessment and Mitigation

### 11.1 Technical Risks

**Risk 1: Inaccurate Complexity Calculation**
- **Impact**: High - Bad data leads to bad decisions
- **Likelihood**: Medium - Regex-based JS parsing is error-prone
- **Mitigation**:
  - Validate against established tools (radon, complexity-report)
  - Use proper AST parsing for Python (high accuracy)
  - Document accuracy limitations for JavaScript
  - Fallback: Recommend native reading for critical decisions

**Risk 2: Performance Issues on Large Codebases**
- **Impact**: Medium - Slow scripts frustrate users
- **Likelihood**: Medium - AST parsing can be slow
- **Mitigation**:
  - Implement timeouts to prevent infinite hangs
  - Profile and optimize hot paths
  - Add `--fast` mode with sampling for quick estimates
  - Document expected performance characteristics

**Risk 3: Security Vulnerabilities**
- **Impact**: High - Path traversal could expose sensitive files
- **Likelihood**: Low - Mitigations in place
- **Mitigation**:
  - Comprehensive path validation (reject `..`, symlinks)
  - File size limits to prevent DoS
  - No code execution (AST parsing only)
  - Security review before production release

### 11.2 Adoption Risks

**Risk 4: Agents Don't Use Scripts**
- **Impact**: High - Wasted effort if unused
- **Likelihood**: Medium - Native reading may be sufficient
- **Mitigation**:
  - Clear use case documentation in SKILL.md
  - Agent prompts include script invocation examples
  - User education: Blog post on when to use scripts
  - Monitor usage and adjust based on data

**Risk 5: Maintenance Burden**
- **Impact**: Medium - Outdated scripts provide bad data
- **Likelihood**: Medium - Languages evolve, new syntax added
- **Mitigation**:
  - Version skill as experimental (0.x) to set expectations
  - Document maintenance requirements upfront
  - Set deprecation criteria (if unused after 3 months)
  - Community contributions for language support expansion

### 11.3 User Experience Risks

**Risk 6: Confusing Output Format**
- **Impact**: Low - Users misinterpret results
- **Likelihood**: Medium - JSON can be verbose
- **Mitigation**:
  - Include `--output-format summary` for human-readable output
  - Examples in SKILL.md show how to parse JSON
  - Reference files explain metric interpretation
  - Agents provide user-friendly summaries of script output

---

## 12. Alternatives Considered

### 12.1 Alternative 1: Pure Reference Skill (No Executable Code)

**Approach**: Skill contains only reference documentation on complexity metrics, no scripts

**Pros**:
- Simpler to maintain (no code to update)
- No security concerns (read-only)
- Works without Bash tool access

**Cons**:
- No quantitative analysis (agents must calculate manually)
- Slower for large codebases (file-by-file reading)
- Inconsistent metrics (different agents may calculate differently)

**Decision**: REJECTED - The value proposition is precise, automated metrics. Without scripts, skill adds little over native reading.

---

### 12.2 Alternative 2: External Tool Integration (radon, eslint-complexity)

**Approach**: Skill documents how to invoke external tools via Bash, no custom scripts

**Pros**:
- Leverage proven, maintained tools
- Higher accuracy (battle-tested parsers)
- Broader language support

**Cons**:
- Dependency management burden on users
- Installation complexity (pip install, npm install)
- Different output formats require custom parsing
- Less control over features and output

**Decision**: DEFERRED - Consider for Phase 2 expansion if custom scripts prove insufficient. Start with standard library to minimize dependencies.

---

### 12.3 Alternative 3: Agent-Embedded Analysis (No Skill)

**Approach**: Agents contain analysis logic directly, no separate skill

**Pros**:
- No Bash tool required
- Faster invocation (no script loading)

**Cons**:
- Duplicated code across agents
- Harder to maintain (update all agents)
- Can't share improvements across agents
- Agents become bloated with analysis logic

**Decision**: REJECTED - Violates separation of concerns. Skills are the right abstraction for shared, reusable analysis capabilities.

---

## 13. Future Enhancements (Post-MVP)

### 13.1 Additional Metrics

**Code Churn Analysis**:
- Track files changed most frequently (via git log)
- Identify churn hotspots (high change frequency = instability)
- Cross-reference with complexity (high churn + high complexity = risk)

**Comment Density**:
- Calculate comment ratio (comment lines / code lines)
- Flag under-commented complex functions
- Identify over-commented simple code (possible code smell)

**Duplication Detection**:
- Identify duplicate code blocks (simple hash-based approach)
- Flag copy-paste code for refactoring
- Estimate % of codebase that's duplicated

### 13.2 Language Expansion

**Additional Languages**:
- Ruby: AST parsing via `ripper` (if available)
- Go: Regex-based parsing (simpler syntax than JS)
- Java: AST parsing (more complex, requires external parser)
- PHP: Regex-based parsing

**Language Priority**: Based on user demand and PACT user base language distribution

### 13.3 Visualization Support

**Dependency Graph Visualization**:
- Generate DOT format for Graphviz rendering
- Inline SVG generation for self-contained output
- Interactive HTML dependency viewer

**Complexity Heatmaps**:
- Generate HTML heatmap of codebase complexity
- Color-coded file tree (green = low, red = high)
- Drill-down to function-level complexity

### 13.4 Integration with Other Skills

**pact-testing-patterns Integration**:
- Export complexity data in format compatible with coverage tools
- Generate test prioritization matrix (complexity × coverage)

**pact-architecture-patterns Integration**:
- Detect architectural patterns via dependency structure
- Flag anti-patterns (god objects, circular dependencies)

---

## 14. Conclusion and Recommendations

### 14.1 Implementation Recommendation

**Recommendation**: PROCEED with Phase 1 implementation of pact-code-analyzer skill as experimental feature.

**Rationale**:
1. Clear value proposition: Quantitative metrics complement Claude's qualitative analysis
2. Low risk: Standard library only, read-only, well-defined scope
3. Validation path: 5-week phased implementation with Go/No-Go decision
4. Learning opportunity: Test executable code in skills pattern for future expansion

### 14.2 Success Criteria for Experiment

**Go Criteria** (Continue to production):
- Agent invocation rate >50% for relevant tasks
- Accuracy >90% compared to established tools
- User satisfaction rating >4.0/5.0
- Clear use cases where scripts outperform native reading

**No-Go Criteria** (Deprecate):
- Agent invocation rate <25%
- Accuracy issues persist despite fixes
- Native reading consistently faster/better
- High maintenance burden relative to value

### 14.3 Next Steps

1. **Review and Approve Design**: Stakeholder review of this specification
2. **Phase 1 Implementation**: Build core scripts (complexity, dependencies, metrics)
3. **Agent Integration Testing**: Validate with pact-architect and pact-test-engineer
4. **Security Review**: External security audit of path validation and sandboxing
5. **Phased Rollout**: Internal testing → Beta release → Evaluation → Decision

### 14.4 Documentation Deliverables

**For Implementers**:
- This design specification (complete)
- Script implementation guide (code structure, testing approach)
- Security checklist (path validation, timeouts, size limits)

**For Users**:
- SKILL.md (usage guide, invocation examples)
- Reference files (algorithm explanations, metric interpretation)
- Examples (complete workflows with sample outputs)

---

## Appendix A: Example Script Invocation from Agent

**Scenario**: pact-architect analyzing codebase before designing new feature

**Agent Workflow**:

```markdown
I'll analyze the existing codebase complexity to understand where to place the new feature.

First, let me run a complexity analysis on the services directory:

```bash
python ~/.claude/skills/pact-code-analyzer/scripts/complexity_analyzer.py \
  --directory src/services/ \
  --threshold 10 \
  --output-format json
```

[Script output shows 3 files exceeding complexity threshold]

Based on the analysis:
- `user_service.py`: Complexity 15 (exceeds threshold)
- `order_service.py`: Complexity 12 (exceeds threshold)
- `payment_service.py`: Complexity 8 (acceptable)

The new feature should be implemented as a separate service rather than adding to the already complex user_service. I'll design a new `notification_service` to keep complexity manageable.

Let me also check dependencies to ensure we don't create circular references:

```bash
python ~/.claude/skills/pact-code-analyzer/scripts/dependency_mapper.py \
  --directory src/services/ \
  --language python \
  --detect-circular
```

[Script output shows one existing circular dependency between user_service and auth_service]

Given the existing circular dependency, I'll design the notification_service with explicit interfaces to avoid adding to this problem...
```

---

## Appendix B: JSON Schema for Script Outputs

### complexity_analyzer.py Output Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["summary", "files"],
  "properties": {
    "summary": {
      "type": "object",
      "required": ["total_files", "total_functions", "average_complexity"],
      "properties": {
        "total_files": { "type": "integer" },
        "total_functions": { "type": "integer" },
        "average_complexity": { "type": "number" },
        "files_exceeding_threshold": { "type": "integer" },
        "functions_exceeding_threshold": { "type": "integer" }
      }
    },
    "files": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["path", "language", "total_complexity", "functions"],
        "properties": {
          "path": { "type": "string" },
          "language": { "type": "string", "enum": ["python", "javascript", "typescript"] },
          "total_complexity": { "type": "integer" },
          "average_complexity": { "type": "number" },
          "functions": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["name", "line", "complexity", "exceeds_threshold"],
              "properties": {
                "name": { "type": "string" },
                "line": { "type": "integer" },
                "complexity": { "type": "integer" },
                "exceeds_threshold": { "type": "boolean" },
                "recommendation": { "type": "string" }
              }
            }
          }
        }
      }
    },
    "errors": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "file": { "type": "string" },
          "error": { "type": "string" },
          "severity": { "type": "string", "enum": ["warning", "error"] },
          "action": { "type": "string" }
        }
      }
    }
  }
}
```

---

**Document Status**: IMPLEMENTATION COMPLETE (Phases 1-3), Phase 4 Partial
**Current State**: 4 Python scripts + 1 Node.js AST analyzer implemented, peer-reviewed, bug fixes applied
**Next Steps**: Real-world validation, optional test suite and examples
