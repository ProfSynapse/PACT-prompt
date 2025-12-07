# Coupling Metrics Calculation

**Reference Guide for coupling_detector.py**

## Overview

Coupling metrics measure the degree of interdependence between modules in a software system. The coupling_detector.py script analyzes module dependencies to calculate fan-in and fan-out metrics, helping identify architectural risks and refactoring opportunities.

## What is Module Coupling?

**Module coupling** refers to the degree to which modules depend on each other. High coupling indicates:
- Modules are tightly interconnected
- Changes to one module often require changes to dependent modules
- Testing becomes difficult due to extensive mocking/stubbing needs
- System is fragile and hard to refactor

**Low coupling** (desirable) indicates:
- Modules are independent and self-contained
- Changes are isolated to specific modules
- Testing is straightforward with minimal dependencies
- System is flexible and easy to modify

## Fan-In and Fan-Out Concepts

### Fan-In (Incoming Dependencies)

**Fan-in** counts how many other modules import/depend on a given module.

**What it measures**:
- Reusability: High fan-in means many modules use this functionality
- Centrality: Module is a central component in the architecture
- Risk: Changes to this module affect many other modules

**Example**:
```
Module: src/utils/validation.py

Fan-In = 5 (imported by these modules):
  - src/api/users.py
  - src/api/posts.py
  - src/services/auth_service.py
  - src/services/user_service.py
  - src/services/post_service.py
```

**Interpretation**:
- **High fan-in (10+)**: This module is a dependency hub
  - **Positive**: Code reuse, shared functionality
  - **Negative**: Changes are risky (affect many modules)
  - **Action**: Ensure stability, comprehensive testing, clear API

- **Low fan-in (0-2)**: This module is rarely used
  - **Positive**: Changes have limited impact
  - **Negative**: May indicate dead code or over-specialization
  - **Action**: Consider if module is still needed

### Fan-Out (Outgoing Dependencies)

**Fan-out** counts how many other modules a given module imports/depends on.

**What it measures**:
- Complexity: High fan-out means module coordinates many components
- Fragility: Module depends on many other modules
- Testing difficulty: Many dependencies to mock in tests

**Example**:
```
Module: src/services/user_service.py

Fan-Out = 8 (imports these modules):
  - src/models/user.py
  - src/models/profile.py
  - src/repositories/user_repository.py
  - src/repositories/profile_repository.py
  - src/utils/validation.py
  - src/utils/email.py
  - src/services/auth_service.py
  - src/services/notification_service.py
```

**Interpretation**:
- **High fan-out (10+)**: This module has many dependencies
  - **Negative**: Fragile (breaks if any dependency changes)
  - **Negative**: Hard to test (many mocks needed)
  - **Negative**: Violates Single Responsibility Principle
  - **Action**: Refactor using dependency injection, facades, or events

- **Low fan-out (0-3)**: This module is self-contained
  - **Positive**: Easy to test and maintain
  - **Positive**: Clear, focused responsibility
  - **Action**: Maintain this pattern

## Coupling Metrics Calculation

The coupling_detector.py script calculates three key metrics per module:

### 1. Fan-In Calculation

**Algorithm**:
1. Parse all import statements in the codebase
2. Build a dependency graph: `{source_module: [target_modules]}`
3. Reverse the graph to count incoming dependencies
4. For each module, count how many modules import it

**Formula**:
```
Fan-In(Module) = Count of modules that import this module
```

### 2. Fan-Out Calculation

**Algorithm**:
1. For each module, count its import statements
2. Resolve imports to actual files in the project
3. Exclude external dependencies (e.g., node_modules, standard library)

**Formula**:
```
Fan-Out(Module) = Count of modules this module imports
```

### 3. Total Coupling

**Formula**:
```
Total Coupling = Fan-In + Fan-Out
```

**Why both matter**:
- Total coupling gives overall dependency burden
- High total coupling (>10) indicates architectural hotspot
- Combination of fan-in and fan-out reveals coupling pattern

## Coupling Metrics Output

The script outputs JSON with per-module metrics:

```json
{
  "modules": [
    {
      "path": "src/services/user_service.py",
      "outgoing_dependencies": 8,
      "incoming_dependencies": 12,
      "total_coupling": 20,
      "exceeds_threshold": true,
      "fan_out": [
        "src/models/user.py",
        "src/repositories/user_repository.py"
      ],
      "fan_in": [
        "src/api/users.py",
        "src/api/auth.py"
      ],
      "recommendation": "High coupling (20 dependencies). Consider splitting into smaller services or using events to decouple."
    }
  ]
}
```

## Interpretation Guidelines

### Threshold Recommendations

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| **Fan-In** | 8+ | 12+ | Review stability, add tests, document API |
| **Fan-Out** | 8+ | 12+ | Refactor with dependency injection, events |
| **Total Coupling** | 10+ | 15+ | Architectural refactoring required |

**Default threshold**: 10 (configurable via `--threshold` argument)

### Coupling Health Matrix

| Fan-In | Fan-Out | Total | Pattern | Interpretation |
|--------|---------|-------|---------|----------------|
| High (10+) | Low (0-3) | 10-15 | **Utility/Library Module** | ✅ Often acceptable - shared utilities |
| Low (0-3) | High (10+) | 10-15 | **Controller/Orchestrator** | ⚠️ Review - may violate SRP |
| High (10+) | High (10+) | 20+ | **God Object** | 🚨 Critical - refactor immediately |
| Low (0-3) | Low (0-3) | 0-6 | **Isolated Module** | ✅ Good - focused responsibility |
| 0 | 0 | 0 | **Orphan Module** | 🔍 Investigate - dead code? |

### What High Fan-In Means

**Scenario**: Module has fan-in of 15

**Implications**:
- This module is a **central dependency** in your architecture
- **15 other modules** will break if this module's interface changes
- Module is likely providing **core, shared functionality**

**Risk Assessment**:
- **High risk**: Any bug or breaking change affects 15 modules
- **High value**: Code reuse is good (DRY principle)

**Recommendations**:
1. **Stability**: Lock down the API, avoid breaking changes
2. **Testing**: Ensure 95%+ test coverage with comprehensive edge cases
3. **Documentation**: Clearly document all public interfaces
4. **Versioning**: Consider semantic versioning if module evolves
5. **Deprecation**: Use deprecation warnings before removing features

**When high fan-in is acceptable**:
- Utility modules (e.g., validation, logging, date formatting)
- Core domain models
- Shared configuration modules
- Stable, well-tested infrastructure components

**When to refactor**:
- Fan-in > 15 AND module is unstable/changing frequently
- Module does too many things (violates SRP)
- Fan-in modules use only subset of functionality (interface segregation violation)

### What High Fan-Out Means

**Scenario**: Module has fan-out of 12

**Implications**:
- This module **depends on 12 other modules**
- Module is **fragile**: Changes to any dependency may break it
- Module is likely an **orchestrator or controller**

**Risk Assessment**:
- **Testing difficulty**: Requires mocking 12 dependencies
- **Fragility**: 12 potential breakage points
- **Violates SRP**: Module probably does too much

**Recommendations**:
1. **Dependency Injection**: Pass dependencies as parameters, not direct imports
2. **Facades**: Group related dependencies behind single interface
3. **Events**: Replace direct dependencies with event-driven communication
4. **Split Module**: Break into smaller, focused modules

**When high fan-out is acceptable**:
- Application entry points (main.py, app.py) that wire up dependencies
- Configuration modules that import many settings
- Test files that need to import production code

**When to refactor**:
- Fan-out > 10 in domain logic or services
- Module orchestrates complex workflows
- Dependencies are tightly coupled (not just imported)

## Coupling Patterns

### Pattern 1: God Object (High Fan-In + High Fan-Out)

**Metrics**:
```json
{
  "path": "src/services/user_service.py",
  "incoming_dependencies": 15,
  "outgoing_dependencies": 12,
  "total_coupling": 27
}
```

**Problem**:
- Module is central to many flows AND depends on many others
- Likely violates Single Responsibility Principle
- Testing is nightmare (mock 12 deps, verify 15 dependents still work)

**Refactoring Strategy**:
1. **Identify Responsibilities**: What does this module actually do?
2. **Split by Concern**: Create separate modules for each responsibility
3. **Reduce Fan-Out**: Use dependency injection, facades, or events
4. **Stabilize Interfaces**: Lock down APIs for high fan-in modules

**Example Refactoring**:
```
BEFORE: user_service.py (fan-in: 15, fan-out: 12)
  - Handles user CRUD
  - Sends notifications
  - Manages permissions
  - Updates profiles

AFTER:
  - user_repository.py (fan-in: 8, fan-out: 2) - CRUD only
  - notification_service.py (fan-in: 5, fan-out: 3) - Notifications
  - permission_manager.py (fan-in: 7, fan-out: 2) - Permissions
  - profile_service.py (fan-in: 4, fan-out: 3) - Profiles
```

### Pattern 2: Utility Module (High Fan-In, Low Fan-Out)

**Metrics**:
```json
{
  "path": "src/utils/validation.py",
  "incoming_dependencies": 12,
  "outgoing_dependencies": 2,
  "total_coupling": 14
}
```

**Assessment**:
- **Often acceptable**: Shared utility is exactly what we want
- High fan-in reflects good code reuse
- Low fan-out means module is self-contained

**When to refactor**:
- Module does unrelated things (e.g., validation + email + logging)
- Interface is too large (violates Interface Segregation)

**Refactoring Strategy**:
```
BEFORE: utils/validation.py (fan-in: 12, fan-out: 2)
  - Email validation
  - Phone validation
  - Credit card validation
  - Password strength

AFTER (if clients use only subsets):
  - utils/email_validation.py (fan-in: 4, fan-out: 1)
  - utils/phone_validation.py (fan-in: 3, fan-out: 1)
  - utils/payment_validation.py (fan-in: 2, fan-out: 1)
  - utils/auth_validation.py (fan-in: 3, fan-out: 1)
```

### Pattern 3: Controller/Orchestrator (Low Fan-In, High Fan-Out)

**Metrics**:
```json
{
  "path": "src/api/user_controller.py",
  "incoming_dependencies": 2,
  "outgoing_dependencies": 10,
  "total_coupling": 12
}
```

**Assessment**:
- Typical for API controllers or workflow orchestrators
- High fan-out is expected (controller coordinates services)

**When to refactor**:
- Fan-out > 15 (too many direct dependencies)
- Controller contains business logic (should delegate to services)

**Refactoring Strategy**:
```
BEFORE: user_controller.py (fan-out: 10)
  - Imports 10 services directly
  - Orchestrates complex workflows inline

AFTER:
  - user_controller.py (fan-out: 3)
    - Imports user_service_facade
    - Delegates to facade
  - user_service_facade.py (fan-out: 10)
    - Encapsulates the 10 service dependencies
    - Provides simplified interface
```

### Pattern 4: Orphan Module (Zero Fan-In and Fan-Out)

**Metrics**:
```json
{
  "path": "src/utils/deprecated_helper.py",
  "incoming_dependencies": 0,
  "outgoing_dependencies": 0,
  "total_coupling": 0
}
```

**Implications**:
- Module is not imported by anything (fan-in = 0)
- Module imports nothing (fan-out = 0)
- Likely **dead code**

**Action**:
1. Search codebase for dynamic imports (e.g., `__import__`, `importlib`)
2. Check if module is entry point (e.g., CLI script)
3. If truly unused, **delete it**

**Exceptions**:
- Entry point scripts (main.py, cli.py)
- Standalone utilities meant to be run directly
- Documentation examples

## Refactoring Strategies

### Strategy 1: Reducing Fan-Out via Dependency Injection

**Before** (Fan-Out = 8):
```python
# src/services/order_service.py
from src.repositories.order_repository import OrderRepository
from src.repositories.user_repository import UserRepository
from src.services.payment_service import PaymentService
from src.services.notification_service import NotificationService
from src.utils.validation import validate_order
from src.utils.email import send_email
from src.models.order import Order
from src.models.user import User

class OrderService:
    def __init__(self):
        self.order_repo = OrderRepository()
        self.user_repo = UserRepository()
        self.payment = PaymentService()
        self.notification = NotificationService()

    def create_order(self, order_data):
        # Use all 8 dependencies
        pass
```

**After** (Fan-Out = 3):
```python
# src/services/order_service.py
from src.models.order import Order
from src.models.user import User
from typing import Protocol

# Define interfaces, inject implementations
class IOrderRepository(Protocol):
    def save(self, order: Order) -> None: ...

class IPaymentService(Protocol):
    def process(self, amount: float) -> bool: ...

class INotificationService(Protocol):
    def send(self, user: User, message: str) -> None: ...

class OrderService:
    def __init__(
        self,
        order_repo: IOrderRepository,
        user_repo: IUserRepository,
        payment: IPaymentService,
        notification: INotificationService
    ):
        self.order_repo = order_repo
        self.user_repo = user_repo
        self.payment = payment
        self.notification = notification

    def create_order(self, order_data):
        # Dependencies injected, not imported
        pass
```

**Benefits**:
- Fan-out reduced from 8 to 3 (only import interfaces/models)
- Testing easier (inject mocks)
- Flexible (swap implementations without changing code)

### Strategy 2: Reducing Fan-In by Splitting Responsibilities

**Before** (Fan-In = 15):
```python
# src/models/user.py (imported by 15 modules)
class User:
    # User data
    id: int
    email: str
    password_hash: str

    # Profile data
    display_name: str
    avatar_url: str
    bio: str

    # Preferences
    theme: str
    notifications_enabled: bool

    # Admin data
    is_admin: bool
    permissions: List[str]

    # Session data
    last_login: datetime
    session_token: str
```

**After** (Split into 4 modules with fan-in 4-5 each):
```python
# src/models/user.py (fan-in: 8)
class User:
    id: int
    email: str
    password_hash: str

# src/models/user_profile.py (fan-in: 4)
class UserProfile:
    user_id: int
    display_name: str
    avatar_url: str
    bio: str

# src/models/user_preferences.py (fan-in: 2)
class UserPreferences:
    user_id: int
    theme: str
    notifications_enabled: bool

# src/models/user_permissions.py (fan-in: 3)
class UserPermissions:
    user_id: int
    is_admin: bool
    permissions: List[str]
```

**Benefits**:
- Each module has single responsibility
- Modules depend only on what they need (Interface Segregation)
- Changes to profile don't affect permissions

### Strategy 3: Using Events to Decouple

**Before** (Fan-Out = 10):
```python
# src/services/user_service.py
from src.services.notification_service import NotificationService
from src.services.analytics_service import AnalyticsService
from src.services.email_service import EmailService
from src.services.audit_service import AuditService
# ... 6 more imports

class UserService:
    def create_user(self, user_data):
        user = self.user_repo.create(user_data)

        # Notify 10 different services
        NotificationService().notify_new_user(user)
        AnalyticsService().track_signup(user)
        EmailService().send_welcome(user)
        AuditService().log_user_creation(user)
        # ... 6 more direct calls
```

**After** (Fan-Out = 2):
```python
# src/services/user_service.py
from src.events.event_bus import EventBus
from src.events.user_events import UserCreatedEvent

class UserService:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    def create_user(self, user_data):
        user = self.user_repo.create(user_data)

        # Publish event instead of calling services
        event = UserCreatedEvent(user)
        self.event_bus.publish(event)
```

```python
# Subscribers register themselves (in their own modules)
# src/services/notification_service.py
class NotificationService:
    def __init__(self, event_bus):
        event_bus.subscribe(UserCreatedEvent, self.on_user_created)

    def on_user_created(self, event):
        self.notify_new_user(event.user)
```

**Benefits**:
- UserService fan-out reduced from 10 to 2
- Services are decoupled (can add/remove without changing UserService)
- Event-driven architecture enables async processing

### Strategy 4: Using Facades to Manage Complexity

**Before** (Fan-Out = 12):
```python
# src/api/order_controller.py
from src.services.order_service import OrderService
from src.services.user_service import UserService
from src.services.inventory_service import InventoryService
from src.services.payment_service import PaymentService
from src.services.shipping_service import ShippingService
from src.services.notification_service import NotificationService
# ... 6 more imports

class OrderController:
    def create_order(self, request):
        # Orchestrate 12 services
        user = UserService().get_user(request.user_id)
        inventory = InventoryService().check_availability(request.items)
        payment = PaymentService().process(request.payment_info)
        # ... many more calls
```

**After** (Fan-Out = 2):
```python
# src/api/order_controller.py
from src.facades.order_facade import OrderFacade

class OrderController:
    def __init__(self, order_facade: OrderFacade):
        self.order_facade = order_facade

    def create_order(self, request):
        # Delegate complexity to facade
        result = self.order_facade.create_order(request)
        return result
```

```python
# src/facades/order_facade.py (encapsulates 12 services)
class OrderFacade:
    def __init__(
        self,
        order_service,
        user_service,
        inventory_service,
        # ... all 12 services injected
    ):
        self.order_service = order_service
        # ...

    def create_order(self, request):
        # Orchestrate the 12 services
        # Controller doesn't need to know the details
        pass
```

**Benefits**:
- Controller fan-out reduced from 12 to 2
- Facade provides simplified interface
- Complexity isolated in dedicated module

## Relationship to Other Metrics

### Coupling vs Complexity

**Different concerns**:
- **Coupling**: How many modules depend on each other (architectural)
- **Complexity**: How many decision points in a function (algorithmic)

**Relationship**:
- High coupling often leads to high complexity (orchestrating many dependencies)
- Low coupling enables low complexity (focused, simple modules)

**Example**:
```python
# High coupling (fan-out: 8), moderate complexity (complexity: 6)
def process_order(order):
    user = UserService().get_user(order.user_id)  # +dependency
    if not InventoryService().has_stock(order.items):  # +dependency, +complexity
        return False
    if not PaymentService().charge(user, order.total):  # +dependency, +complexity
        return False
    # ... 5 more dependencies
```

### Coupling vs Cohesion

**Inverse relationship**:
- **High coupling + Low cohesion**: Module does many unrelated things, depends on many modules (BAD)
- **Low coupling + High cohesion**: Module does one thing well, minimal dependencies (GOOD)

**Coupling metrics help identify low cohesion**:
- If module has high fan-out AND high fan-in, likely lacks cohesion
- If fan-in modules only use subset of functionality, cohesion is low

### When High Coupling is Acceptable

**Acceptable scenarios**:
1. **Application Entry Points**: Main files, server startup scripts
2. **Test Files**: Need to import production code
3. **Configuration Modules**: Import many settings to aggregate
4. **Stable Utility Modules**: High fan-in is desirable for shared utilities

**Key distinction**: Is the coupling **stable** or **volatile**?
- **Stable coupling**: Dependencies rarely change (e.g., standard library, mature utilities)
- **Volatile coupling**: Dependencies change frequently (e.g., internal services still evolving)

Volatile coupling with high fan-in is **high risk**.

## Practical Workflow Examples

### Example 1: Pre-Refactoring Risk Assessment

**Scenario**: Planning to refactor authentication module.

**Steps**:
1. Run coupling detector on authentication module
2. Check fan-in to assess impact radius
3. Check fan-out to understand dependencies

```bash
python ~/.claude/skills/pact-code-analyzer/scripts/coupling_detector.py \
  --directory src/services/ \
  --threshold 10 \
  --show-details
```

**Output**:
```json
{
  "modules": [
    {
      "path": "src/services/auth_service.py",
      "incoming_dependencies": 14,
      "outgoing_dependencies": 6,
      "total_coupling": 20,
      "exceeds_threshold": true,
      "fan_in": ["src/api/auth.py", "src/api/users.py", ...],
      "recommendation": "High coupling (20). Consider splitting..."
    }
  ]
}
```

**Interpretation**:
- Fan-in of 14: **High risk** - changes affect 14 modules
- Fan-out of 6: Moderate complexity
- **Action**: Create comprehensive test suite before refactoring, plan for gradual migration with backward compatibility

### Example 2: Identifying Architectural Hotspots

**Scenario**: Want to understand which modules are architectural bottlenecks.

**Steps**:
1. Run coupling detector across entire codebase
2. Sort by total_coupling descending
3. Focus on top 5-10 highest coupling modules

**Decision Matrix**:

| Module | Fan-In | Fan-Out | Total | Pattern | Action |
|--------|--------|---------|-------|---------|--------|
| user_service.py | 15 | 12 | 27 | God Object | 🚨 Split immediately |
| validation.py | 12 | 2 | 14 | Utility | ✅ Acceptable, add tests |
| order_controller.py | 3 | 11 | 14 | Controller | ⚠️ Add facade |
| notification_service.py | 8 | 7 | 15 | Balanced | ⚠️ Review responsibilities |

### Example 3: Pull Request Review

**Scenario**: Reviewing PR that adds new service module.

**Steps**:
1. Run coupling detector on new module
2. Check if coupling is reasonable for module type
3. Request changes if thresholds exceeded

**Example**:
```bash
# Analyze new module
python ~/.claude/skills/pact-code-analyzer/scripts/coupling_detector.py \
  --directory src/services/ \
  --threshold 10 \
  --show-details | grep "new_feature_service.py"
```

**Review Criteria**:
- New service with fan-out > 10: Request dependency injection refactor
- New service with fan-in > 0 before merging: Unexpected, investigate
- Total coupling > 15: Block merge, require architectural review

## Summary

Coupling metrics provide objective measures of module interdependence:

- **Fan-In**: Number of modules that import this module
  - High fan-in (10+) = Central component, changes are risky
  - Action: Stabilize, test thoroughly, document

- **Fan-Out**: Number of modules this module imports
  - High fan-out (10+) = Many dependencies, fragile
  - Action: Refactor with dependency injection, events, or facades

- **Total Coupling**: Fan-In + Fan-Out
  - Threshold: 10 (warn), 15 (critical)
  - High total coupling indicates architectural hotspot

**Use coupling metrics to**:
- Identify refactoring priorities (God Objects with fan-in 15+, fan-out 15+)
- Assess risk before refactoring (high fan-in = many affected modules)
- Guide architectural decisions (isolate volatile high-coupling modules)
- Prioritize testing (high fan-in modules need comprehensive tests)

**Key insight**: Not all coupling is bad. Stable, well-tested utility modules with high fan-in provide valuable code reuse. Focus refactoring efforts on volatile, high-coupling modules that lack cohesion.
