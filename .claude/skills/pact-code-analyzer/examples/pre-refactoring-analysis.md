# Example: Pre-Refactoring Analysis

## Scenario

**Context**: E-commerce monolith with 6-person team planning to extract inventory management into separate microservice.

**Goals**:
1. Assess complexity and coupling of inventory-related modules
2. Identify circular dependencies that must be broken
3. Estimate refactoring effort and risk
4. Create phased migration plan

**Timeline**: 3-month refactoring project

**Constraints**:
- Must maintain 99.9% uptime during migration
- Cannot break existing API contracts
- Limited to 2 developers dedicated to refactoring

## Initial State

**Codebase Structure**:
```
src/
├── api/
│   ├── inventory_controller.py
│   ├── product_controller.py
│   └── order_controller.py
├── services/
│   ├── inventory_service.py
│   ├── product_service.py
│   ├── order_service.py
│   └── notification_service.py
├── models/
│   ├── inventory.py
│   ├── product.py
│   └── order.py
└── repositories/
    ├── inventory_repository.py
    ├── product_repository.py
    └── order_repository.py
```

**Known Issues**:
- Inventory logic scattered across multiple modules
- Suspected circular dependencies between services
- Some functions have complexity warnings in code reviews

## Analysis Step 1: Identify Complex Code

**Goal**: Find high-complexity functions that will be difficult to refactor.

**Command**:
```bash
python ~/.claude/skills/pact-code-analyzer/scripts/complexity_analyzer.py \
  --directory src/services/ \
  --threshold 10 \
  --output-format json > complexity-report.json
```

**Output** (excerpt):
```json
{
  "summary": {
    "total_files": 4,
    "total_functions": 67,
    "average_complexity": 5.3,
    "files_exceeding_threshold": 2,
    "functions_exceeding_threshold": 8
  },
  "files": [
    {
      "path": "src/services/inventory_service.py",
      "language": "python",
      "analysis_method": "python_ast",
      "total_complexity": 142,
      "average_complexity": 7.1,
      "functions": [
        {
          "name": "update_stock_levels",
          "line": 45,
          "complexity": 15,
          "exceeds_threshold": true,
          "recommendation": "Consider breaking into smaller functions"
        },
        {
          "name": "process_inventory_adjustment",
          "line": 89,
          "complexity": 12,
          "exceeds_threshold": true
        },
        {
          "name": "check_reorder_points",
          "line": 134,
          "complexity": 11,
          "exceeds_threshold": true
        }
      ]
    },
    {
      "path": "src/services/order_service.py",
      "language": "python",
      "total_complexity": 98,
      "average_complexity": 6.5,
      "functions": [
        {
          "name": "reserve_inventory",
          "line": 67,
          "complexity": 13,
          "exceeds_threshold": true
        },
        {
          "name": "release_inventory_on_cancellation",
          "line": 102,
          "complexity": 10,
          "exceeds_threshold": false
        }
      ]
    }
  ]
}
```

**Interpretation**:

| Module | High-Complexity Functions | Max Complexity | Risk Level |
|--------|---------------------------|----------------|------------|
| inventory_service.py | 3 | 15 | 🔴 High |
| order_service.py | 1 | 13 | 🟡 Medium |
| product_service.py | 0 | 8 | 🟢 Low |
| notification_service.py | 0 | 6 | 🟢 Low |

**Key Findings**:
- **inventory_service.py**: 3 functions with complexity 11-15
  - `update_stock_levels` (15): Critical path, needs careful testing
  - `process_inventory_adjustment` (12): Business logic heavy
  - `check_reorder_points` (11): Multiple conditional branches
- **order_service.py**: 1 function with complexity 13
  - `reserve_inventory` (13): Cross-service coordination, high risk

**Decision**: Refactor high-complexity functions BEFORE extracting to microservice to reduce risk.

## Analysis Step 2: Detect Circular Dependencies

**Goal**: Identify circular dependencies that will block microservice extraction.

**Command**:
```bash
python ~/.claude/skills/pact-code-analyzer/scripts/dependency_mapper.py \
  --directory src/ \
  --language python \
  --detect-circular \
  --output-graph json > dependency-report.json
```

**Output** (excerpt):
```json
{
  "summary": {
    "total_modules": 28,
    "total_dependencies": 94,
    "circular_dependencies": 3,
    "orphan_modules": 1,
    "max_depth": 5
  },
  "circular_dependencies": [
    {
      "cycle": [
        "src/services/inventory_service.py",
        "src/services/order_service.py",
        "src/services/inventory_service.py"
      ],
      "severity": "high",
      "length": 2
    },
    {
      "cycle": [
        "src/models/inventory.py",
        "src/models/product.py",
        "src/models/inventory.py"
      ],
      "severity": "medium",
      "length": 2
    },
    {
      "cycle": [
        "src/api/inventory_controller.py",
        "src/services/inventory_service.py",
        "src/services/notification_service.py",
        "src/api/inventory_controller.py"
      ],
      "severity": "low",
      "length": 3
    }
  ],
  "orphan_modules": [
    "src/utils/legacy_inventory_helper.py"
  ]
}
```

**Interpretation**:

**Critical Cycle** (Must fix before extraction):
```
inventory_service.py ←→ order_service.py
```
- **Problem**: Services depend on each other, cannot cleanly separate
- **Impact**: Blocking issue for microservice extraction
- **Root cause investigation needed**: Why does inventory_service import order_service?

**Model Cycle** (Moderate priority):
```
inventory.py ←→ product.py
```
- **Problem**: Models reference each other
- **Likely cause**: Bidirectional relationship in ORM
- **Fix**: Use forward references or split models

**Controller Cycle** (Low priority):
```
inventory_controller → inventory_service → notification_service → inventory_controller
```
- **Problem**: Notification service shouldn't know about controllers
- **Fix**: Use events instead of direct controller import

**Decision**: Break inventory_service ↔ order_service cycle FIRST (blocking), then address model cycle.

## Analysis Step 3: Measure Module Coupling

**Goal**: Understand how tightly inventory modules are coupled to rest of system.

**Command**:
```bash
python ~/.claude/skills/pact-code-analyzer/scripts/coupling_detector.py \
  --directory src/services/ \
  --threshold 10 \
  --show-details > coupling-report.json
```

**Output** (excerpt):
```json
{
  "summary": {
    "total_modules": 12,
    "average_coupling": 7.4,
    "tightly_coupled_modules": 3,
    "coupling_threshold": 10,
    "top_coupled_modules": [
      {"path": "src/services/inventory_service.py", "coupling": 22},
      {"path": "src/services/order_service.py", "coupling": 18},
      {"path": "src/services/product_service.py", "coupling": 14}
    ]
  },
  "modules": [
    {
      "path": "src/services/inventory_service.py",
      "outgoing_dependencies": 9,
      "incoming_dependencies": 13,
      "total_coupling": 22,
      "exceeds_threshold": true,
      "fan_out": [
        "src/models/inventory.py",
        "src/models/product.py",
        "src/repositories/inventory_repository.py",
        "src/repositories/product_repository.py",
        "src/services/order_service.py",
        "src/services/notification_service.py",
        "src/utils/validation.py",
        "src/utils/date_utils.py",
        "src/config/settings.py"
      ],
      "fan_in": [
        "src/api/inventory_controller.py",
        "src/api/product_controller.py",
        "src/api/order_controller.py",
        "src/services/order_service.py",
        "src/services/product_service.py",
        "src/services/reporting_service.py",
        "src/services/analytics_service.py",
        "src/tasks/inventory_sync.py",
        "src/tasks/reorder_check.py",
        "src/tasks/stock_alert.py",
        "src/tasks/inventory_report.py",
        "src/workers/inventory_worker.py",
        "src/admin/inventory_admin.py"
      ],
      "recommendation": "High coupling (22 total). Consider splitting into smaller services or using events to decouple."
    },
    {
      "path": "src/services/order_service.py",
      "outgoing_dependencies": 8,
      "incoming_dependencies": 10,
      "total_coupling": 18,
      "exceeds_threshold": true,
      "fan_out": [
        "src/models/order.py",
        "src/models/inventory.py",
        "src/repositories/order_repository.py",
        "src/services/inventory_service.py",
        "src/services/payment_service.py",
        "src/services/notification_service.py",
        "src/utils/validation.py",
        "src/config/settings.py"
      ],
      "fan_in": [
        "src/api/order_controller.py",
        "src/api/cart_controller.py",
        "src/services/inventory_service.py",
        "src/services/shipping_service.py",
        "src/tasks/order_processor.py",
        "src/tasks/abandoned_cart.py",
        "src/workers/order_worker.py",
        "src/admin/order_admin.py",
        "src/webhooks/payment_webhook.py",
        "src/webhooks/shipping_webhook.py"
      ]
    }
  ]
}
```

**Interpretation**:

**inventory_service.py** (Coupling = 22):
- **Fan-In (13)**: 🚨 Very high - 13 modules depend on this service
  - 3 API controllers
  - 5 background tasks
  - 2 workers
  - 2 other services
  - 1 admin module
- **Fan-Out (9)**: 🟡 High - depends on 9 other modules
- **Pattern**: God Object (high fan-in AND high fan-out)

**Impact Assessment**:
- **13 modules will break** if inventory_service API changes
- Extracting to microservice requires updating 13 import sites
- High risk of regression bugs during refactoring

**order_service.py** (Coupling = 18):
- **Fan-In (10)**: 🟡 High - 10 modules depend on this service
- **Fan-Out (8)**: 🟡 High - depends on 8 other modules
- **Key dependency**: `inventory_service` (creates circular dependency)

**Decision**:
1. Break circular dependency by introducing events
2. Create stable inventory_service API before extraction
3. Plan for gradual migration (13 import sites one at a time)

## Analysis Step 4: Combine Metrics into Risk Matrix

**Goal**: Prioritize modules for refactoring based on complexity + coupling.

**Risk Matrix**:

| Module | Complexity | Coupling | Circular Deps | Risk Score | Priority |
|--------|------------|----------|---------------|------------|----------|
| inventory_service.py | 🔴 15 (max) | 🔴 22 | ✅ Yes (order_service) | **10/10** | P0 - Critical |
| order_service.py | 🟡 13 (max) | 🟡 18 | ✅ Yes (inventory_service) | **8/10** | P1 - High |
| product_service.py | 🟢 8 (max) | 🟡 14 | ❌ No | **5/10** | P2 - Medium |
| notification_service.py | 🟢 6 (max) | 🟢 7 | ⚠️ Yes (controller) | **3/10** | P3 - Low |

**Risk Scoring** (1-10):
- Complexity: 15+ = 4 points, 11-14 = 3 points, 8-10 = 2 points, <8 = 1 point
- Coupling: 20+ = 4 points, 15-19 = 3 points, 10-14 = 2 points, <10 = 1 point
- Circular Dep: Yes = 2 points, No = 0 points

## Decisions and Refactoring Plan

### Phase 1: Break Circular Dependencies (Weeks 1-2)

**Goal**: Eliminate blocking circular dependencies.

**Tasks**:
1. **Investigate inventory_service → order_service dependency**
   - Found: `inventory_service` calls `order_service.get_pending_orders()` in reorder logic
   - **Fix**: Use event-driven approach instead

   ```python
   # BEFORE: Direct import (creates cycle)
   from src.services.order_service import OrderService

   def check_reorder_points(self):
       pending = OrderService().get_pending_orders()  # Circular!

   # AFTER: Event-driven (no import)
   def check_reorder_points(self):
       event = InventoryLowEvent(product_id=..., quantity=...)
       self.event_bus.publish(event)
   ```

2. **Break inventory.py ↔ product.py model cycle**
   - Use forward references in type hints
   - Separate into inventory_core.py and product_core.py

**Validation**:
```bash
# Re-run dependency mapper after changes
python ~/.claude/skills/pact-code-analyzer/scripts/dependency_mapper.py \
  --directory src/ \
  --language python \
  --detect-circular
# Expected: 0 circular dependencies in inventory-related modules
```

### Phase 2: Reduce Complexity (Weeks 3-4)

**Goal**: Refactor high-complexity functions before extraction.

**Tasks**:
1. **Refactor `update_stock_levels` (complexity 15 → target 8)**
   - Extract validation logic to separate function
   - Extract notification logic to event handlers
   - Extract audit logging to separate function

   ```python
   # BEFORE: Complexity 15
   def update_stock_levels(self, updates):
       # 15 decision points mixed together

   # AFTER: Complexity 5 each (total 15, but separated)
   def validate_stock_updates(self, updates):  # Complexity 5
       pass

   def apply_stock_updates(self, updates):  # Complexity 5
       pass

   def publish_stock_change_events(self, changes):  # Complexity 5
       pass
   ```

2. **Refactor `reserve_inventory` (complexity 13 → target 8)**
   - Extract reservation validation
   - Simplify error handling with early returns

**Validation**:
```bash
# Re-run complexity analyzer after refactoring
python ~/.claude/skills/pact-code-analyzer/scripts/complexity_analyzer.py \
  --file src/services/inventory_service.py \
  --threshold 10
# Expected: 0 functions exceeding threshold
```

### Phase 3: Reduce Coupling (Weeks 5-6)

**Goal**: Reduce fan-in/fan-out to enable clean extraction.

**Tasks**:
1. **Reduce fan-out (9 → target 5)**
   - Dependency injection for repositories
   - Event bus for notifications
   - Remove direct service-to-service calls

   ```python
   # BEFORE: Fan-out 9 (direct imports)
   from src.services.order_service import OrderService
   from src.services.notification_service import NotificationService

   # AFTER: Fan-out 3 (inject dependencies)
   class InventoryService:
       def __init__(
           self,
           inventory_repo: IInventoryRepository,
           event_bus: IEventBus
       ):
           # Inject, don't import
   ```

2. **Prepare for fan-in migration (13 → gradual reduction)**
   - Create stable inventory_service API contract
   - Document all public methods
   - Add deprecation warnings for methods that will move

**Validation**:
```bash
# Re-run coupling detector
python ~/.claude/skills/pact-code-analyzer/scripts/coupling_detector.py \
  --directory src/services/ \
  --threshold 10 \
  --show-details
# Target: total_coupling < 10 for inventory_service
```

### Phase 4: Extract Microservice (Weeks 7-10)

**Goal**: Move inventory logic to separate service.

**Tasks**:
1. Create new inventory-service repository
2. Copy refactored inventory_service code
3. Implement REST API matching internal API contract
4. Migrate 13 import sites one-by-one:
   - Week 7: Controllers (3 modules)
   - Week 8: Background tasks (5 modules)
   - Week 9: Workers and admin (3 modules)
   - Week 10: Other services (2 modules), deprecate old service

**Validation per migration**:
```bash
# After each module migration, verify no new coupling
python ~/.claude/skills/pact-code-analyzer/scripts/coupling_detector.py \
  --directory src/services/ \
  --show-details
# Monitor: inventory_service fan-in should decrease each week
```

### Phase 5: Testing and Validation (Weeks 11-12)

**Goal**: Ensure refactoring maintained correctness.

**Tasks**:
1. Run full integration test suite
2. Performance testing (ensure latency acceptable with HTTP calls)
3. Gradual traffic migration (10% → 50% → 100%)
4. Monitoring and rollback plan

## Outcome Metrics

**Before Refactoring**:
- inventory_service.py:
  - Max complexity: 15
  - Total coupling: 22
  - Circular dependencies: 1 (blocking)
  - Test coverage: 68%

**After Refactoring** (Target):
- inventory-service (microservice):
  - Max complexity: 8
  - Total coupling: 5
  - Circular dependencies: 0
  - Test coverage: 85%
  - Independent deployment ✅

**Success Criteria**:
- ✅ Zero circular dependencies
- ✅ All functions complexity < 10
- ✅ Total coupling < 10
- ✅ 13 import sites successfully migrated
- ✅ Zero production incidents during migration
- ✅ API latency < 100ms (p95)

## Lessons Learned

### What Worked Well

1. **Metrics-driven approach**: Objective data prevented emotional/political refactoring decisions
2. **Phased plan**: Breaking cycle first prevented wasted effort on impossible extraction
3. **Complexity reduction first**: Made testing easier, reduced migration risk
4. **Coupling tracking**: Fan-in metric showed exactly which modules needed migration

### What Could Be Improved

1. **Earlier analysis**: Should have run these scripts BEFORE estimating 3 months (took 4 months)
2. **Test coverage baseline**: Should have measured test coverage alongside complexity
3. **Performance baseline**: Didn't measure internal call latency before adding HTTP overhead

### Recommendations for Similar Projects

1. **Always run all three scripts** (complexity + coupling + dependencies) together
2. **Create risk matrix** combining all metrics, don't optimize one metric in isolation
3. **Break cycles first** - they are blocking issues for any architectural change
4. **Reduce complexity before extraction** - complex code is hard to test and migrate
5. **Track metrics throughout** - re-run scripts weekly to ensure progress

## Related Examples

- **test-prioritization.md**: How to use complexity metrics to prioritize test coverage (we should have done this first!)
- **references/coupling-metrics.md**: Deep dive on interpreting fan-in/fan-out
- **references/complexity-calculation.md**: Understanding complexity scores
