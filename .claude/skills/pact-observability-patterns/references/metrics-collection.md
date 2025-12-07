# Metrics Collection Patterns

Comprehensive guide to production-grade metrics collection using RED/USE methods, Prometheus, and OpenTelemetry.

---

## 1. Metrics Fundamentals

### Understanding Metric Types

Modern observability platforms support four core metric types, each designed for specific measurement scenarios:

**Counter**: Monotonically increasing value tracking cumulative events
- Use for: Total requests processed, total errors encountered, total bytes transferred
- Example: `http_requests_total`, `database_queries_total`, `cache_hits_total`
- Calculation: Rate over time window (requests per second: `rate(http_requests_total[5m])`)
- Important: Counters never decrease (except on service restart), always increment

**Gauge**: Point-in-time value that can increase or decrease
- Use for: Current state, instantaneous measurements, resource utilization
- Example: `cpu_usage_percent`, `memory_bytes_used`, `active_connections`, `queue_length`
- Calculation: Current value, average over time, min/max analysis
- Important: Gauges represent "right now" state, not cumulative totals

**Histogram**: Distribution of values in configurable buckets
- Use for: Latency measurements, request/response sizes, duration tracking
- Example: `http_request_duration_seconds`, `db_query_duration_seconds`, `message_size_bytes`
- Provides: Count, sum, and bucket counts for percentile calculation (p50, p95, p99)
- Storage: More expensive than counters/gauges (stores multiple bucket values)
- Important: Buckets must be configured appropriately for your latency targets

**Summary**: Similar to histogram, calculates percentiles client-side
- Use for: Streaming percentile calculation when histogram buckets are impractical
- Example: `api_response_time_summary`
- Provides: Count, sum, and pre-calculated quantiles (0.5, 0.95, 0.99)
- Trade-off: Lower storage cost but less flexible for querying (percentiles cannot be re-aggregated across instances)
- Important: Less common than histograms in modern observability stacks

### RED Method for Request-Driven Services

The RED method provides a systematic approach to monitoring any request-driven service (APIs, web servers, microservices, message consumers). These three golden signals answer critical operational questions:

**Rate**: How many requests per second is the service processing?
- Metric: `http_requests_total` counter, calculate rate over time window
- Query: `rate(http_requests_total[5m])` (requests per second over 5 minutes)
- Purpose: Understand traffic volume, capacity planning, detect traffic spikes/drops
- Alert on: Unexpected traffic drops (possible outage) or sustained traffic above capacity

**Errors**: What percentage of requests are failing?
- Metric: `http_requests_total{status="5xx"}` divided by total requests
- Query: `sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100`
- Purpose: Service health indicator, SLO tracking
- Alert on: Error rate >1% (typical threshold, adjust based on SLA)

**Duration**: How long do requests take (latency distribution)?
- Metric: `http_request_duration_seconds` histogram
- Query: `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))`
- Purpose: Performance monitoring, SLO compliance (p95 latency <200ms)
- Alert on: p95 latency exceeding SLA threshold

**When to use RED**: APIs, web applications, microservices, RPC servers, GraphQL endpoints, message queue consumers (treat each message as a "request").

### USE Method for Resource Monitoring

The USE method focuses on infrastructure resource monitoring (CPU, memory, network, disk, database connections). These three metrics identify resource bottlenecks:

**Utilization**: Percentage of resource capacity currently in use
- Metrics: `cpu_usage_percent`, `memory_usage_percent`, `disk_usage_percent`
- Purpose: Identify resources approaching capacity limits
- Alert on: Sustained utilization >80% (provision more capacity)

**Saturation**: Queue length or amount of work waiting for the resource
- Metrics: `db_connection_pool_wait_count`, `request_queue_length`, `disk_io_wait_time`
- Purpose: Identify resource contention even when utilization appears normal
- Alert on: Non-zero saturation (work is being delayed)

**Errors**: Count of resource-related failures
- Metrics: `db_connection_errors_total`, `disk_io_errors_total`, `oom_kills_total`
- Purpose: Detect resource failures that impact service reliability
- Alert on: Any errors (indicates resource exhaustion or hardware issues)

**When to use USE**: Hosts, virtual machines, containers, databases, caches, message queues, connection pools, thread pools.

### RED vs USE Decision Guide

```
START: Choose metrics strategy

├─ Are you monitoring a REQUEST-DRIVEN service?
│  └─ YES → Use RED Method
│     - APIs (REST, GraphQL, gRPC)
│     - Web applications
│     - Microservices
│     - Message consumers (each message = request)

├─ Are you monitoring a RESOURCE?
│  └─ YES → Use USE Method
│     - Servers (CPU, memory, disk, network)
│     - Databases (connection pools, query execution)
│     - Caches (Redis, Memcached)
│     - Message queues (broker resources)

└─ Complex service with BOTH request handling AND resource constraints?
   └─ Use BOTH RED and USE
      - RED for application-level metrics (API performance)
      - USE for resource-level metrics (database connections, cache memory)
```

---

## 2. Prometheus Implementation

Prometheus is the industry-standard metrics platform, graduated CNCF project with widespread adoption. It uses a pull-based model where Prometheus scrapes metrics from your application's `/metrics` endpoint.

### Metric Naming Conventions

Following Prometheus best practices ensures consistent, queryable metrics across your infrastructure:

**Naming Format**:
- Lowercase with underscores: `http_requests_total`, `db_query_duration_seconds`
- Include unit suffix: `_seconds`, `_bytes`, `_total` (counters), `_ratio` (0-1 values)
- Avoid redundancy: ❌ `api_http_requests_total` (redundant), ✅ `http_requests_total`

**Standard Suffixes**:
- `_total`: Counters (e.g., `http_requests_total`, `errors_total`)
- `_seconds`: Duration (e.g., `http_request_duration_seconds`)
- `_bytes`: Size (e.g., `response_size_bytes`)
- `_ratio`: Ratios between 0-1 (e.g., `cache_hit_ratio`)
- `_percent`: Percentages 0-100 (less common, prefer `_ratio`)

### Label Design Patterns

Labels enable multi-dimensional metrics analysis but require careful design to avoid cardinality explosion:

**Good Labels** (low cardinality, bounded values):
- `method="POST"` (limited to HTTP methods: GET, POST, PUT, DELETE, PATCH)
- `endpoint="/api/users"` (limited to your API routes)
- `status="200"` (limited to HTTP status codes: 200, 201, 400, 404, 500, etc.)
- `environment="production"` (limited to: production, staging, development)
- `version="v1.2.3"` (limited to deployed versions)

**Bad Labels** (high cardinality, unbounded values):
- ❌ `user_id="12345"` (unbounded, millions of unique users)
- ❌ `request_id="abc-123-def"` (unbounded, every request unique)
- ❌ `ip_address="192.168.1.1"` (unbounded, thousands of IPs)
- ❌ `timestamp="2025-12-07T10:30:00Z"` (unbounded, every second unique)

**Why Cardinality Matters**: Each unique label combination creates a new time series. High-cardinality labels create millions of time series, causing:
- Memory explosion (Prometheus OOM errors)
- Query performance degradation
- Cardinality limit errors ("too many metrics")

**Rule of Thumb**: Label cardinality should be <100 unique values per label. Total unique label combinations should be <10,000 per metric.

### Histogram Bucket Selection

Histogram buckets determine percentile accuracy. Choose buckets based on your SLA targets:

**Latency-Based Buckets** (for API/database duration):
```javascript
buckets: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
// Covers: 5ms (fast cache hit) → 10s (slow database query)
// Good for: APIs with <1s SLA target
```

**Size-Based Buckets** (for request/response payloads):
```javascript
buckets: [100, 1000, 10000, 100000, 1000000, 10000000]
// Covers: 100 bytes → 10 MB
// Good for: Payload size monitoring
```

**Bucket Design Principles**:
- Include boundaries around your SLA targets (if p95 SLA is 200ms, include buckets: 0.1, 0.2, 0.3, 0.5)
- Use logarithmic scaling for wide ranges (0.01, 0.1, 1, 10)
- More buckets = better accuracy but higher storage cost
- Prometheus automatically adds `+Inf` bucket (counts all observations)

### Node.js - prom-client

```javascript
// metrics.js - Prometheus metrics setup
// Location: src/observability/metrics.js
// Used by: Express middleware (src/middleware/metricsMiddleware.js)
// Dependencies: prom-client (npm install prom-client)

const promClient = require('prom-client');

// Enable default system metrics (CPU, memory, event loop lag, garbage collection)
promClient.collectDefaultMetrics({
  timeout: 5000, // Collect every 5 seconds
  prefix: 'payment_service_' // Namespace for default metrics
});

// RED Metrics for API Monitoring

// Rate: Total requests counter
const httpRequestsTotal = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'endpoint', 'status']
});

// Duration: Request latency histogram
const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'endpoint'],
  buckets: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5]
});

// USE Metrics for Resource Monitoring

// Utilization: Active database connections gauge
const dbConnectionsActive = new promClient.Gauge({
  name: 'db_connections_active',
  help: 'Number of active database connections',
  labelNames: ['pool', 'state'] // state: idle, active, waiting
});

// Saturation: Connection pool wait time
const dbConnectionWaitDuration = new promClient.Histogram({
  name: 'db_connection_wait_duration_seconds',
  help: 'Time waiting for database connection',
  buckets: [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1]
});

// Errors: Connection errors counter
const dbConnectionErrors = new promClient.Counter({
  name: 'db_connection_errors_total',
  help: 'Total database connection errors',
  labelNames: ['pool', 'error_type']
});

// Express Middleware to Instrument Requests
function metricsMiddleware(req, res, next) {
  const start = Date.now();

  // Capture response finish event
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000; // Convert to seconds
    const endpoint = req.route?.path || 'unknown'; // Normalize endpoint (avoid high cardinality)

    // Record request count (Rate)
    httpRequestsTotal.inc({
      method: req.method,
      endpoint: endpoint,
      status: res.statusCode
    });

    // Record request duration (Duration)
    httpRequestDuration.observe({
      method: req.method,
      endpoint: endpoint
    }, duration);
  });

  next();
}

// Metrics Endpoint for Prometheus Scraping
async function metricsHandler(req, res) {
  res.set('Content-Type', promClient.register.contentType);
  const metrics = await promClient.register.metrics();
  res.end(metrics);
}

module.exports = {
  httpRequestsTotal,
  httpRequestDuration,
  dbConnectionsActive,
  dbConnectionWaitDuration,
  dbConnectionErrors,
  metricsMiddleware,
  metricsHandler
};
```

**Usage in Express App**:
```javascript
const express = require('express');
const { metricsMiddleware, metricsHandler } = require('./observability/metrics');

const app = express();

// Apply metrics middleware to all routes
app.use(metricsMiddleware);

// Expose /metrics endpoint for Prometheus
app.get('/metrics', metricsHandler);

app.listen(3000);
```

### Python - prometheus_client

```python
# metrics.py - Prometheus metrics setup
# Location: src/observability/metrics.py
# Used by: Flask middleware (src/middleware.py)
# Dependencies: prometheus_client (pip install prometheus-client)

from prometheus_client import Counter, Histogram, Gauge, start_http_server, generate_latest, CONTENT_TYPE_LATEST
import time

# RED Metrics for API Monitoring

# Rate: Total requests counter
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

# Duration: Request latency histogram
http_request_duration = Histogram(
    'http_request_duration_seconds',
    'Duration of HTTP requests in seconds',
    ['method', 'endpoint'],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5]
)

# USE Metrics for Resource Monitoring

# Utilization: Active database connections
db_connections_active = Gauge(
    'db_connections_active',
    'Number of active database connections',
    ['pool', 'state']
)

# Errors: Connection errors counter
db_connection_errors = Counter(
    'db_connection_errors_total',
    'Total database connection errors',
    ['pool', 'error_type']
)

# Flask Middleware for Request Instrumentation
def metrics_middleware():
    """Flask before/after request handlers for metrics collection"""
    from flask import request, g

    @app.before_request
    def before_request():
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            endpoint = request.endpoint or 'unknown'

            # Record request count (Rate)
            http_requests_total.labels(
                method=request.method,
                endpoint=endpoint,
                status=response.status_code
            ).inc()

            # Record request duration (Duration)
            http_request_duration.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(duration)

        return response

# Metrics Endpoint for Prometheus Scraping
def metrics_handler():
    """Flask route handler for /metrics endpoint"""
    from flask import Response
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
```

**Usage in Flask App**:
```python
from flask import Flask
from observability.metrics import metrics_middleware, metrics_handler

app = Flask(__name__)

# Apply metrics middleware
metrics_middleware()

# Expose /metrics endpoint
app.route('/metrics')(metrics_handler)

if __name__ == '__main__':
    app.run(port=5000)
```

### Java - Micrometer

```java
// MetricsConfiguration.java - Micrometer metrics setup
// Location: src/main/java/com/example/observability/MetricsConfiguration.java
// Used by: Spring Boot application (auto-configured via Spring Boot Actuator)
// Dependencies: micrometer-registry-prometheus (Maven/Gradle)

package com.example.observability;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.HandlerInterceptor;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

@Configuration
public class MetricsInterceptor implements HandlerInterceptor {

    private final MeterRegistry registry;

    public MetricsInterceptor(MeterRegistry registry) {
        this.registry = registry;
    }

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        request.setAttribute("startTime", System.currentTimeMillis());
        return true;
    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) {
        long startTime = (long) request.getAttribute("startTime");
        long duration = System.currentTimeMillis() - startTime;

        String endpoint = request.getRequestURI(); // Normalize to avoid high cardinality
        String method = request.getMethod();
        int status = response.getStatus();

        // RED Metrics

        // Rate: Total requests counter
        Counter.builder("http.requests.total")
            .tag("method", method)
            .tag("endpoint", endpoint)
            .tag("status", String.valueOf(status))
            .description("Total number of HTTP requests")
            .register(registry)
            .increment();

        // Duration: Request latency timer (histogram)
        Timer.builder("http.request.duration")
            .tag("method", method)
            .tag("endpoint", endpoint)
            .description("Duration of HTTP requests")
            .publishPercentiles(0.5, 0.95, 0.99) // p50, p95, p99
            .register(registry)
            .record(duration, java.util.concurrent.TimeUnit.MILLISECONDS);
    }
}
```

**Spring Boot Configuration** (exposes /actuator/prometheus):
```yaml
# application.yml
management:
  endpoints:
    web:
      exposure:
        include: prometheus, health, metrics
  metrics:
    export:
      prometheus:
        enabled: true
```

---

## 3. OpenTelemetry Metrics

OpenTelemetry Metrics API provides vendor-neutral instrumentation that exports to any backend (Prometheus, DataDog, New Relic, Grafana Cloud).

### OTel Metrics vs Prometheus Client

**Prometheus Client** (prom-client, prometheus_client):
- Pull-based: Prometheus scrapes `/metrics` endpoint
- Prometheus-specific: Tight coupling to Prometheus ecosystem
- Use when: Single backend (Prometheus), simpler setup

**OpenTelemetry Metrics** (@opentelemetry/sdk-metrics):
- Push-based: Application pushes metrics to collector/backend
- Vendor-neutral: Export to any backend via OTLP protocol
- Use when: Multi-backend flexibility (Prometheus + DataDog), unified observability stack

**Recommendation**: Use OpenTelemetry for new projects (future-proof, vendor flexibility). Use Prometheus client for existing Prometheus-only setups.

### Semantic Conventions for Consistent Attribute Names

OpenTelemetry semantic conventions define standard attribute names for consistency across services:

**HTTP Metrics**:
- `http.method`: GET, POST, PUT, DELETE
- `http.status_code`: 200, 404, 500
- `http.route`: /api/users, /api/orders/{id}
- `http.scheme`: http, https

**Database Metrics**:
- `db.system`: postgresql, mysql, mongodb
- `db.operation`: SELECT, INSERT, UPDATE
- `db.name`: Database name

**See**: https://opentelemetry.io/docs/specs/semconv/

### Node.js - OpenTelemetry Metrics SDK

```javascript
// otel-metrics.js - OpenTelemetry metrics setup
// Location: src/observability/otel-metrics.js
// Used by: Application initialization (src/index.js)
// Dependencies: @opentelemetry/sdk-metrics, @opentelemetry/exporter-prometheus

const { MeterProvider, PeriodicExportingMetricReader } = require('@opentelemetry/sdk-metrics');
const { PrometheusExporter } = require('@opentelemetry/exporter-prometheus');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

// Configure Prometheus exporter (pull-based scraping on port 9464)
const prometheusExporter = new PrometheusExporter({
  port: 9464,
  endpoint: '/metrics'
});

// Create meter provider with service metadata
const meterProvider = new MeterProvider({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'payment-service',
    [SemanticResourceAttributes.SERVICE_VERSION]: '1.2.3'
  }),
  readers: [new PeriodicExportingMetricReader({ exporter: prometheusExporter })]
});

// Get meter for this service
const meter = meterProvider.getMeter('payment-service');

// RED Metrics using OpenTelemetry semantic conventions

const httpRequestsTotal = meter.createCounter('http.requests.total', {
  description: 'Total HTTP requests',
  unit: '1' // Dimensionless (count)
});

const httpRequestDuration = meter.createHistogram('http.request.duration', {
  description: 'HTTP request duration',
  unit: 's', // Seconds
  advice: {
    explicitBucketBoundaries: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5]
  }
});

// Express middleware using OpenTelemetry metrics
function otelMetricsMiddleware(req, res, next) {
  const start = Date.now();

  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    const route = req.route?.path || 'unknown';

    // Use semantic conventions for attributes
    httpRequestsTotal.add(1, {
      'http.method': req.method,
      'http.route': route,
      'http.status_code': res.statusCode
    });

    httpRequestDuration.record(duration, {
      'http.method': req.method,
      'http.route': route
    });
  });

  next();
}

module.exports = { otelMetricsMiddleware };
```

---

## 4. Custom Business Metrics

Beyond infrastructure metrics, track domain-specific business outcomes to measure what matters to your organization.

### Domain-Specific Metrics Examples

**E-commerce**:
- `orders_total` (counter): Total orders placed
- `revenue_usd_total` (counter): Total revenue in USD
- `cart_abandonment_rate` (gauge): Percentage of abandoned carts
- `average_order_value_usd` (gauge): Average order value

**SaaS Platform**:
- `signups_total` (counter): Total user registrations
- `active_users` (gauge): Currently active users
- `subscription_churn_rate` (gauge): Monthly churn percentage
- `feature_usage_total` (counter): Feature adoption tracking

**API Platform**:
- `api_calls_by_customer` (counter): API usage per customer
- `quota_usage_percent` (gauge): Customer quota consumption
- `rate_limit_exceeded_total` (counter): Rate limit violations

### SLO/SLI Tracking

**Service Level Indicators (SLIs)**: Quantitative measures of service quality
- Availability: Percentage of successful requests (e.g., 99.9%)
- Latency: Percentage of requests under threshold (e.g., 95% <200ms)
- Error rate: Percentage of failed requests (e.g., <1%)

**Service Level Objectives (SLOs)**: Target values for SLIs
- "99.9% of requests succeed" (availability SLO)
- "95% of requests complete in <200ms" (latency SLO)
- "Error rate <1%" (error rate SLO)

**Error Budget**: Allowed failures based on SLO
- 99.9% availability = 0.1% allowed downtime = 43 minutes/month
- Track error budget consumption to balance feature velocity vs reliability

**Example - SLO Tracking**:
```javascript
// Calculate availability SLI
const availabilitySLI = meter.createCounter('slo.availability.requests', {
  description: 'Requests for availability SLO calculation'
});

// Track successful and failed requests
if (response.statusCode < 500) {
  availabilitySLI.add(1, { result: 'success' });
} else {
  availabilitySLI.add(1, { result: 'failure' });
}

// Query for availability percentage
// success_rate = sum(rate(slo_availability_requests{result="success"}[30d])) /
//                sum(rate(slo_availability_requests[30d]))
```

---

## 5. APM Integration

### Prometheus + Grafana (Self-Hosted)

**Setup**:
1. Expose `/metrics` endpoint in application (Prometheus client or OTel exporter)
2. Configure Prometheus to scrape metrics (prometheus.yml)
3. Add Prometheus as data source in Grafana
4. Create dashboards with PromQL queries

**prometheus.yml**:
```yaml
global:
  scrape_interval: 15s # Scrape every 15 seconds

scrape_configs:
  - job_name: 'payment-service'
    static_configs:
      - targets: ['localhost:9464'] # Application /metrics endpoint
        labels:
          environment: 'production'
          service: 'payment-service'
```

**Grafana Dashboard PromQL Queries**:
```promql
# Request rate (requests per second)
rate(http_requests_total[5m])

# Error rate (percentage)
sum(rate(http_requests_total{status=~"5.."}[5m])) /
sum(rate(http_requests_total[5m])) * 100

# P95 latency (95th percentile)
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint)
)

# Active database connections
sum(db_connections_active) by (state)
```

### DataDog Metrics Integration

**Setup** (using OpenTelemetry):
```javascript
const { OTLPMetricExporter } = require('@opentelemetry/exporter-metrics-otlp-http');

const datadogExporter = new OTLPMetricExporter({
  url: 'https://api.datadoghq.com/api/v2/otlp/v1/metrics',
  headers: {
    'DD-API-KEY': process.env.DATADOG_API_KEY
  }
});

const meterProvider = new MeterProvider({
  readers: [new PeriodicExportingMetricReader({ exporter: datadogExporter })]
});
```

**Features**:
- Automatic dashboard creation for standard metrics
- Anomaly detection (ML-based alerts)
- Unified metrics, logs, traces in single platform

### New Relic Metrics Integration

**Setup** (using OpenTelemetry):
```javascript
const { OTLPMetricExporter } = require('@opentelemetry/exporter-metrics-otlp-http');

const newRelicExporter = new OTLPMetricExporter({
  url: 'https://otlp.nr-data.net:4318/v1/metrics',
  headers: {
    'api-key': process.env.NEW_RELIC_LICENSE_KEY
  }
});

const meterProvider = new MeterProvider({
  readers: [new PeriodicExportingMetricReader({ exporter: newRelicExporter })]
});
```

**NRQL Query Example** (New Relic Query Language):
```sql
SELECT rate(sum(http.requests.total), 1 minute)
FROM Metric
WHERE service.name = 'payment-service'
FACET http.method, http.route
```

### Alerting Based on Metrics

**Threshold Alerts** (static thresholds):
- CPU usage >80% for 5 minutes
- Error rate >5% for 2 minutes
- p95 latency >500ms for 3 minutes

**Anomaly Detection** (ML-based):
- Request rate deviates >3 standard deviations from historical baseline
- Error rate spike compared to last 7 days

**Alert Fatigue Reduction**:
- Group related alerts (avoid 100 alerts for same incident)
- De-duplicate alerts (suppress repeat alerts within 15 minutes)
- Intelligent routing (route database alerts to database team, API alerts to backend team)

---

## Summary

Effective metrics collection requires:

1. **Choose the right method**: RED for request-driven services, USE for resource monitoring
2. **Design metrics carefully**: Low-cardinality labels, appropriate histogram buckets, semantic naming
3. **Instrument systematically**: Use OpenTelemetry for vendor neutrality, or Prometheus client for simplicity
4. **Track business outcomes**: Beyond infrastructure metrics, measure domain-specific KPIs
5. **Visualize and alert**: Grafana dashboards for visualization, threshold and anomaly-based alerting

**Next Steps**:
- See `logging-patterns.md` for structured logging implementation
- See `distributed-tracing.md` for OpenTelemetry tracing setup
- See `../templates/observability-stack-setup.md` for complete stack deployment
