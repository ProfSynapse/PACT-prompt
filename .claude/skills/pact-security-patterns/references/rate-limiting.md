# Rate Limiting and Throttling Patterns

Complete guide to implementing rate limiting to protect against abuse, DoS attacks, and resource exhaustion.

## Rate Limiting Strategy Decision Tree

```
What are you protecting?
├─ API endpoints
│   ├─ Public endpoints (no auth) → Aggressive limits (IP-based)
│   ├─ Authenticated endpoints → User-based limits
│   └─ Critical operations (login, signup) → Strict limits + CAPTCHA
│
├─ Resource-intensive operations
│   ├─ File uploads → Size + count limits
│   ├─ Database queries → Query complexity limits
│   ├─ External API calls → Cost-based throttling
│   └─ Computation → CPU/memory quotas
│
└─ Business operations
    ├─ Free tier → Usage caps + upgrade prompts
    ├─ Paid tier → Plan-based quotas
    └─ Enterprise → Custom limits + burst allowance

Algorithm selection:
├─ Simple enforcement → Fixed Window Counter
├─ Smooth traffic shaping → Leaky Bucket
├─ Burst tolerance → Token Bucket (RECOMMENDED)
├─ Precise rate limiting → Sliding Window Log
└─ Memory-efficient precision → Sliding Window Counter

Distributed systems?
├─ Single server → In-memory storage
├─ Multiple servers → Redis-based coordination
└─ Multi-region → Regional limits + global aggregation
```

## Core Rate Limiting Algorithms

### 1. Token Bucket Algorithm (RECOMMENDED)

**Concept**: Tokens accumulate in a bucket at a fixed rate. Each request consumes one token. If no tokens available, request is denied.

**Characteristics**:
- Allows bursts up to bucket capacity
- Smooth long-term rate limiting
- Most flexible and commonly used
- Used by: AWS API Gateway, Stripe API, GitHub API

**Implementation**:

```javascript
// Token Bucket - In-Memory Implementation
class TokenBucket {
  constructor(capacity, refillRate) {
    this.capacity = capacity;          // Max tokens in bucket
    this.tokens = capacity;            // Current tokens
    this.refillRate = refillRate;      // Tokens added per second
    this.lastRefill = Date.now();
  }

  refill() {
    const now = Date.now();
    const timePassed = (now - this.lastRefill) / 1000;  // seconds
    const tokensToAdd = timePassed * this.refillRate;

    this.tokens = Math.min(this.capacity, this.tokens + tokensToAdd);
    this.lastRefill = now;
  }

  consume(tokens = 1) {
    this.refill();

    if (this.tokens >= tokens) {
      this.tokens -= tokens;
      return {
        allowed: true,
        remaining: Math.floor(this.tokens),
        retryAfter: null
      };
    }

    // Calculate retry-after time
    const tokensNeeded = tokens - this.tokens;
    const retryAfter = Math.ceil(tokensNeeded / this.refillRate);

    return {
      allowed: false,
      remaining: 0,
      retryAfter  // seconds
    };
  }
}

// Usage
const bucket = new TokenBucket(100, 10);  // 100 capacity, 10 tokens/sec

app.use((req, res, next) => {
  const key = req.user?.id || req.ip;
  const bucket = getBucket(key);  // Get or create bucket for user/IP

  const result = bucket.consume(1);

  // Set rate limit headers
  res.set('X-RateLimit-Limit', bucket.capacity);
  res.set('X-RateLimit-Remaining', result.remaining);

  if (!result.allowed) {
    res.set('Retry-After', result.retryAfter);
    return res.status(429).json({
      error: 'Too many requests',
      retryAfter: result.retryAfter
    });
  }

  next();
});
```

**Redis-based Token Bucket**:

```python
import redis
import time
import math

class RedisTokenBucket:
    def __init__(self, redis_client, key, capacity, refill_rate):
        self.redis = redis_client
        self.key = f"rate_limit:{key}"
        self.capacity = capacity
        self.refill_rate = refill_rate

    def consume(self, tokens=1):
        now = time.time()

        # Lua script for atomic token bucket operations
        lua_script = """
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        local tokens_requested = tonumber(ARGV[4])

        -- Get current state
        local state = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(state[1]) or capacity
        local last_refill = tonumber(state[2]) or now

        -- Refill tokens
        local time_passed = now - last_refill
        local tokens_to_add = time_passed * refill_rate
        tokens = math.min(capacity, tokens + tokens_to_add)

        -- Try to consume
        local allowed = 0
        local remaining = math.floor(tokens)
        local retry_after = 0

        if tokens >= tokens_requested then
            tokens = tokens - tokens_requested
            allowed = 1
            remaining = math.floor(tokens)
        else
            local tokens_needed = tokens_requested - tokens
            retry_after = math.ceil(tokens_needed / refill_rate)
        end

        -- Update state
        redis.call('HSET', key, 'tokens', tokens, 'last_refill', now)
        redis.call('EXPIRE', key, 3600)  -- 1 hour TTL

        return {allowed, remaining, retry_after}
        """

        result = self.redis.eval(
            lua_script,
            1,  # Number of keys
            self.key,
            self.capacity,
            self.refill_rate,
            now,
            tokens
        )

        return {
            'allowed': bool(result[0]),
            'remaining': int(result[1]),
            'retryAfter': int(result[2])
        }

# Usage
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

@app.before_request
def rate_limit():
    user_id = get_user_id() or request.remote_addr
    bucket = RedisTokenBucket(redis_client, user_id, capacity=100, refill_rate=10)

    result = bucket.consume(1)

    response.headers['X-RateLimit-Limit'] = '100'
    response.headers['X-RateLimit-Remaining'] = str(result['remaining'])

    if not result['allowed']:
        response.headers['Retry-After'] = str(result['retryAfter'])
        abort(429, description='Too many requests')
```

**Pros**:
- Allows controlled bursts (good UX)
- Memory efficient (2 values per user)
- Natural rate smoothing
- Industry standard

**Cons**:
- Complexity in distributed systems
- Requires careful tuning of capacity and refill rate
- Clock skew issues in distributed setups

**Use cases**:
- General API rate limiting
- Services with bursty legitimate traffic
- Protecting against gradual DoS attacks

---

### 2. Sliding Window Counter

**Concept**: Combines fixed window simplicity with sliding window precision. Approximates current window rate based on previous and current fixed windows.

**Implementation**:

```javascript
// Sliding Window Counter - Redis Implementation
async function slidingWindowRateLimit(userId, limit, windowSeconds) {
  const now = Date.now();
  const currentWindow = Math.floor(now / (windowSeconds * 1000));
  const previousWindow = currentWindow - 1;

  const currentKey = `rate_limit:${userId}:${currentWindow}`;
  const previousKey = `rate_limit:${userId}:${previousWindow}`;

  // Get counts from both windows
  const [currentCount, previousCount] = await Promise.all([
    redis.get(currentKey).then(v => parseInt(v) || 0),
    redis.get(previousKey).then(v => parseInt(v) || 0)
  ]);

  // Calculate position in current window (0.0 to 1.0)
  const percentageInCurrent = (now % (windowSeconds * 1000)) / (windowSeconds * 1000);

  // Weighted count from previous window
  const estimatedCount =
    Math.floor(previousCount * (1 - percentageInCurrent)) + currentCount;

  if (estimatedCount >= limit) {
    const resetTime = (currentWindow + 1) * windowSeconds;
    return {
      allowed: false,
      remaining: 0,
      resetAt: resetTime
    };
  }

  // Increment current window
  const pipeline = redis.pipeline();
  pipeline.incr(currentKey);
  pipeline.expire(currentKey, windowSeconds * 2);  // Keep for 2 windows
  await pipeline.exec();

  return {
    allowed: true,
    remaining: limit - estimatedCount - 1,
    resetAt: (currentWindow + 1) * windowSeconds
  };
}

// Express middleware
app.use(async (req, res, next) => {
  const userId = req.user?.id || req.ip;
  const result = await slidingWindowRateLimit(userId, 100, 60);  // 100 req/min

  res.set('X-RateLimit-Limit', '100');
  res.set('X-RateLimit-Remaining', result.remaining.toString());
  res.set('X-RateLimit-Reset', result.resetAt.toString());

  if (!result.allowed) {
    const retryAfter = result.resetAt - Math.floor(Date.now() / 1000);
    res.set('Retry-After', retryAfter.toString());
    return res.status(429).json({ error: 'Too many requests' });
  }

  next();
});
```

**Python Implementation with Redis**:

```python
import time
import redis

class SlidingWindowRateLimiter:
    def __init__(self, redis_client, key, limit, window_seconds):
        self.redis = redis_client
        self.key_prefix = f"rate_limit:{key}"
        self.limit = limit
        self.window_seconds = window_seconds

    def is_allowed(self):
        now = time.time()
        current_window = int(now // self.window_seconds)
        previous_window = current_window - 1

        current_key = f"{self.key_prefix}:{current_window}"
        previous_key = f"{self.key_prefix}:{previous_window}"

        # Get counts
        pipe = self.redis.pipeline()
        pipe.get(current_key)
        pipe.get(previous_key)
        current_count, previous_count = pipe.execute()

        current_count = int(current_count) if current_count else 0
        previous_count = int(previous_count) if previous_count else 0

        # Calculate weighted count
        percentage_in_current = (now % self.window_seconds) / self.window_seconds
        estimated_count = int(
            previous_count * (1 - percentage_in_current) + current_count
        )

        if estimated_count >= self.limit:
            reset_at = (current_window + 1) * self.window_seconds
            return {
                'allowed': False,
                'remaining': 0,
                'reset_at': reset_at
            }

        # Increment counter
        pipe = self.redis.pipeline()
        pipe.incr(current_key)
        pipe.expire(current_key, self.window_seconds * 2)
        pipe.execute()

        return {
            'allowed': True,
            'remaining': self.limit - estimated_count - 1,
            'reset_at': (current_window + 1) * self.window_seconds
        }
```

**Pros**:
- More accurate than fixed window
- Memory efficient (2 counters)
- No sudden traffic spikes at window boundaries
- Good for distributed systems

**Cons**:
- Approximation (not exact)
- Can allow slightly over limit in edge cases
- Requires synchronized clocks

**Use cases**:
- APIs with strict rate limits
- Distributed systems needing precision
- Services with predictable traffic patterns

---

### 3. Leaky Bucket

**Concept**: Requests enter a queue (bucket) and drain at a constant rate. If bucket overflows, requests are rejected.

**Implementation**:

```javascript
// Leaky Bucket - Queue-based Implementation
class LeakyBucket {
  constructor(capacity, leakRate) {
    this.capacity = capacity;        // Max queue size
    this.leakRate = leakRate;        // Requests processed per second
    this.queue = [];
    this.lastLeak = Date.now();
  }

  leak() {
    const now = Date.now();
    const timePassed = (now - this.lastLeak) / 1000;
    const leakedRequests = Math.floor(timePassed * this.leakRate);

    if (leakedRequests > 0) {
      this.queue.splice(0, leakedRequests);
      this.lastLeak = now;
    }
  }

  add(request) {
    this.leak();

    if (this.queue.length >= this.capacity) {
      return {
        allowed: false,
        queueSize: this.queue.length,
        retryAfter: Math.ceil(this.queue.length / this.leakRate)
      };
    }

    this.queue.push(request);
    const position = this.queue.length;
    const estimatedWait = position / this.leakRate;

    return {
      allowed: true,
      queueSize: position,
      estimatedWait  // seconds until processing
    };
  }
}

// Redis-based Leaky Bucket (using sorted set for queue)
async function leakyBucketRateLimit(key, capacity, leakRate) {
  const now = Date.now();
  const queueKey = `leaky_bucket:${key}`;

  const lua_script = `
    local queue_key = KEYS[1]
    local capacity = tonumber(ARGV[1])
    local leak_rate = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])

    -- Remove old entries (leaked)
    local last_leak = tonumber(redis.call('GET', queue_key .. ':last_leak') or now)
    local time_passed = (now - last_leak) / 1000
    local to_remove = math.floor(time_passed * leak_rate)

    if to_remove > 0 then
      redis.call('ZREMRANGEBYRANK', queue_key, 0, to_remove - 1)
      redis.call('SET', queue_key .. ':last_leak', now)
    end

    -- Check capacity
    local queue_size = redis.call('ZCARD', queue_key)
    if queue_size >= capacity then
      local retry_after = math.ceil(queue_size / leak_rate)
      return {0, queue_size, retry_after}
    end

    -- Add to queue
    redis.call('ZADD', queue_key, now, now .. ':' .. math.random())
    redis.call('EXPIRE', queue_key, 3600)

    queue_size = queue_size + 1
    local estimated_wait = queue_size / leak_rate

    return {1, queue_size, estimated_wait}
  `;

  const result = await redis.eval(
    lua_script,
    1,
    queueKey,
    capacity,
    leakRate,
    now
  );

  return {
    allowed: result[0] === 1,
    queueSize: result[1],
    waitTime: result[2]
  };
}
```

**Pros**:
- Perfectly smooth output rate
- Great for traffic shaping
- Protects downstream services
- Predictable resource usage

**Cons**:
- Adds latency (queueing)
- Memory overhead (queue storage)
- Complex distributed implementation
- Can delay legitimate requests

**Use cases**:
- Protecting rate-sensitive downstream services
- Traffic shaping for external API calls
- Background job processing
- Webhook delivery systems

---

### 4. Fixed Window Counter

**Concept**: Count requests in fixed time windows. Reset counter at window boundary.

**Implementation**:

```python
import redis
import time

class FixedWindowRateLimiter:
    def __init__(self, redis_client, key, limit, window_seconds):
        self.redis = redis_client
        self.key = f"rate_limit:{key}"
        self.limit = limit
        self.window_seconds = window_seconds

    def is_allowed(self):
        current_window = int(time.time() // self.window_seconds)
        key = f"{self.key}:{current_window}"

        # Increment counter
        count = self.redis.incr(key)

        # Set expiration on first request
        if count == 1:
            self.redis.expire(key, self.window_seconds)

        remaining = max(0, self.limit - count)
        reset_at = (current_window + 1) * self.window_seconds

        return {
            'allowed': count <= self.limit,
            'remaining': remaining,
            'reset_at': reset_at
        }

# Express.js middleware
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 60 * 1000,  // 1 minute
  max: 100,  // 100 requests per window
  standardHeaders: true,  // Return rate limit info in headers
  legacyHeaders: false,
  handler: (req, res) => {
    res.status(429).json({
      error: 'Too many requests',
      retryAfter: Math.ceil((req.rateLimit.resetTime - Date.now()) / 1000)
    });
  }
});

app.use('/api/', limiter);
```

**Pros**:
- Extremely simple to implement
- Very memory efficient
- Minimal computational overhead
- Easy to reason about

**Cons**:
- Traffic spikes at window boundaries (can get 2x limit)
- Unfair: early requesters consume quota
- Sudden resets confusing for users

**Use cases**:
- Internal rate limiting (less critical)
- Simple quotas and billing
- Quick implementation for low-stakes APIs
- Development/testing environments

---

## Distributed Rate Limiting

### Redis-based Coordination

**Problem**: Multiple servers need to coordinate rate limits across instances.

**Solution**: Centralized Redis store with atomic operations.

```javascript
// Production-grade Redis rate limiter with retry logic
const Redis = require('ioredis');

class DistributedRateLimiter {
  constructor(redisClient, options = {}) {
    this.redis = redisClient;
    this.prefix = options.prefix || 'rate_limit';
    this.maxRetries = options.maxRetries || 3;
  }

  async checkLimit(identifier, limit, windowSeconds, cost = 1) {
    const key = `${this.prefix}:${identifier}`;

    // Lua script for atomic rate limit check
    const lua = `
      local key = KEYS[1]
      local limit = tonumber(ARGV[1])
      local window = tonumber(ARGV[2])
      local cost = tonumber(ARGV[3])
      local now = tonumber(ARGV[4])

      -- Use sorted set to track requests with timestamps
      local window_start = now - window

      -- Remove old entries
      redis.call('ZREMRANGEBYSCORE', key, 0, window_start)

      -- Count current requests
      local current = redis.call('ZCARD', key)

      if current + cost > limit then
        local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
        local reset_at = oldest[2] and (tonumber(oldest[2]) + window) or (now + window)
        return {0, current, limit, reset_at}
      end

      -- Add current request
      for i = 1, cost do
        redis.call('ZADD', key, now, now .. ':' .. i .. ':' .. math.random())
      end

      redis.call('EXPIRE', key, window)

      return {1, current + cost, limit, now + window}
    `;

    let retries = 0;
    while (retries < this.maxRetries) {
      try {
        const result = await this.redis.eval(
          lua,
          1,
          key,
          limit,
          windowSeconds,
          cost,
          Date.now()
        );

        return {
          allowed: result[0] === 1,
          current: result[1],
          limit: result[2],
          resetAt: new Date(result[3]),
          remaining: Math.max(0, result[2] - result[1])
        };
      } catch (error) {
        retries++;
        if (retries >= this.maxRetries) {
          // Fail open: allow request if Redis is down
          console.error('Rate limit check failed:', error);
          return {
            allowed: true,
            current: 0,
            limit,
            resetAt: new Date(Date.now() + windowSeconds * 1000),
            remaining: limit,
            error: 'Rate limit check unavailable'
          };
        }
        // Exponential backoff
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, retries) * 10));
      }
    }
  }
}

// Usage with Express
const redis = new Redis({
  host: process.env.REDIS_HOST,
  port: process.env.REDIS_PORT,
  retryStrategy: (times) => {
    return Math.min(times * 50, 2000);
  }
});

const rateLimiter = new DistributedRateLimiter(redis);

app.use(async (req, res, next) => {
  const identifier = req.user?.id || req.ip;
  const result = await rateLimiter.checkLimit(identifier, 100, 60);

  res.set('X-RateLimit-Limit', result.limit.toString());
  res.set('X-RateLimit-Remaining', result.remaining.toString());
  res.set('X-RateLimit-Reset', Math.floor(result.resetAt.getTime() / 1000).toString());

  if (!result.allowed) {
    res.set('Retry-After', Math.ceil((result.resetAt - Date.now()) / 1000).toString());
    return res.status(429).json({
      error: 'Too many requests',
      retryAfter: result.resetAt
    });
  }

  next();
});
```

### Multi-Region Rate Limiting

**Challenge**: Coordinating limits across geographically distributed data centers.

**Approaches**:

```javascript
// Approach 1: Regional limits with global aggregation
class MultiRegionRateLimiter {
  constructor(localRedis, options = {}) {
    this.localRedis = localRedis;
    this.region = options.region || 'default';
    this.globalLimit = options.globalLimit;
    this.regionalLimit = options.regionalLimit;
  }

  async checkLimit(identifier) {
    // Check regional limit first (fast)
    const regionalResult = await this.checkRegionalLimit(identifier);
    if (!regionalResult.allowed) {
      return regionalResult;
    }

    // Check global limit (slower, eventual consistency OK)
    if (this.globalLimit) {
      const globalResult = await this.checkGlobalLimit(identifier);
      if (!globalResult.allowed) {
        return globalResult;
      }
    }

    return regionalResult;
  }

  async checkRegionalLimit(identifier) {
    const key = `rate_limit:${this.region}:${identifier}`;
    // Use local Redis for regional limit
    return await this.localRedis.checkLimit(key, this.regionalLimit, 60);
  }

  async checkGlobalLimit(identifier) {
    // Aggregate counts from all regions (can be eventually consistent)
    const key = `rate_limit:global:${identifier}`;
    return await this.localRedis.checkLimit(key, this.globalLimit, 60);
  }
}

// Approach 2: Partition limits by region
class PartitionedRateLimiter {
  async checkLimit(identifier, globalLimit) {
    const regions = ['us-east', 'us-west', 'eu-west', 'ap-south'];
    const limitPerRegion = Math.ceil(globalLimit / regions.length);

    // Each region enforces its partition independently
    const regionalKey = `rate_limit:${this.region}:${identifier}`;
    return await this.redis.checkLimit(regionalKey, limitPerRegion, 60);
  }
}
```

---

## Rate Limit Headers

**Standard headers for communicating rate limit status to clients:**

```javascript
// Standard Rate Limit Headers (IETF Draft)
function setRateLimitHeaders(res, rateLimit) {
  // RateLimit-Policy: Shows the policy applied
  res.set('RateLimit-Policy', `${rateLimit.limit};w=${rateLimit.window}`);

  // RateLimit-Limit: Requests allowed in window
  res.set('RateLimit-Limit', rateLimit.limit.toString());

  // RateLimit-Remaining: Requests remaining in current window
  res.set('RateLimit-Remaining', rateLimit.remaining.toString());

  // RateLimit-Reset: Seconds until window reset
  const resetSeconds = Math.ceil((rateLimit.resetAt - Date.now()) / 1000);
  res.set('RateLimit-Reset', resetSeconds.toString());

  // Legacy Twitter-style headers (widely supported)
  res.set('X-RateLimit-Limit', rateLimit.limit.toString());
  res.set('X-RateLimit-Remaining', rateLimit.remaining.toString());
  res.set('X-RateLimit-Reset', Math.floor(rateLimit.resetAt.getTime() / 1000).toString());

  // When rate limited, include Retry-After
  if (rateLimit.remaining === 0) {
    res.set('Retry-After', resetSeconds.toString());
  }
}

// Usage
app.use((req, res, next) => {
  const result = rateLimiter.check(req.user?.id || req.ip);

  setRateLimitHeaders(res, {
    limit: 100,
    remaining: result.remaining,
    window: 60,
    resetAt: result.resetAt
  });

  if (!result.allowed) {
    return res.status(429).json({
      error: 'Too many requests',
      message: 'You have exceeded the rate limit. Please try again later.',
      retryAfter: Math.ceil((result.resetAt - Date.now()) / 1000)
    });
  }

  next();
});
```

---

## Bypass Prevention Strategies

### 1. IP + User Combination

```javascript
// Multi-factor rate limiting
class MultiFactorRateLimiter {
  async checkLimit(req) {
    const checks = [];

    // Check 1: IP-based limit (prevents IP rotation)
    checks.push(
      this.checkByIP(req.ip, { limit: 1000, window: 3600 })
    );

    // Check 2: User-based limit (if authenticated)
    if (req.user) {
      checks.push(
        this.checkByUser(req.user.id, { limit: 100, window: 60 })
      );
    }

    // Check 3: IP + User Agent combination (detect bot patterns)
    const fingerprint = this.createFingerprint(req);
    checks.push(
      this.checkByFingerprint(fingerprint, { limit: 200, window: 60 })
    );

    // Check 4: Endpoint-specific limits
    checks.push(
      this.checkByEndpoint(req.path, req.ip, { limit: 10, window: 60 })
    );

    const results = await Promise.all(checks);

    // Fail if any check fails
    const failed = results.find(r => !r.allowed);
    return failed || results[0];
  }

  createFingerprint(req) {
    const crypto = require('crypto');
    const data = `${req.ip}:${req.get('User-Agent')}:${req.get('Accept-Language')}`;
    return crypto.createHash('sha256').update(data).digest('hex');
  }
}
```

### 2. Advanced Fingerprinting

```python
import hashlib
import json

class DeviceFingerprinter:
    def __init__(self):
        self.weights = {
            'ip': 0.3,
            'user_agent': 0.2,
            'accept_language': 0.1,
            'accept_encoding': 0.1,
            'tls_fingerprint': 0.2,
            'behavior': 0.1
        }

    def create_fingerprint(self, request):
        components = {
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'accept_language': request.headers.get('Accept-Language', ''),
            'accept_encoding': request.headers.get('Accept-Encoding', ''),
            'tls_fingerprint': self.get_tls_fingerprint(request),
            'behavior': self.analyze_behavior(request)
        }

        # Create weighted fingerprint
        fingerprint = hashlib.sha256(
            json.dumps(components, sort_keys=True).encode()
        ).hexdigest()

        return fingerprint

    def get_tls_fingerprint(self, request):
        # JA3 fingerprinting for TLS client identification
        # https://github.com/salesforce/ja3
        tls_data = {
            'version': request.environ.get('SSL_PROTOCOL'),
            'ciphers': request.environ.get('SSL_CIPHER_SUITES'),
            'extensions': request.environ.get('SSL_EXTENSIONS')
        }
        return hashlib.md5(
            json.dumps(tls_data, sort_keys=True).encode()
        ).hexdigest()

    def analyze_behavior(self, request):
        # Behavioral fingerprinting
        # - Mouse movement patterns
        # - Keystroke dynamics
        # - Request timing patterns
        # Returned from client-side JavaScript
        return request.headers.get('X-Behavior-Hash', '')
```

### 3. CAPTCHA Integration

```javascript
// Progressive CAPTCHA enforcement
class AdaptiveRateLimiter {
  async checkRequest(req) {
    const identifier = req.user?.id || req.ip;
    const result = await this.rateLimiter.check(identifier);

    // Progressive enforcement
    if (result.remaining < result.limit * 0.1) {
      // Less than 10% remaining: require CAPTCHA
      if (!req.body.captchaToken) {
        return {
          allowed: false,
          requiresCaptcha: true,
          remaining: result.remaining
        };
      }

      // Verify CAPTCHA
      const captchaValid = await this.verifyCaptcha(req.body.captchaToken);
      if (!captchaValid) {
        return {
          allowed: false,
          error: 'Invalid CAPTCHA',
          remaining: result.remaining
        };
      }

      // CAPTCHA success: grant extra quota
      await this.grantBonus(identifier, 10);
      result.remaining += 10;
    }

    return result;
  }

  async verifyCaptcha(token) {
    // Google reCAPTCHA v3
    const response = await fetch('https://www.google.com/recaptcha/api/siteverify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        secret: process.env.RECAPTCHA_SECRET_KEY,
        response: token
      })
    });

    const data = await response.json();
    return data.success && data.score > 0.5;  // Score threshold
  }
}
```

### 4. Cost-Based Rate Limiting

```python
# Different operations have different costs
class CostBasedRateLimiter:
    OPERATION_COSTS = {
        'list_items': 1,
        'get_item': 1,
        'create_item': 5,
        'update_item': 3,
        'delete_item': 2,
        'search': 10,
        'export': 50,
        'bulk_import': 100
    }

    def __init__(self, redis_client, user_id, total_budget):
        self.redis = redis_client
        self.user_id = user_id
        self.total_budget = total_budget
        self.window_seconds = 3600  # 1 hour

    def check_budget(self, operation):
        cost = self.OPERATION_COSTS.get(operation, 1)
        key = f"rate_limit:cost:{self.user_id}"

        # Check current spend
        current_spend = int(self.redis.get(key) or 0)

        if current_spend + cost > self.total_budget:
            reset_time = self.redis.ttl(key)
            return {
                'allowed': False,
                'cost': cost,
                'spent': current_spend,
                'budget': self.total_budget,
                'reset_in': reset_time
            }

        # Deduct cost
        pipe = self.redis.pipeline()
        new_spend = pipe.incrby(key, cost)
        if current_spend == 0:
            pipe.expire(key, self.window_seconds)
        pipe.execute()

        return {
            'allowed': True,
            'cost': cost,
            'spent': current_spend + cost,
            'budget': self.total_budget,
            'remaining': self.total_budget - current_spend - cost
        }
```

---

## Endpoint-Specific Rate Limiting

```javascript
// Different limits for different endpoints
const rateLimitConfig = {
  '/api/auth/login': {
    windowMs: 15 * 60 * 1000,  // 15 minutes
    max: 5,  // 5 attempts
    skipSuccessfulRequests: true,  // Don't count successful logins
    keyGenerator: (req) => req.body.username || req.ip  // Per username or IP
  },
  '/api/auth/signup': {
    windowMs: 60 * 60 * 1000,  // 1 hour
    max: 3,  // 3 signups per hour per IP
    keyGenerator: (req) => req.ip
  },
  '/api/password-reset': {
    windowMs: 60 * 60 * 1000,
    max: 5,
    keyGenerator: (req) => req.body.email || req.ip
  },
  '/api/search': {
    windowMs: 60 * 1000,  // 1 minute
    max: 20,  // 20 searches per minute
    keyGenerator: (req) => req.user?.id || req.ip
  },
  '/api/export': {
    windowMs: 24 * 60 * 60 * 1000,  // 24 hours
    max: 10,  // 10 exports per day
    keyGenerator: (req) => req.user.id  // Must be authenticated
  },
  '/api/*': {  // Default for all other endpoints
    windowMs: 60 * 1000,
    max: 100,
    keyGenerator: (req) => req.user?.id || req.ip
  }
};

// Apply endpoint-specific limits
Object.entries(rateLimitConfig).forEach(([endpoint, config]) => {
  app.use(endpoint, rateLimit(config));
});
```

---

## Testing Rate Limiters

```javascript
// Unit tests for rate limiter
describe('TokenBucket Rate Limiter', () => {
  let bucket;

  beforeEach(() => {
    bucket = new TokenBucket(10, 1);  // 10 capacity, 1 token/sec
  });

  test('allows requests within limit', () => {
    for (let i = 0; i < 10; i++) {
      const result = bucket.consume();
      expect(result.allowed).toBe(true);
    }
  });

  test('rejects requests over limit', () => {
    // Consume all tokens
    for (let i = 0; i < 10; i++) {
      bucket.consume();
    }

    const result = bucket.consume();
    expect(result.allowed).toBe(false);
    expect(result.retryAfter).toBeGreaterThan(0);
  });

  test('refills tokens over time', async () => {
    // Consume all tokens
    for (let i = 0; i < 10; i++) {
      bucket.consume();
    }

    // Wait for refill (2 seconds = 2 tokens)
    await new Promise(resolve => setTimeout(resolve, 2000));

    const result1 = bucket.consume();
    expect(result1.allowed).toBe(true);

    const result2 = bucket.consume();
    expect(result2.allowed).toBe(true);

    const result3 = bucket.consume();
    expect(result3.allowed).toBe(false);
  });

  test('handles bursts correctly', () => {
    // Burst of 10 requests should succeed
    const results = Array.from({ length: 10 }, () => bucket.consume());
    expect(results.every(r => r.allowed)).toBe(true);

    // 11th should fail
    expect(bucket.consume().allowed).toBe(false);
  });
});

// Load testing rate limiter
async function loadTest() {
  const rateLimiter = new DistributedRateLimiter(redis);
  const concurrency = 100;
  const requestsPerClient = 50;

  const clients = Array.from({ length: concurrency }, (_, i) => `client_${i}`);

  const results = await Promise.all(
    clients.map(async (clientId) => {
      const clientResults = [];
      for (let i = 0; i < requestsPerClient; i++) {
        const result = await rateLimiter.checkLimit(clientId, 100, 60);
        clientResults.push(result.allowed);
      }
      return clientResults;
    })
  );

  const totalRequests = concurrency * requestsPerClient;
  const allowedRequests = results.flat().filter(Boolean).length;

  console.log(`Total: ${totalRequests}, Allowed: ${allowedRequests}, Rejected: ${totalRequests - allowedRequests}`);
}
```

---

## Quick Reference

### Algorithm Comparison

| Algorithm | Bursts | Memory | Precision | Distributed | Best For |
|-----------|--------|--------|-----------|-------------|----------|
| **Token Bucket** | Yes | Low | Good | Medium | General APIs, allows bursts |
| **Sliding Window** | Moderate | Medium | Excellent | Easy | Precise limits, distributed systems |
| **Leaky Bucket** | No | Medium | Perfect | Hard | Traffic shaping, constant rate |
| **Fixed Window** | Yes (2x) | Very Low | Poor | Easy | Simple quotas, internal APIs |

### Implementation Checklist

- [ ] Choose algorithm based on use case (Token Bucket recommended)
- [ ] Implement Redis-based storage for distributed systems
- [ ] Use Lua scripts for atomic operations
- [ ] Set appropriate limits per endpoint
- [ ] Implement multiple rate limit factors (IP, user, fingerprint)
- [ ] Add standard rate limit headers
- [ ] Include Retry-After header when rate limited
- [ ] Log rate limit violations for monitoring
- [ ] Fail open if rate limiter is unavailable
- [ ] Test with load testing tools
- [ ] Monitor false positives (legitimate users blocked)
- [ ] Implement CAPTCHA for progressive enforcement
- [ ] Document rate limits in API documentation
- [ ] Provide webhooks or polling for quota status
- [ ] Consider different limits for authenticated vs anonymous users

### Common Rate Limit Values

**Public APIs:**
- GitHub: 5,000 requests/hour (authenticated), 60/hour (unauthenticated)
- Twitter: 900 requests/15 min (user context), 450/15 min (app context)
- Stripe: 100 requests/second (burst), throttled beyond that

**Authentication Endpoints:**
- Login: 5 attempts per 15 minutes per username/IP
- Signup: 3 signups per hour per IP
- Password reset: 5 requests per hour per email/IP

**General API Endpoints:**
- Authenticated: 1,000-10,000 requests/hour
- Anonymous: 100-1,000 requests/hour
- Search/expensive operations: 10-100 requests/minute

### Response Format

```json
{
  "error": "Too many requests",
  "message": "You have exceeded the rate limit. Please try again later.",
  "retryAfter": 45,
  "limit": 100,
  "remaining": 0,
  "resetAt": "2025-12-06T12:00:00Z"
}
```

### Security Best Practices

- [ ] Rate limit authentication endpoints aggressively
- [ ] Use multiple factors for rate limiting (IP + user + fingerprint)
- [ ] Monitor for distributed attacks across IPs
- [ ] Implement exponential backoff for repeated violations
- [ ] Log and alert on rate limit bypass attempts
- [ ] Consider CAPTCHA after multiple violations
- [ ] Whitelist known good actors (verified partners, internal services)
- [ ] Implement circuit breakers for downstream service protection
- [ ] Test rate limiter performance under load
- [ ] Document rate limits clearly for API consumers
