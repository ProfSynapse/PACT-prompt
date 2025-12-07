# Example: Test Coverage Prioritization

## Scenario

**Context**: Legacy Python API with 45% test coverage. New CTO mandates 80% coverage within 3 months.

**Goals**:
1. Identify high-risk code requiring test coverage
2. Prioritize test writing efforts for maximum risk reduction
3. Estimate test effort and create realistic timeline
4. Track progress toward 80% coverage goal

**Team**:
- 2 developers (can dedicate 50% time to testing)
- Existing test infrastructure in place (pytest, fixtures, mocks)

**Constraints**:
- Cannot pause feature development
- Limited time: 3 months = ~120 dev-hours for testing
- Must focus on highest-risk code first

## Initial State

**Codebase**:
- 127 Python files in src/
- ~15,000 lines of code
- Current coverage: 45% (measured via pytest-cov)
- Some modules have 0% coverage, others have 90%+

**Known Issues**:
- Production bugs often traced to uncovered edge cases
- Complex validation logic has caused customer-facing errors
- Refactoring is scary due to lack of regression tests

## Analysis Step 1: Measure Complexity Across Codebase

**Goal**: Identify complex functions that are high risk if untested.

**Command**:
```bash
python ~/.claude/skills/pact-code-analyzer/scripts/complexity_analyzer.py \
  --directory src/ \
  --threshold 8 \
  --output-format json > complexity-baseline.json
```

**Output Summary**:
```json
{
  "summary": {
    "total_files": 127,
    "total_functions": 892,
    "average_complexity": 4.7,
    "files_exceeding_threshold": 23,
    "functions_exceeding_threshold": 87
  }
}
```

**Key Finding**: 87 functions with complexity > 8

**High-Complexity Modules** (top 10):
```json
{
  "high_complexity_files": [
    {
      "path": "src/services/order_processing.py",
      "total_complexity": 156,
      "average_complexity": 9.8,
      "max_complexity": 18,
      "functions_exceeding_threshold": 12
    },
    {
      "path": "src/services/payment_validator.py",
      "total_complexity": 134,
      "average_complexity": 8.9,
      "max_complexity": 16,
      "functions_exceeding_threshold": 9
    },
    {
      "path": "src/utils/validation.py",
      "total_complexity": 98,
      "average_complexity": 7.3,
      "max_complexity": 14,
      "functions_exceeding_threshold": 7
    },
    {
      "path": "src/api/order_controller.py",
      "total_complexity": 87,
      "average_complexity": 6.2,
      "max_complexity": 12,
      "functions_exceeding_threshold": 5
    },
    {
      "path": "src/services/inventory_sync.py",
      "total_complexity": 76,
      "average_complexity": 8.4,
      "max_complexity": 15,
      "functions_exceeding_threshold": 6
    }
  ]
}
```

**Interpretation**:
- **order_processing.py**: 12 complex functions, max complexity 18 (critical)
- **payment_validator.py**: 9 complex functions, max complexity 16 (high risk)
- **validation.py**: 7 complex functions (shared utility - high fan-in expected)

## Analysis Step 2: Identify High-Coupling Modules

**Goal**: Find modules with high coupling (many dependents = high impact if buggy).

**Command**:
```bash
python ~/.claude/skills/pact-code-analyzer/scripts/coupling_detector.py \
  --directory src/ \
  --threshold 10 \
  --show-details > coupling-baseline.json
```

**Output** (excerpt):
```json
{
  "summary": {
    "total_modules": 127,
    "average_coupling": 5.8,
    "tightly_coupled_modules": 14
  },
  "modules": [
    {
      "path": "src/utils/validation.py",
      "outgoing_dependencies": 2,
      "incoming_dependencies": 34,
      "total_coupling": 36,
      "fan_in": [
        "src/api/order_controller.py",
        "src/api/user_controller.py",
        "... (32 more modules)"
      ]
    },
    {
      "path": "src/services/order_processing.py",
      "outgoing_dependencies": 11,
      "incoming_dependencies": 8,
      "total_coupling": 19,
      "fan_in": [
        "src/api/order_controller.py",
        "src/tasks/order_processor.py",
        "src/webhooks/payment_webhook.py",
        "... (5 more modules)"
      ]
    },
    {
      "path": "src/services/payment_validator.py",
      "outgoing_dependencies": 6,
      "incoming_dependencies": 12,
      "total_coupling": 18,
      "fan_in": [
        "src/services/order_processing.py",
        "src/api/payment_controller.py",
        "... (10 more modules)"
      ]
    }
  ]
}
```

**Key Findings**:

| Module | Fan-In | Impact if Buggy |
|--------|--------|-----------------|
| validation.py | 34 | 🚨 Critical - affects 34 modules |
| payment_validator.py | 12 | 🔴 High - affects 12 modules |
| order_processing.py | 8 | 🟡 Medium - affects 8 modules |

**Interpretation**:
- **validation.py**: 34 modules depend on it - bugs have widespread impact
- **payment_validator.py**: 12 dependents, handles money (critical business logic)
- **order_processing.py**: 8 dependents, core business flow

## Analysis Step 3: Get Current Test Coverage

**Goal**: Identify coverage gaps for high-complexity/high-coupling modules.

**Command**:
```bash
# Generate coverage report with pytest-cov
pytest --cov=src --cov-report=json --cov-report=term-missing

# Extract coverage data for high-priority modules
python -c "
import json
with open('coverage.json') as f:
    data = json.load(f)

priority_files = [
    'src/utils/validation.py',
    'src/services/payment_validator.py',
    'src/services/order_processing.py',
    'src/services/inventory_sync.py',
    'src/api/order_controller.py'
]

for filepath in priority_files:
    info = data['files'].get(filepath, {})
    covered = info.get('summary', {}).get('covered_lines', 0)
    total = info.get('summary', {}).get('num_statements', 0)
    pct = (covered / total * 100) if total > 0 else 0
    print(f'{filepath}: {pct:.1f}% ({covered}/{total} lines)')
"
```

**Output**:
```
src/utils/validation.py: 23% (45/196 lines)
src/services/payment_validator.py: 12% (18/150 lines)
src/services/order_processing.py: 8% (14/175 lines)
src/services/inventory_sync.py: 0% (0/132 lines)
src/api/order_controller.py: 67% (89/133 lines)
```

**Interpretation**:
- **inventory_sync.py**: 0% coverage (untested!)
- **order_processing.py**: 8% coverage (critical business logic barely tested)
- **payment_validator.py**: 12% coverage (money handling with no tests!)
- **validation.py**: 23% coverage (shared utility, low coverage)

## Step 4: Create Risk-Based Priority Matrix

**Goal**: Combine complexity, coupling, and coverage into single priority score.

**Priority Formula**:
```
Risk Score = (Complexity Weight × Max Complexity) +
             (Coupling Weight × Fan-In) +
             (Coverage Weight × (100 - Coverage%))

Weights:
- Complexity: 1.0 (high complexity = harder to test, more bugs)
- Coupling: 0.5 (high fan-in = more impact if buggy)
- Coverage: 0.3 (low coverage = gap in safety net)
```

**Priority Matrix**:

| Module | Max Complexity | Fan-In | Coverage | Risk Score | Priority |
|--------|----------------|--------|----------|------------|----------|
| **order_processing.py** | 18 × 1.0 = 18 | 8 × 0.5 = 4 | (100-8) × 0.3 = 27.6 | **49.6** | **P0** |
| **payment_validator.py** | 16 × 1.0 = 16 | 12 × 0.5 = 6 | (100-12) × 0.3 = 26.4 | **48.4** | **P0** |
| **inventory_sync.py** | 15 × 1.0 = 15 | 4 × 0.5 = 2 | (100-0) × 0.3 = 30 | **47.0** | **P0** |
| **validation.py** | 14 × 1.0 = 14 | 34 × 0.5 = 17 | (100-23) × 0.3 = 23.1 | **54.1** | **P0** |
| **order_controller.py** | 12 × 1.0 = 12 | 3 × 0.5 = 1.5 | (100-67) × 0.3 = 9.9 | **23.4** | **P1** |

**Sorted by Risk** (highest first):

1. **validation.py** (54.1) - P0: Complexity 14, Fan-in 34, Coverage 23%
2. **order_processing.py** (49.6) - P0: Complexity 18, Fan-in 8, Coverage 8%
3. **payment_validator.py** (48.4) - P0: Complexity 16, Fan-in 12, Coverage 12%
4. **inventory_sync.py** (47.0) - P0: Complexity 15, Fan-in 4, Coverage 0%
5. **order_controller.py** (23.4) - P1: Complexity 12, Fan-in 3, Coverage 67%

## Step 5: Estimate Test Effort

**Goal**: Estimate hours needed to reach 80% coverage for each module.

**Effort Estimation Formula**:
```
Hours = (Target Coverage% - Current Coverage%) × Lines of Code × Effort Factor

Effort Factors:
- Complexity 1-5: 0.01 hours/line (simple code, easy tests)
- Complexity 6-10: 0.02 hours/line (moderate code, setup needed)
- Complexity 11-15: 0.04 hours/line (complex code, many test cases)
- Complexity 16+: 0.06 hours/line (very complex, extensive mocking)
```

**Effort Estimates**:

| Module | Lines | Current Cov | Target Cov | Gap% | Avg Complexity | Effort Factor | Hours |
|--------|-------|-------------|------------|------|----------------|---------------|-------|
| validation.py | 196 | 23% | 80% | 57% | 7.3 | 0.02 | **22.3** |
| order_processing.py | 175 | 8% | 80% | 72% | 9.8 | 0.02 | **25.2** |
| payment_validator.py | 150 | 12% | 80% | 68% | 8.9 | 0.02 | **20.4** |
| inventory_sync.py | 132 | 0% | 80% | 80% | 8.4 | 0.02 | **21.1** |
| order_controller.py | 133 | 67% | 80% | 13% | 6.2 | 0.02 | **3.5** |

**Total Effort**: 92.5 hours (for top 5 modules)

**Available Capacity**: 2 developers × 50% time × 12 weeks = ~120 hours

**Conclusion**: We have enough capacity to cover top 5 modules + some additional lower-priority modules.

## Step 6: Create Phased Test Writing Plan

### Phase 1: Critical Business Logic (Weeks 1-4, ~48 hours)

**Goal**: Cover payment and order processing (money + core business flow).

**Modules**:
1. **payment_validator.py** (20.4 hours)
   - Week 1-2: Write unit tests for all 9 high-complexity functions
   - Focus: Edge cases in payment validation (expired cards, insufficient funds, fraud checks)
   - Target: 80% coverage

2. **order_processing.py** (25.2 hours)
   - Week 2-4: Write unit + integration tests for 12 complex functions
   - Focus: State transitions, error handling, rollback scenarios
   - Target: 80% coverage

**Success Criteria**:
- Zero production payment errors during period
- All order processing edge cases tested
- Coverage: payment_validator 12% → 80%, order_processing 8% → 80%

**Validation**:
```bash
# After Phase 1, re-check coverage
pytest --cov=src/services/payment_validator.py --cov-report=term-missing
pytest --cov=src/services/order_processing.py --cov-report=term-missing

# Target: Both at 80%+
```

### Phase 2: Shared Utilities (Weeks 5-7, ~22 hours)

**Goal**: Cover validation.py (high fan-in = affects 34 modules).

**Module**:
1. **validation.py** (22.3 hours)
   - Week 5-7: Write tests for 7 high-complexity validation functions
   - Focus: Boundary conditions, malformed inputs, internationalization
   - Target: 80% coverage

**Why this order**:
- Phases 1-2 covered, safe to refactor validation.py if needed
- High fan-in means bugs affect many modules - need safety net

**Success Criteria**:
- All validation edge cases tested
- Confidence to refactor validation logic if needed
- Coverage: validation 23% → 80%

**Validation**:
```bash
pytest --cov=src/utils/validation.py --cov-report=term-missing
# Target: 80%+
```

### Phase 3: Background Jobs (Weeks 8-10, ~21 hours)

**Goal**: Cover inventory_sync.py (0% coverage, causes production issues).

**Module**:
1. **inventory_sync.py** (21.1 hours)
   - Week 8-10: Write integration tests for sync workflows
   - Focus: API failures, partial syncs, data consistency
   - Target: 80% coverage

**Why this order**:
- Less critical than payment/orders (can tolerate some bugs)
- Background job (doesn't directly affect customer-facing flows)
- Complex integration testing (needs time)

**Success Criteria**:
- All sync failure scenarios tested
- Monitoring/alerts validated
- Coverage: inventory_sync 0% → 80%

### Phase 4: Controllers and Lower Priority (Weeks 11-12, ~8 hours)

**Goal**: Fill coverage gaps in remaining modules.

**Modules**:
1. **order_controller.py** (3.5 hours)
   - Fill gaps: 67% → 80% (mostly error handling)

2. **Other modules** (~4.5 hours)
   - Low-hanging fruit: Simple modules with 50-70% coverage
   - Push to 80% with minimal effort

**Success Criteria**:
- Overall codebase coverage: 45% → 80%+
- All critical paths tested
- Regression test suite in place

## Step 7: Track Progress

**Weekly Metrics**:
```bash
# Run every Friday
pytest --cov=src --cov-report=term-missing --cov-report=json

# Track metrics in spreadsheet
Week | Overall Coverage | payment_validator | order_processing | validation | inventory_sync
1    | 47%              | 25%              | 15%              | 23%        | 0%
2    | 52%              | 45%              | 28%              | 23%        | 0%
3    | 58%              | 68%              | 45%              | 23%        | 0%
4    | 64%              | 82%              | 78%              | 23%        | 0%
5    | 68%              | 82%              | 78%              | 42%        | 0%
6    | 72%              | 82%              | 78%              | 61%        | 0%
7    | 76%              | 82%              | 78%              | 80%        | 0%
8    | 77%              | 82%              | 78%              | 80%        | 15%
9    | 78%              | 82%              | 78%              | 80%        | 45%
10   | 79%              | 82%              | 78%              | 80%        | 75%
11   | 81%              | 82%              | 78%              | 80%        | 82%
12   | 82%              | 82%              | 78%              | 80%        | 82%
```

**Re-run Complexity Analysis**:
```bash
# After tests written, may refactor complex functions
# Track if complexity decreases (side benefit of testing)
python ~/.claude/skills/pact-code-analyzer/scripts/complexity_analyzer.py \
  --directory src/ \
  --threshold 8 \
  --output-format json > complexity-week12.json

# Compare with baseline
# Did complexity decrease? (Tests enable safe refactoring)
```

## Outcome

### Coverage Results (After 12 weeks)

**Overall Coverage**: 45% → 82% (goal: 80%, exceeded!)

**High-Priority Modules**:
- ✅ payment_validator.py: 12% → 82% (+70%)
- ✅ order_processing.py: 8% → 78% (+70%)
- ✅ validation.py: 23% → 80% (+57%)
- ✅ inventory_sync.py: 0% → 82% (+82%)
- ✅ order_controller.py: 67% → 81% (+14%)

### Side Benefits

**Bugs Found During Test Writing**:
- 3 critical bugs in payment_validator.py (edge cases never tested)
- 2 data consistency bugs in inventory_sync.py
- 1 race condition in order_processing.py

**Complexity Reduction** (unexpected benefit):
- Writing tests revealed overly complex functions
- Refactored during test writing (tests made refactoring safe)
- Average complexity: 4.7 → 4.1 (12% reduction)

**Developer Confidence**:
- Team now comfortable refactoring critical code
- Feature velocity actually INCREASED (less production debugging)
- Code review process faster (tests validate behavior)

## Lessons Learned

### What Worked

1. **Risk-based prioritization**: Focusing on high-complexity + high-coupling modules first reduced production bugs fastest
2. **Objective metrics**: Complexity and coupling data prevented bike-shedding about what to test
3. **Phased approach**: Critical business logic first meant early wins (payment bugs found in Week 2)
4. **Effort estimation**: Formula was accurate (92.5 estimated vs 89 actual hours)

### What Could Be Improved

1. **Integration test estimates**: Underestimated inventory_sync.py (complex integration testing)
2. **Flaky test handling**: Should have budgeted time for fixing flaky tests
3. **Test maintenance**: Didn't account for updating tests when features changed

### Recommendations

1. **Always combine metrics**: Complexity + Coupling + Coverage gives complete picture
2. **Business logic first**: Payment/order processing tests had highest ROI
3. **Update estimates weekly**: Effort estimation formula is starting point, adjust based on actuals
4. **Celebrate milestones**: Hit 80% in Week 11 (ahead of schedule), team morale boost!

## Test Effort Estimation Guidelines

Based on this project, refined effort estimation:

| Avg Complexity | Test Type | Hours per 10% Coverage Gain | Notes |
|----------------|-----------|------------------------------|-------|
| 1-5 | Unit tests | 0.5-1 hour | Simple functions, straightforward tests |
| 6-10 | Unit + integration | 1-2 hours | Moderate complexity, some mocking needed |
| 11-15 | Unit + integration + edge | 2-4 hours | High complexity, extensive test cases |
| 16+ | Comprehensive suite | 4-6 hours | Very complex, may need refactoring first |

**Integration Test Multiplier**: 1.5-2× (external dependencies, setup overhead)

**Adjustment Factors**:
- Existing test infrastructure: -20% (fixtures, mocks already available)
- Greenfield tests: +30% (no patterns established)
- Legacy code without dependency injection: +50% (hard to mock)
- Well-documented code: -20% (easier to understand expected behavior)

## Related Examples

- **pre-refactoring-analysis.md**: Combining complexity + coupling for refactoring decisions
- **references/complexity-calculation.md**: Understanding complexity scores for test case estimation
- **references/coupling-metrics.md**: Fan-in interpretation for prioritizing shared utilities
