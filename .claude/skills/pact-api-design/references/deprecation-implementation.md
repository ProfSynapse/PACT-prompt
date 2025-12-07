# API Deprecation Implementation

Technical implementation guide for deprecation headers, version lifecycle management, feature flags, and code annotations.

## Table of Contents

1. [HTTP Headers](#http-headers)
2. [Version Lifecycle States](#version-lifecycle-states)
3. [Code Annotations](#code-annotations)
4. [Feature Flags](#feature-flags)
5. [Complete Implementation Example](#complete-implementation-example)
6. [Quick Reference](#quick-reference)

## HTTP Headers

### Standard Headers

**Deprecation Header** (RFC Draft):
```
Deprecation: true
```

Indicates the resource is deprecated but still functional.

**Sunset Header** (RFC 8594):
```
Sunset: Sat, 01 Jun 2026 00:00:00 GMT
```

Indicates when the resource will become unavailable.

**Link Header**:
```
Link: </api/v2/users>; rel="successor-version"
Link: <https://api.example.com/docs/migration>; rel="deprecation"
```

Provides links to successor version and migration documentation.

### Complete Header Implementation

**TypeScript**:
```typescript
import { format } from 'date-fns';

function setDeprecationHeaders(
  res: Response,
  sunsetDate: Date,
  successorUrl: string,
  migrationGuideUrl: string
) {
  // Deprecation header
  res.set('Deprecation', 'true');

  // Sunset header (HTTP date format)
  const sunsetHttpDate = format(sunsetDate, 'EEE, dd MMM yyyy HH:mm:ss') + ' GMT';
  res.set('Sunset', sunsetHttpDate);

  // Link headers
  res.set('Link', [
    `<${successorUrl}>; rel="successor-version"`,
    `<${migrationGuideUrl}>; rel="deprecation"`
  ].join(', '));

  // Custom headers for machine-readable data
  res.set('X-API-Deprecation-Date', '2025-12-06T00:00:00Z');
  res.set('X-API-Sunset-Date', sunsetDate.toISOString());
  res.set('X-API-Removal-Date', sunsetDate.toISOString());
}

// Usage in route
app.get('/api/v1/users', (req, res) => {
  setDeprecationHeaders(
    res,
    new Date('2026-06-01T00:00:00Z'),
    '/api/v2/users',
    'https://api.example.com/docs/v1-to-v2'
  );

  const users = await getUsersV1();
  res.json(users);
});
```

**Python (FastAPI)**:
```python
from datetime import datetime
from email.utils import formatdate
from fastapi import Response

def set_deprecation_headers(
    response: Response,
    sunset_date: datetime,
    successor_url: str,
    migration_guide_url: str
):
    # Deprecation header
    response.headers['Deprecation'] = 'true'

    # Sunset header (HTTP date format)
    sunset_timestamp = sunset_date.timestamp()
    response.headers['Sunset'] = formatdate(sunset_timestamp, usegmt=True)

    # Link headers
    response.headers['Link'] = (
        f'<{successor_url}>; rel="successor-version", '
        f'<{migration_guide_url}>; rel="deprecation"'
    )

    # Custom headers
    response.headers['X-API-Deprecation-Date'] = '2025-12-06T00:00:00Z'
    response.headers['X-API-Sunset-Date'] = sunset_date.isoformat()
    response.headers['X-API-Removal-Date'] = sunset_date.isoformat()

# Usage
@app.get('/api/v1/users')
def get_users_v1(response: Response):
    set_deprecation_headers(
        response,
        datetime(2026, 6, 1),
        '/api/v2/users',
        'https://api.example.com/docs/v1-to-v2'
    )

    users = get_users_from_db()
    return users
```

### Client Detection of Deprecation

**TypeScript Client**:
```typescript
async function apiRequest(url: string): Promise<any> {
  const response = await fetch(url);

  // Check for deprecation
  if (response.headers.get('Deprecation') === 'true') {
    const sunsetDate = response.headers.get('Sunset');
    const successorLink = response.headers.get('Link')?.match(
      /<([^>]+)>; rel="successor-version"/
    )?.[1];

    console.warn(
      `⚠️ API endpoint ${url} is deprecated.`,
      `Sunset date: ${sunsetDate}`,
      `Migrate to: ${successorLink}`
    );

    // Optional: Track deprecation usage
    trackDeprecationUsage(url, sunsetDate);
  }

  return response.json();
}
```

**Python Client**:
```python
import requests
import logging

def api_request(url: str) -> dict:
    response = requests.get(url)

    # Check for deprecation
    if response.headers.get('Deprecation') == 'true':
        sunset_date = response.headers.get('Sunset')
        link_header = response.headers.get('Link', '')

        # Parse Link header for successor
        import re
        match = re.search(r'<([^>]+)>; rel="successor-version"', link_header)
        successor_url = match.group(1) if match else None

        logging.warning(
            f"⚠️ API endpoint {url} is deprecated. "
            f"Sunset date: {sunset_date}. "
            f"Migrate to: {successor_url}"
        )

        # Optional: Track deprecation usage
        track_deprecation_usage(url, sunset_date)

    return response.json()
```

## Version Lifecycle States

### State Definitions

| State | Description | Behavior |
|-------|-------------|----------|
| **Active** | Current, fully supported version | Full functionality, receives all updates |
| **Deprecated** | Discouraged but fully functional | Full functionality, only security updates |
| **Sunset** | End-of-life date announced | Read-only, no updates, removal pending |
| **Removed** | No longer available | Returns 410 Gone |

### State Transitions

```
Active → Deprecated → Sunset → Removed
   |         |           |         |
   |         |           |         └─ Returns 410 Gone
   |         |           └─ Read-only, removal date set
   |         └─ Deprecation warnings, migration encouraged
   └─ Full support
```

### Implementation with State Machine

**TypeScript**:
```typescript
enum APIVersionState {
  ACTIVE = 'active',
  DEPRECATED = 'deprecated',
  SUNSET = 'sunset',
  REMOVED = 'removed'
}

interface APIVersionConfig {
  version: string;
  state: APIVersionState;
  deprecation_date?: Date;
  sunset_date?: Date;
  removal_date?: Date;
  successor_version?: string;
}

const versionConfigs: Record<string, APIVersionConfig> = {
  v1: {
    version: 'v1',
    state: APIVersionState.SUNSET,
    deprecation_date: new Date('2025-12-06'),
    sunset_date: new Date('2026-04-01'),
    removal_date: new Date('2026-06-01'),
    successor_version: 'v2'
  },
  v2: {
    version: 'v2',
    state: APIVersionState.ACTIVE
  }
};

function getVersionState(version: string): APIVersionConfig {
  const config = versionConfigs[version];
  if (!config) {
    throw new Error(`Unknown version: ${version}`);
  }

  const now = new Date();

  // Update state based on dates
  if (config.removal_date && now >= config.removal_date) {
    config.state = APIVersionState.REMOVED;
  } else if (config.sunset_date && now >= config.sunset_date) {
    config.state = APIVersionState.SUNSET;
  } else if (config.deprecation_date && now >= config.deprecation_date) {
    config.state = APIVersionState.DEPRECATED;
  }

  return config;
}

// Middleware to enforce version state
function versionStateMiddleware(req: Request, res: Response, next: NextFunction) {
  const version = extractVersion(req); // e.g., 'v1' from /api/v1/users
  const config = getVersionState(version);

  switch (config.state) {
    case APIVersionState.REMOVED:
      return res.status(410).json({
        error: 'This API version has been removed',
        version: config.version,
        removal_date: config.removal_date,
        successor_version: config.successor_version,
        migration_guide: `https://api.example.com/docs/${version}-to-${config.successor_version}`
      });

    case APIVersionState.SUNSET:
      // Read-only mode: block write operations
      if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(req.method)) {
        return res.status(403).json({
          error: 'This API version is in sunset mode (read-only)',
          version: config.version,
          removal_date: config.removal_date,
          message: 'Write operations disabled. Please migrate to ' + config.successor_version
        });
      }
      // Allow GET/HEAD for reads
      setDeprecationHeaders(res, config.sunset_date!, config.successor_version!);
      break;

    case APIVersionState.DEPRECATED:
      setDeprecationHeaders(res, config.sunset_date!, config.successor_version!);
      break;

    case APIVersionState.ACTIVE:
      // No special handling
      break;
  }

  next();
}
```

**Python (FastAPI)**:
```python
from enum import Enum
from datetime import datetime
from typing import Optional
from fastapi import Request, Response, HTTPException

class APIVersionState(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"
    REMOVED = "removed"

class APIVersionConfig:
    def __init__(
        self,
        version: str,
        state: APIVersionState,
        deprecation_date: Optional[datetime] = None,
        sunset_date: Optional[datetime] = None,
        removal_date: Optional[datetime] = None,
        successor_version: Optional[str] = None
    ):
        self.version = version
        self.state = state
        self.deprecation_date = deprecation_date
        self.sunset_date = sunset_date
        self.removal_date = removal_date
        self.successor_version = successor_version

VERSION_CONFIGS = {
    'v1': APIVersionConfig(
        version='v1',
        state=APIVersionState.SUNSET,
        deprecation_date=datetime(2025, 12, 6),
        sunset_date=datetime(2026, 4, 1),
        removal_date=datetime(2026, 6, 1),
        successor_version='v2'
    ),
    'v2': APIVersionConfig(
        version='v2',
        state=APIVersionState.ACTIVE
    )
}

def get_version_state(version: str) -> APIVersionConfig:
    config = VERSION_CONFIGS.get(version)
    if not config:
        raise ValueError(f"Unknown version: {version}")

    now = datetime.now()

    # Update state based on dates
    if config.removal_date and now >= config.removal_date:
        config.state = APIVersionState.REMOVED
    elif config.sunset_date and now >= config.sunset_date:
        config.state = APIVersionState.SUNSET
    elif config.deprecation_date and now >= config.deprecation_date:
        config.state = APIVersionState.DEPRECATED

    return config

# Middleware
from starlette.middleware.base import BaseHTTPMiddleware

class VersionStateMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        version = self.extract_version(request.url.path)
        config = get_version_state(version)

        if config.state == APIVersionState.REMOVED:
            return Response(
                content={
                    'error': 'This API version has been removed',
                    'version': config.version,
                    'removal_date': config.removal_date.isoformat(),
                    'successor_version': config.successor_version
                },
                status_code=410,
                media_type='application/json'
            )

        if config.state == APIVersionState.SUNSET:
            if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                return Response(
                    content={
                        'error': 'This API version is in sunset mode (read-only)',
                        'version': config.version,
                        'removal_date': config.removal_date.isoformat()
                    },
                    status_code=403,
                    media_type='application/json'
                )

        response = await call_next(request)

        if config.state in [APIVersionState.DEPRECATED, APIVersionState.SUNSET]:
            set_deprecation_headers(response, config.sunset_date, config.successor_version)

        return response

    def extract_version(self, path: str) -> str:
        # Extract version from path like /api/v1/users
        import re
        match = re.search(r'/api/(v\d+)/', path)
        return match.group(1) if match else 'v1'
```

## Code Annotations

### Documentation Annotations

**TypeScript/JavaScript JSDoc**:
```typescript
/**
 * Get user by ID
 *
 * @deprecated Since version 2.0. Use {@link getUserV2} instead.
 * @param {number} id - User ID
 * @returns {Promise<User>} User object
 * @see https://api.example.com/docs/migration/get-user
 * @example
 * // Old (deprecated)
 * const user = await getUserV1(123);
 *
 * // New (recommended)
 * const user = await getUserV2(123);
 */
async function getUserV1(id: number): Promise<User> {
  console.warn('getUserV1 is deprecated. Use getUserV2 instead.');
  // Implementation
}
```

**Python Docstring**:
```python
def get_user_v1(user_id: int) -> User:
    """
    Get user by ID.

    .. deprecated:: 2.0
       Use :func:`get_user_v2` instead. This function will be removed in version 3.0.

    Args:
        user_id: The user's unique identifier

    Returns:
        User object

    See Also:
        get_user_v2: Replacement function with improved performance

    Examples:
        >>> # Old (deprecated)
        >>> user = get_user_v1(123)
        >>>
        >>> # New (recommended)
        >>> user = get_user_v2(123)
    """
    import warnings
    warnings.warn(
        "get_user_v1 is deprecated. Use get_user_v2 instead.",
        DeprecationWarning,
        stacklevel=2
    )
    # Implementation
```

### Runtime Warnings

**TypeScript**:
```typescript
function deprecated(
  replacement: string,
  removalVersion: string
): MethodDecorator {
  return function(
    target: any,
    propertyKey: string | symbol,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;

    descriptor.value = function(...args: any[]) {
      console.warn(
        `⚠️ ${String(propertyKey)} is deprecated and will be removed in ${removalVersion}. ` +
        `Use ${replacement} instead.`
      );

      // Track deprecation usage
      trackDeprecatedFunctionCall(String(propertyKey));

      return originalMethod.apply(this, args);
    };

    return descriptor;
  };
}

// Usage
class UserAPI {
  @deprecated('getUserV2', 'v3.0')
  async getUserV1(id: number): Promise<User> {
    // Implementation
  }

  async getUserV2(id: number): Promise<User> {
    // New implementation
  }
}
```

**Python Decorator**:
```python
import functools
import warnings

def deprecated(replacement: str, removal_version: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"⚠️ {func.__name__} is deprecated and will be removed in {removal_version}. "
                f"Use {replacement} instead.",
                DeprecationWarning,
                stacklevel=2
            )

            # Track deprecation usage
            track_deprecated_function_call(func.__name__)

            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
class UserAPI:
    @deprecated('get_user_v2', 'v3.0')
    def get_user_v1(self, user_id: int) -> User:
        # Implementation
        pass

    def get_user_v2(self, user_id: int) -> User:
        # New implementation
        pass
```

## Feature Flags

### Feature Flag Configuration

**TypeScript**:
```typescript
interface FeatureFlag {
  name: string;
  enabled: boolean;
  deprecation_date?: Date;
  removal_date?: Date;
  replacement_feature?: string;
}

class FeatureFlagService {
  private flags: Map<string, FeatureFlag> = new Map([
    ['legacy_user_api', {
      name: 'legacy_user_api',
      enabled: true, // Still enabled but deprecated
      deprecation_date: new Date('2025-12-06'),
      removal_date: new Date('2026-06-01'),
      replacement_feature: 'user_api_v2'
    }],
    ['user_api_v2', {
      name: 'user_api_v2',
      enabled: true
    }]
  ]);

  isEnabled(flagName: string): boolean {
    const flag = this.flags.get(flagName);
    if (!flag) return false;

    // Check if past removal date
    if (flag.removal_date && new Date() >= flag.removal_date) {
      return false;
    }

    return flag.enabled;
  }

  isDeprecated(flagName: string): boolean {
    const flag = this.flags.get(flagName);
    if (!flag || !flag.deprecation_date) return false;

    return new Date() >= flag.deprecation_date;
  }

  getReplacement(flagName: string): string | undefined {
    return this.flags.get(flagName)?.replacement_feature;
  }
}

// Usage in code
const featureFlags = new FeatureFlagService();

app.get('/api/users/:id', async (req, res) => {
  if (featureFlags.isEnabled('user_api_v2')) {
    // Use new implementation
    return getUserV2(req.params.id);
  } else if (featureFlags.isEnabled('legacy_user_api')) {
    // Use deprecated implementation with warning
    if (featureFlags.isDeprecated('legacy_user_api')) {
      const replacement = featureFlags.getReplacement('legacy_user_api');
      console.warn(`legacy_user_api is deprecated. Migrate to ${replacement}`);
    }
    return getUserV1(req.params.id);
  } else {
    return res.status(410).json({
      error: 'This feature has been removed',
      replacement: featureFlags.getReplacement('legacy_user_api')
    });
  }
});
```

**Python**:
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict

@dataclass
class FeatureFlag:
    name: str
    enabled: bool
    deprecation_date: Optional[datetime] = None
    removal_date: Optional[datetime] = None
    replacement_feature: Optional[str] = None

class FeatureFlagService:
    def __init__(self):
        self.flags: Dict[str, FeatureFlag] = {
            'legacy_user_api': FeatureFlag(
                name='legacy_user_api',
                enabled=True,  # Still enabled but deprecated
                deprecation_date=datetime(2025, 12, 6),
                removal_date=datetime(2026, 6, 1),
                replacement_feature='user_api_v2'
            ),
            'user_api_v2': FeatureFlag(
                name='user_api_v2',
                enabled=True
            )
        }

    def is_enabled(self, flag_name: str) -> bool:
        flag = self.flags.get(flag_name)
        if not flag:
            return False

        # Check if past removal date
        if flag.removal_date and datetime.now() >= flag.removal_date:
            return False

        return flag.enabled

    def is_deprecated(self, flag_name: str) -> bool:
        flag = self.flags.get(flag_name)
        if not flag or not flag.deprecation_date:
            return False

        return datetime.now() >= flag.deprecation_date

    def get_replacement(self, flag_name: str) -> Optional[str]:
        flag = self.flags.get(flag_name)
        return flag.replacement_feature if flag else None

# Usage
feature_flags = FeatureFlagService()

@app.get('/api/users/{user_id}')
async def get_user(user_id: int):
    if feature_flags.is_enabled('user_api_v2'):
        # Use new implementation
        return get_user_v2(user_id)
    elif feature_flags.is_enabled('legacy_user_api'):
        # Use deprecated implementation with warning
        if feature_flags.is_deprecated('legacy_user_api'):
            replacement = feature_flags.get_replacement('legacy_user_api')
            logging.warning(f"legacy_user_api is deprecated. Migrate to {replacement}")
        return get_user_v1(user_id)
    else:
        raise HTTPException(
            status_code=410,
            detail={
                'error': 'This feature has been removed',
                'replacement': feature_flags.get_replacement('legacy_user_api')
            }
        )
```

### Gradual Rollout with Feature Flags

**Progressive Feature Migration**:
```typescript
interface RolloutStrategy {
  percentage: number; // 0-100
  customer_ids?: string[]; // Whitelist
  exclude_customer_ids?: string[]; // Blacklist
}

class FeatureFlagService {
  private rolloutStrategies: Map<string, RolloutStrategy> = new Map([
    ['user_api_v2', {
      percentage: 50, // 50% of traffic
      customer_ids: ['early-adopter-1', 'early-adopter-2'], // Always enabled
      exclude_customer_ids: ['legacy-customer-1'] // Never enabled
    }]
  ]);

  isEnabledForUser(flagName: string, customerId: string): boolean {
    const strategy = this.rolloutStrategies.get(flagName);
    if (!strategy) return this.isEnabled(flagName);

    // Check exclusion list
    if (strategy.exclude_customer_ids?.includes(customerId)) {
      return false;
    }

    // Check whitelist
    if (strategy.customer_ids?.includes(customerId)) {
      return true;
    }

    // Percentage-based rollout
    const hash = this.hashCustomerId(customerId);
    return hash % 100 < strategy.percentage;
  }

  private hashCustomerId(customerId: string): number {
    // Simple hash function for deterministic percentage
    let hash = 0;
    for (let i = 0; i < customerId.length; i++) {
      hash = ((hash << 5) - hash) + customerId.charCodeAt(i);
      hash |= 0; // Convert to 32-bit integer
    }
    return Math.abs(hash);
  }
}
```

## Complete Implementation Example

Here's a complete end-to-end implementation example:

**Step 1: Configure Version States**
```typescript
// config/api-versions.ts
export const API_VERSION_CONFIG = {
  v1: {
    version: 'v1',
    state: 'sunset',
    deprecation_date: new Date('2025-12-06'),
    sunset_date: new Date('2026-04-01'),
    removal_date: new Date('2026-06-01'),
    successor_version: 'v2'
  },
  v2: {
    version: 'v2',
    state: 'active'
  }
};
```

**Step 2: Create Middleware**
```typescript
// middleware/deprecation.ts
import { API_VERSION_CONFIG } from '../config/api-versions';

export function deprecationMiddleware(req: Request, res: Response, next: NextFunction) {
  const version = extractVersion(req.path);
  const config = API_VERSION_CONFIG[version];

  if (!config) {
    return next();
  }

  // Add deprecation headers
  if (config.state === 'deprecated' || config.state === 'sunset') {
    res.set('Deprecation', 'true');
    res.set('Sunset', formatHttpDate(config.removal_date));
    res.set('Link', `</${config.successor_version}>; rel="successor-version"`);
  }

  // Block removed versions
  if (config.state === 'removed') {
    return res.status(410).json({
      error: 'This API version has been removed',
      migration_guide: `https://api.example.com/docs/${version}-to-${config.successor_version}`
    });
  }

  // Block writes in sunset mode
  if (config.state === 'sunset' && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(req.method)) {
    return res.status(403).json({
      error: 'This API version is in sunset mode (read-only)',
      removal_date: config.removal_date.toISOString()
    });
  }

  next();
}
```

**Step 3: Apply Middleware**
```typescript
// app.ts
import express from 'express';
import { deprecationMiddleware } from './middleware/deprecation';

const app = express();

app.use(deprecationMiddleware);

// Routes
app.get('/v1/users', getUsersV1);
app.get('/v2/users', getUsersV2);

app.listen(3000);
```

## Quick Reference

### HTTP Headers

```http
Deprecation: true
Sunset: Mon, 01 Jun 2026 00:00:00 GMT
Link: </api/v2>; rel="successor-version"
Link: <https://api.example.com/docs/migration>; rel="deprecation"
```

### Error Codes

- **200 OK** + Deprecation headers: Deprecated but functional
- **403 Forbidden**: Sunset mode (read-only), write blocked
- **410 Gone**: Completely removed
- **429 Too Many Requests** + Deprecation info: Rate limiting deprecated version

### Version States

1. **Active**: Full support, all updates
2. **Deprecated**: Full functionality, security updates only
3. **Sunset**: Read-only mode, removal pending
4. **Removed**: Returns 410 Gone

### Code Annotations

**TypeScript**:
```typescript
@deprecated('newMethod', 'v3.0')
```

**Python**:
```python
@deprecated('new_method', 'v3.0')
```

### Feature Flag Checks

```typescript
if (featureFlags.isEnabled('feature_name')) {
  // Use feature
}

if (featureFlags.isDeprecated('feature_name')) {
  // Warn about deprecation
}
```
