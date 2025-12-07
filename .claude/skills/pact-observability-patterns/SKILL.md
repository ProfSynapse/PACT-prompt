---
name: pact-observability-patterns
description: |
  CODE PHASE: Observability patterns for logging, metrics, and distributed tracing - structured
  logging with correlation IDs, metrics collection (RED/USE methods), distributed tracing via
  OpenTelemetry, and APM platform integration.

  Use when implementing: structured JSON logging, correlation ID propagation, Prometheus metrics,
  OpenTelemetry instrumentation (auto/manual), distributed tracing, W3C Trace Context, APM integration
  (DataDog, New Relic, Application Insights, Grafana), log aggregation (ELK, Loki), metrics dashboards,
  trace sampling strategies, or correlating logs/metrics/traces.

  Activation keywords: observability, logging, metrics, tracing, monitoring, telemetry, OpenTelemetry,
  Prometheus, correlation IDs, distributed tracing, Jaeger, APM, structured logging, RED method, USE
  method, Grafana, DataDog, New Relic, Loki, sampling.

  DO NOT use for: security logging/audit patterns (use pact-security-patterns), testing observability
  code (use pact-testing-patterns), infrastructure monitoring setup (use cloud provider docs).
allowed-tools:
  - Read
  - mcp__sequential-thinking__sequentialthinking
metadata:
  phase: "Code"
  version: "1.0.0"
  updated: "2025-12-07"
  primary-agents:
    - pact-backend-coder
    - pact-database-engineer
    - pact-frontend-coder
---

# PACT Observability Patterns Skill

## Overview

Observability is the ability to understand the internal state of a system by examining its external outputs: logs, metrics, and traces. Unlike traditional monitoring (which asks "is the system up?"), observability enables teams to ask novel questions about system behavior without predicting failure modes in advance.

### What is Observability?

Observability provides visibility into production systems through three complementary data types:
- **Logs**: Detailed event records explaining what happened at specific points in time
- **Metrics**: Numerical measurements of system behavior aggregated over time windows
- **Traces**: Request flow visualization showing how operations propagate through distributed systems

Modern observability goes beyond passive monitoring to enable active debugging of complex distributed systems through correlation across these three pillars.

### Observability in the PACT Framework

In the CODE phase, observability instrumentation should be implemented alongside application logic, not added as an afterthought. This skill guides implementation across all CODE phase domains:
- **Backend services**: Structured logging, RED metrics, distributed tracing spans
- **Database operations**: Query performance metrics, slow query logging, connection pool monitoring
- **APIs**: Request/response logging, endpoint-level metrics, trace context propagation

Proper observability implementation during CODE phase enables effective validation during TEST phase and supports production debugging.

### When to Use This Skill

Use this skill when:
- Implementing structured logging in backend services
- Collecting metrics for APIs and database operations
- Setting up distributed tracing for microservices
- Choosing APM platforms (DataDog, New Relic, Application Insights, Grafana)
- Selecting log aggregation systems (ELK, Loki, DataDog Logs)
- Integrating OpenTelemetry instrumentation
- Correlating logs, metrics, and traces for unified debugging

### Integration with Other Skills

This skill provides observability implementation patterns. For related concerns, see:
- **pact-security-patterns**: Secure logging (PII redaction, audit logs, sensitive data handling)
- **pact-testing-patterns**: Testing observability instrumentation (verify metrics, logs, traces)
- **pact-api-design**: API-specific observability patterns (request/response logging, health checks)
- **pact-backend-patterns**: Backend-specific patterns (service layer logging, error handling integration)
- **pact-database-patterns**: Database-specific patterns (query monitoring, connection pool metrics)

## Quick Reference: The Three Pillars

Understanding when to use logs, metrics, or traces is critical for effective observability implementation.

### Metrics - What is Happening

**Use metrics when** you need to understand system health in real-time or identify trends over time.

Metrics answer questions like:
- Is the system healthy right now?
- Are error rates increasing?
- Is latency within acceptable ranges?
- Are we approaching capacity limits?

**Examples**:
- Request rate (requests per second by endpoint)
- Error rate (percentage of 5xx responses)
- Latency percentiles (p50, p95, p99 response times)
- CPU utilization, memory usage, disk I/O
- Connection pool active connections
- Queue depth, message processing rate

**Tools**: Prometheus, OpenTelemetry Metrics, DataDog, New Relic, Grafana

**Key characteristics**:
- Aggregated numerical data over time windows
- Low storage overhead (time-series data)
- Ideal for dashboards and alerting
- Support dimensional analysis (grouping by endpoint, status, method)

### Logs - What Happened

**Use logs when** you need to understand specific events or debug individual request failures.

Logs answer questions like:
- What went wrong with this specific request?
- What was the exact error message?
- What business event occurred?
- What actions did this user take?

**Examples**:
- Error details with stack traces
- Business events ("Order #12345 shipped")
- Audit trails (user login attempts)
- User actions (button clicks, form submissions)
- External API request/response payloads
- Database query execution details

**Tools**: Pino, Winston, Loguru, ELK Stack, Grafana Loki, DataDog Logs

**Key characteristics**:
- Detailed event records with full context
- Higher storage overhead than metrics
- Searchable and filterable by fields
- Essential for root cause analysis

### Traces - Why It Happened

**Use traces when** you need to understand request flow across services or identify latency bottlenecks.

Traces answer questions like:
- Which service is causing the slowdown?
- How does a request flow through the system?
- Where in the call chain did the error occur?
- Why is this endpoint slower than expected?

**Examples**:
- Request flow across 10+ microservices
- Latency breakdown by service and operation
- Database query duration within request context
- External API call performance
- Dependency visualization and service maps

**Tools**: OpenTelemetry, Jaeger, Zipkin, DataDog APM, New Relic, Grafana Tempo

**Key characteristics**:
- Hierarchical span structure representing operations
- Context propagation across service boundaries
- Sampling required for cost management
- Best for understanding distributed system behavior

### Decision Tree: Which Pillar to Use

```
START: Observability need

├─ Need to know "is the system healthy right now?"
│  └─ Use METRICS (dashboards, alerts, SLO tracking)
│     Example: Create Grafana dashboard with request rate, error rate, p95 latency

├─ Need to know "what went wrong with this specific request?"
│  └─ Use LOGS (error details, context, stack traces)
│     Example: Search logs for correlationId=req_abc123 to see error details

├─ Need to know "which service caused the latency?"
│  └─ Use TRACES (request flow, span durations, dependency analysis)
│     Example: Filter traces for /checkout endpoint >2s to find slow database query

└─ Need complete context for production incident?
   └─ Use ALL THREE (metric alert → find slow trace → read correlated logs)
      Workflow: Alert fires for high p95 latency → Find slowest traces →
                Identify slow span (database query) → Read logs for that traceId →
                Discover missing database index
```

### Unified Debugging Workflow

The three pillars work together to support comprehensive debugging:

1. **Metric alert identifies symptom**: Dashboard shows API latency p95 increased from 100ms to 2s
2. **Trace identifies bottleneck**: Filtering traces for slow requests reveals database query taking 1.8s
3. **Logs provide root cause**: Reading logs for that trace ID shows "Missing index on users.email column"

This unified workflow requires correlation between pillars:
- Logs must include `traceId` and `spanId` fields from OpenTelemetry context
- Traces must use same labels/attributes as metrics (service name, endpoint)
- Metrics dashboards must support click-through to related traces

**Implementation requirement**: Every log entry should include OpenTelemetry trace context for correlation. See "OpenTelemetry Integration" section below.

## Available MCP Tools

### sequential-thinking

**Purpose**: Complex observability architecture decisions requiring systematic trade-off analysis

**When to use**:
- Choosing between APM platforms (DataDog, New Relic, Application Insights, Grafana) with competing priorities (cost, features, ease of use, vendor lock-in)
- Designing sampling strategies for distributed tracing at scale (balancing cost vs visibility)
- Evaluating log aggregation systems (ELK, Loki, cloud providers) based on search needs, volume, budget
- Balancing observability cost vs visibility needs (retention policies, sampling rates, indexing strategies)
- Planning observability architecture for multi-service systems (centralized vs decentralized, push vs pull)
- Resolving competing performance requirements (detailed logging vs latency impact, 100% tracing vs cost)

**Example prompt**:
```
I need to choose an APM platform for a microservices system with 15 services, 5-person DevOps team,
budget constraints ($5k/month max), and Azure-based infrastructure. Options: DataDog (powerful but
expensive, complex pricing), New Relic (all-in-one pricing, simpler but less customizable),
Application Insights (Azure-native, cost-effective but .NET-focused), Grafana Stack (free but
requires operational expertise). Trade-offs: cost predictability vs features, ease of use vs
customization, vendor lock-in vs integration depth. Let me systematically evaluate each option
considering team size, budget constraints, Azure integration needs, and long-term maintenance burden...
```

**When NOT to use**:
- Straightforward implementation of established patterns (structured logging with Pino, Prometheus metrics)
- Standard OpenTelemetry setup following official documentation
- Simple tool selection with clear winner (e.g., already using Azure? Use Application Insights)

### Fallback if sequential-thinking is unavailable

If the sequential-thinking MCP tool is not configured, use structured manual decision-making:

**Option 1: Weighted Criteria Matrix** (Recommended for complex decisions with multiple competing priorities)

1. List all options being considered (e.g., DataDog, New Relic, Application Insights, Grafana Stack)
2. Define evaluation criteria with weights based on project priorities:
   - Cost (30%): Monthly budget impact, pricing predictability
   - Ease of use (20%): Setup complexity, learning curve, team expertise required
   - Features (25%): Required capabilities (APM, logs, traces, alerting)
   - Integration (15%): Compatibility with existing infrastructure
   - Vendor lock-in risk (10%): Migration difficulty, data portability
3. Score each option 1-10 on each criterion
4. Calculate weighted total: (criterion score × weight) summed across all criteria
5. Compare totals, but also review for deal-breakers (e.g., option with highest score exceeds budget)

**Example matrix**:
```
Criteria              Weight   DataDog   New Relic   App Insights   Grafana
Cost                  30%      4 (1.2)   6 (1.8)     9 (2.7)        10 (3.0)
Ease of use           20%      6 (1.2)   8 (1.6)     7 (1.4)        4 (0.8)
Features              25%      10 (2.5)  8 (2.0)     6 (1.5)        7 (1.75)
Integration (Azure)   15%      7 (1.05)  6 (0.9)     10 (1.5)       6 (0.9)
Vendor lock-in        10%      4 (0.4)   5 (0.5)     6 (0.6)        9 (0.9)
-------------------------------------------------------------------
TOTAL                         6.35      6.8         7.7            7.35
```
Conclusion: Application Insights scores highest (7.7) due to Azure integration and cost-effectiveness, Grafana second (7.35) for low vendor lock-in and cost.

**Option 2: Pros/Cons with Decision Framework** (Faster for decisions with clear trade-offs)

1. List 2-3 finalist options after eliminating clear non-starters
2. Create pros/cons list for each option
3. Identify must-have requirements (e.g., "must integrate with Azure", "must stay under $5k/month")
4. Eliminate options that fail must-haves
5. For remaining options, identify key trade-off (e.g., cost vs features, ease of use vs customization)
6. Choose based on project context (e.g., choose simplicity if team is small, choose features if scale is critical)

**Option 3: Break Complex Decisions into Smaller Steps**

For overwhelming decisions with 5+ variables:

1. Make initial filtering decision: Narrow from 6 options to 2-3 finalists using one critical criterion (e.g., "budget <$5k/month" eliminates DataDog and New Relic at scale)
2. Prototype finalist options: Spend 2-4 hours setting up minimal viable implementation for each finalist
3. Evaluate prototypes against remaining criteria: Hands-on experience reveals hidden complexity, ease of use, integration friction
4. Make final decision based on prototype learnings

**Trade-off**: More time investment (4-8 hours) but reduces risk of choosing poorly based on marketing materials vs real-world experience.

**Documentation requirement**: Regardless of method chosen, document decision rationale in architecture docs or implementation notes for future reference and team alignment.

**See pact-backend-coder agent for invocation syntax and workflow integration.**

## OpenTelemetry Integration

### Why OpenTelemetry?

OpenTelemetry (OTel) is the industry standard for observability instrumentation in 2025:

- **W3C and CNCF standard**: Endorsed by World Wide Web Consortium and Cloud Native Computing Foundation
- **Vendor-neutral**: Single instrumentation works with any backend (DataDog, New Relic, Prometheus, Jaeger, Grafana)
- **Unified API**: Consistent interface for metrics, logs, and traces across languages
- **Universal adoption**: Supported by all major APM vendors and open-source tools
- **Active development**: Largest observability project with extensive community support

**Recommendation**: Use OpenTelemetry for all new observability instrumentation. Legacy instrumentation (vendor-specific SDKs, custom logging) should migrate to OpenTelemetry over time.

### Auto-Instrumentation vs Manual

**Auto-instrumentation** provides zero-code observability for common frameworks:
- **Coverage**: HTTP servers (Express, Flask, Spring Boot), database clients (PostgreSQL, MongoDB, MySQL), message queues (Kafka, RabbitMQ), external API calls (fetch, requests, HttpClient)
- **Benefits**: Immediate observability, no code changes, consistent instrumentation across services
- **Trade-offs**: Limited customization, generic span names, no business context

**Manual instrumentation** adds custom spans for business logic:
- **Use cases**: Business-critical operations, complex workflows, domain-specific context
- **Benefits**: Business context (order ID, user ID, payment amount), custom span names, fine-grained performance tracking
- **Trade-offs**: Code changes required, maintenance burden, risk of inconsistency

**Recommendation**: Start with auto-instrumentation to cover 80% of observability needs. Add manual instrumentation for business-critical paths requiring domain context.

### Initialization Best Practices

**Critical**: OpenTelemetry must initialize BEFORE framework imports. Instrumentation patches framework modules during import, so late initialization misses instrumentation.

```javascript
// ❌ WRONG: Framework imported before OpenTelemetry
const express = require('express');
const { NodeSDK } = require('@opentelemetry/sdk-node');
sdk.start(); // Too late, Express already imported

// ✅ CORRECT: OpenTelemetry initialized first
// File: tracing.js (loaded first)
const { NodeSDK } = require('@opentelemetry/sdk-node');
sdk.start();

// File: app.js (loaded after tracing)
require('./tracing'); // Initialize OpenTelemetry first
const express = require('express'); // Now Express will be instrumented
```

### Semantic Conventions

OpenTelemetry semantic conventions define standard attribute names for consistency across services and tools.

**Use semantic conventions for**:
- HTTP operations: `http.method`, `http.status_code`, `http.route`, `http.url`
- Database operations: `db.system`, `db.statement`, `db.operation`, `db.name`
- Messaging: `messaging.system`, `messaging.destination`, `messaging.operation`
- RPC: `rpc.system`, `rpc.service`, `rpc.method`

**Benefits**:
- APM tools automatically recognize and visualize standard attributes
- Consistent dashboards across services
- Cross-team collaboration with shared vocabulary
- Easier migration between APM platforms

**Reference**: https://opentelemetry.io/docs/specs/semconv/

### W3C Trace Context Propagation

W3C Trace Context is the universal standard for propagating trace context across service boundaries.

**traceparent header format**:
```
00-<trace-id>-<parent-span-id>-<trace-flags>

Example: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
         │  │                                │                │
         │  └─ Trace ID (128 bits)           └─ Parent Span   └─ Sampled (01)
         └─ Version (00)                        ID (64 bits)
```

**Automatic propagation**: OpenTelemetry SDKs automatically extract `traceparent` from incoming requests and inject it into outgoing requests (HTTP, gRPC, message queues).

**Benefits**:
- Single trace can span multiple vendors (request enters DataDog service, calls New Relic service, ends in open-source service)
- Replaces vendor-specific headers (X-B3-TraceId, X-Datadog-Trace-Id)
- Interoperability across heterogeneous systems

### OpenTelemetry Collector

The OpenTelemetry Collector is a vendor-neutral telemetry pipeline for receiving, processing, and exporting observability data.

**Deployment patterns**:
- **Agent mode**: Collector runs on same host as application, receives telemetry via localhost
- **Gateway mode**: Centralized collector receives telemetry from multiple applications, performs aggregation and routing

**Key capabilities**:
- **Batching**: Reduce network overhead by batching telemetry before export
- **Filtering**: Drop low-value telemetry to reduce costs (e.g., filter health check traces)
- **Routing**: Send different telemetry types to different backends (traces to Jaeger, metrics to Prometheus)
- **Sampling**: Implement tail sampling (keep errors/slow requests, sample normal traffic)
- **Transformation**: Modify attributes, rename fields, redact sensitive data

**Recommendation**: Use Collector in production for flexibility and cost control. Export directly from SDK for development simplicity.

**For implementation details**: See `references/distributed-tracing.md`

### Kubernetes Deployment Patterns

When deploying OpenTelemetry Collector in Kubernetes, choose a deployment pattern based on your data processing needs:

**Sidecar Pattern**: OTel Collector deployed as sidecar container alongside application pod
- **Use when**: Application-specific processing required, isolated failure domains preferred, fine-grained resource control needed
- **Trade-offs**: Higher resource overhead (one collector per pod), simpler networking (localhost communication), isolated configuration per application
- **Configuration**: Define collector container in pod spec, application sends telemetry to `localhost:4317`

**DaemonSet Pattern**: OTel Collector deployed per Kubernetes node
- **Use when**: Node-level metrics collection required (kubelet, cAdvisor), moderate traffic volume, want to reduce pod count
- **Trade-offs**: Medium resource overhead (one collector per node), efficient for node metrics, shared processing across pod workloads
- **Configuration**: Deploy as DaemonSet, applications send to node IP via downward API (`status.hostIP`)

**Deployment Pattern**: Centralized OTel Collector cluster
- **Use when**: High traffic requiring horizontal scaling, advanced processing pipelines needed (tail sampling, aggregation), want separation of concerns
- **Trade-offs**: Lowest resource overhead (shared infrastructure), requires load balancer, added network hop increases latency slightly
- **Configuration**: Deploy as Kubernetes Deployment with Service, applications send to service DNS name

**Hybrid Approach**: DaemonSet agents + Deployment gateway
- **Use when**: Best of both worlds needed: node metrics + centralized processing
- **Architecture**: DaemonSet collectors receive app telemetry and node metrics, forward to centralized Deployment for processing/export
- **Benefits**: Offloads heavy processing from node agents, enables tail sampling across all traffic, maintains node-level collection

**Recommendation**: Start with DaemonSet pattern for simplicity. Move to hybrid (DaemonSet + Deployment gateway) when implementing tail sampling or complex processing pipelines.

**Reference**: Official [OpenTelemetry Operator for Kubernetes](https://opentelemetry.io/docs/k8s-operator/) automates collector deployment and provides custom resources for configuration management.

## Observability Patterns by Domain

### API Observability

**Key Concerns**: Request/response logging, endpoint-level metrics, health checks, API gateway instrumentation

**Metrics** (RED method):
- Request rate: Requests per second by endpoint, method, status code
- Error rate: Percentage of 5xx responses by endpoint
- Duration: p50, p95, p99 latency by endpoint and method

**Logging**:
- Correlation IDs in headers (X-Correlation-ID) and log entries
- Request/response payloads (sanitized to remove PII/secrets)
- Error details with stack traces for 5xx responses
- Authentication failures and rate limit events

**Tracing**:
- API gateway spans as trace entry points
- Downstream service call spans (HTTP, database, external APIs)
- Span attributes: http.method, http.route, http.status_code

**See `pact-api-design` skill for**: API-specific health check patterns (/health vs /health/ready), API contract observability, versioning and deprecation monitoring

### Backend Observability

**Key Concerns**: Structured logging, business metrics, distributed tracing, service-level monitoring

**Metrics** (RED method for services):
- Service-level request rate, error rate, latency
- Resource utilization: CPU, memory, connection pools
- Business metrics: Orders per minute, signups per hour, revenue per day

**Logging**:
- Structured JSON logs with consistent field names (timestamp, level, message, service, traceId, spanId, correlationId)
- Business events: "Order #12345 placed", "User user_abc registered"
- Error context: Function name, input parameters, error message, stack trace

**Tracing**:
- Service spans wrapping business operations
- External API call spans with retry/timeout context
- Message queue producer/consumer spans

**See `pact-backend-patterns` skill for**: Service layer patterns, error handling strategies, middleware patterns, async processing integration

### Database Observability

**Key Concerns**: Query performance monitoring, connection pool health, slow query logging, transaction tracing

**Metrics** (USE method for databases):
- Query duration: p50, p95, p99 by operation type (SELECT, INSERT, UPDATE)
- Connection pool utilization: Active connections, wait time, idle connections
- Query count: Queries per second by operation type
- Transaction rollback rate

**Logging**:
- Slow query logs: Queries exceeding threshold (e.g., 100ms)
- Connection errors: Pool exhaustion, authentication failures, network timeouts
- Transaction context: Transaction ID, isolation level, duration

**Tracing**:
- Database operation spans: db.system, db.statement, db.operation, db.name
- Query parameter capture (sanitized)
- Connection pool acquisition time

**See `pact-database-patterns` skill for**: Query optimization strategies, connection pool configuration, index design for performance monitoring

## APM Platform Selection

### When to Use APM Platforms

**Choose commercial APM when**:
- Team lacks operational expertise to run open-source observability stack (Prometheus, Loki, Jaeger)
- Budget allows for per-host or per-GB pricing ($100-500/month for small deployments)
- Need unified platform with automatic correlation (logs, metrics, traces in single UI)
- Want managed infrastructure with guaranteed uptime SLAs
- Require advanced features (AI anomaly detection, automatic instrumentation, service maps)

**Choose open-source stack when**:
- Budget-constrained or high data volume (open-source storage costs 10x cheaper)
- Strong DevOps team comfortable operating Kubernetes-based infrastructure
- Need full control over data retention and privacy (on-premises requirements)
- Want to avoid vendor lock-in
- Existing Prometheus/Grafana expertise

### Platform Comparison

**DataDog**
- **Strengths**: Best-in-class infrastructure monitoring, 800+ integrations, powerful query language (DQL), advanced analytics
- **Weaknesses**: Complex pricing (per-host, per-GB, per-custom-metric), costs can spiral unpredictably, steep learning curve
- **Pricing**: APM $31-40/host/month, Logs $0.10/GB ingested + $1.70/million events indexed, Custom metrics volume-based
- **When to choose**: Complex multi-cloud infrastructure, dedicated DevOps team, need deep customization and integrations

**New Relic**
- **Strengths**: All-in-one pricing (per user + per GB), simpler UX, leading AI-powered insights, predictable costs
- **Weaknesses**: Vendor lock-in, less infrastructure monitoring depth than DataDog
- **Pricing**: Standard tier 1 user + 100 GB/month free, Pro $99/user/month + $0.35/GB, Enterprise $549/user/month + $0.50/GB
- **When to choose**: Want simplicity and predictable pricing, smaller teams (5-20 people), value AI-powered anomaly detection

**Azure Application Insights**
- **Strengths**: Native Azure integration (App Service, Functions, AKS), cost-effective for Azure workloads, automatic instrumentation for .NET
- **Weaknesses**: Less feature-rich than DataDog/New Relic, .NET-focused (other languages less mature)
- **Pricing**: First 5 GB/month free per subscription, $2.30/GB beyond free tier, Log Analytics $2.76/GB ingested
- **When to choose**: Azure-centric architecture, Microsoft/.NET stack, budget-conscious with Azure infrastructure

**Grafana Stack (LGTM: Loki, Grafana, Tempo, Mimir)**
- **Strengths**: Free (self-hosted), Kubernetes-native, 10x cheaper storage (object storage: S3, GCS), PromQL compatibility
- **Weaknesses**: Operational complexity, requires Kubernetes expertise, less polished UX than commercial APM
- **Pricing**: Free (infrastructure costs only: ~$0.02/GB S3 storage), Grafana Cloud managed option from $0.50/GB
- **When to choose**: Budget constraints, Kubernetes-heavy, strong DevOps team, existing Prometheus/Grafana expertise

### Decision Tree

```
START: Choose APM platform

├─ Azure-centric architecture?
│  └─ YES → Azure Application Insights (native integration, cost-effective for Azure)

├─ Complex multi-cloud infrastructure?
│  └─ YES → DataDog (800+ integrations, infrastructure monitoring depth)

├─ Budget-conscious with Kubernetes?
│  └─ YES → Grafana Stack (self-hosted, Kubernetes-native, 10x cheaper storage)

├─ Want simplicity and predictable pricing?
│  └─ YES → New Relic (all-in-one pricing, AI insights, simpler UX)

└─ Default → Grafana Stack for prototyping, evaluate commercial options for production
            (Start with Grafana Cloud managed to avoid operational burden)
```

**For detailed comparison**: See `references/metrics-collection.md` (APM integration section)

## Decision Tree: Which Reference to Use

### Implementing structured logging?

**→ See `references/logging-patterns.md`**

Coverage:
- JSON logging format and essential field conventions (timestamp, level, message, service, traceId, spanId, correlationId)
- Language-specific libraries (Pino for Node.js, Loguru for Python, Logback for Java, Serilog for .NET, zap for Go)
- Correlation ID generation and propagation strategies across service boundaries
- Log aggregation systems comparison (ELK Stack, Grafana Loki, DataDog Logs) with decision matrix
- Security: PII redaction patterns, async logging for performance, log sampling

### Collecting metrics?

**→ See `references/metrics-collection.md`**

Coverage:
- RED method (Rate, Errors, Duration) for request-driven services (APIs, web servers, microservices)
- USE method (Utilization, Saturation, Errors) for infrastructure resources (hosts, databases, caches)
- Prometheus implementation: Metric naming conventions, label design patterns (avoiding high cardinality), histogram bucket selection
- OpenTelemetry Metrics SDK: Vendor-neutral instrumentation, semantic conventions, multi-backend export
- APM platform integration: DataDog, New Relic, Application Insights with configuration examples
- Business metrics: Domain-specific metrics (signups, orders, revenue), SLO/SLI tracking

### Implementing distributed tracing?

**→ See `references/distributed-tracing.md`**

Coverage:
- OpenTelemetry auto-instrumentation (zero-code for Express, Flask, Spring Boot) and manual instrumentation for custom spans
- W3C Trace Context propagation: traceparent header format, context extraction/injection
- Sampling strategies: Head sampling (probabilistic, rate-limiting), tail sampling (error-based, latency-based, hybrid)
- Trace backends comparison: Jaeger (open-source, CNCF), Zipkin (legacy), Grafana Tempo (cost-effective), DataDog APM, New Relic
- Correlation with logs and metrics: Logging trace/span IDs, linking traces to metrics dashboards, unified debugging workflow

### Setting up complete observability stack?

**→ See `examples/express-observability-example.md`**

Coverage:
- OpenTelemetry + Prometheus + Jaeger + Grafana configuration
- Docker Compose setup for local development
- Production deployment considerations (sampling, security)

## Common Anti-Patterns

### 🚫 Logging PII and Secrets

**Problem**: Compliance violations (GDPR, HIPAA), security risks (credentials in logs), audit failures

**Bad example**:
```javascript
logger.info('User login', { email: 'user@example.com', password: 'secret123' }); // ❌ Password logged
logger.info('Payment processed', { creditCard: '4111111111111111' }); // ❌ PII logged
```

**Solution**: Implement PII redaction, use secret masking libraries

**Good example**:
```javascript
logger.info('User login', { email: maskEmail('user@example.com') }); // user@***
logger.info('Payment processed', { creditCardLast4: '1111' }); // Only last 4 digits
```

**See**: `pact-security-patterns` skill for secure logging patterns, audit log design

### 🚫 High-Cardinality Metrics Labels

**Problem**: Memory explosion (Prometheus stores one time-series per unique label combination), cardinality limit errors, OOM crashes

**Bad example**:
```javascript
// ❌ User IDs as labels (10M users = 10M time-series)
requestCounter.inc({ endpoint: '/api/users', userId: '12345' });

// ❌ Request IDs as labels (unbounded cardinality)
latencyHistogram.observe({ endpoint: '/checkout', requestId: 'req_abc123' }, 0.5);
```

**Solution**: Use labels for low-cardinality dimensions (endpoint, status, method), store high-cardinality data in logs

**Good example**:
```javascript
// ✅ Low-cardinality labels only
requestCounter.inc({ endpoint: '/api/users', method: 'GET', status: '200' });

// ✅ High-cardinality data in logs
logger.info('Request processed', { userId: '12345', requestId: 'req_abc123', duration: 0.5 });
```

**Cardinality limits**: Prometheus default ~10M time-series, DataDog ~1M custom metrics

### 🚫 100% Sampling in Production

**Problem**: Performance overhead (tracing adds latency), trace storage costs spiral, overwhelming trace backends

**Bad example**:
```javascript
// ❌ 100% sampling (all requests traced)
const sdk = new NodeSDK({
  sampler: new AlwaysOnSampler() // Traces every request
});
```

**Solution**: Probabilistic sampling (1-10% normal traffic) + tail sampling (always keep errors/slow requests)

**Good example**:
```javascript
// ✅ Probabilistic sampling: Keep 5% of traces
const sdk = new NodeSDK({
  sampler: new TraceIdRatioBasedSampler(0.05)
});

// ✅ Or configure tail sampling in OTel Collector (keep errors/slow, sample rest)
```

**Sampling guidelines**: Start with 1-5% probabilistic sampling, adjust based on volume and debugging needs

### 🚫 Unstructured Logs

**Problem**: Cannot query logs by fields, cannot aggregate across services, cannot correlate with traces, manual parsing required

**Bad example**:
```javascript
// ❌ Plain text logs
console.log('User user_12345 placed order order_67890 for $99.99'); // Unparseable
```

**Solution**: Use JSON structured logging with consistent field names

**Good example**:
```javascript
// ✅ Structured JSON logs
logger.info('Order placed', {
  userId: 'user_12345',
  orderId: 'order_67890',
  amount: 99.99,
  currency: 'USD'
}); // Queryable, aggregatable
```

### 🚫 Missing Correlation IDs

**Problem**: Cannot trace requests across services, cannot link related logs, debugging distributed failures is impossible

**Bad example**:
```javascript
// ❌ No correlation ID
app.get('/api/orders', async (req, res) => {
  logger.info('Fetching orders'); // Which request does this belong to?
  const orders = await orderService.getOrders();
  res.json(orders);
});
```

**Solution**: Generate correlation IDs at API gateway, propagate in headers, include in all logs

**Good example**:
```javascript
// ✅ Correlation ID middleware
app.use((req, res, next) => {
  req.correlationId = req.headers['x-correlation-id'] || uuidv4();
  res.setHeader('X-Correlation-ID', req.correlationId);
  next();
});

app.get('/api/orders', async (req, res) => {
  logger.info('Fetching orders', { correlationId: req.correlationId }); // Traceable
  const orders = await orderService.getOrders();
  res.json(orders);
});
```

### 🚫 No Sampling Strategy

**Problem**: Trace storage costs spiral with traffic growth, trace backends overwhelmed, wasted budget on low-value traces

**Solution**: Configure head or tail sampling based on volume and debugging needs

**Sampling strategies**:
- **Low traffic (<100 req/s)**: 100% sampling acceptable
- **Medium traffic (100-1000 req/s)**: 10% probabilistic sampling
- **High traffic (>1000 req/s)**: 1% probabilistic + tail sampling (errors/slow requests)

**See**: `references/distributed-tracing.md` for sampling configuration examples

## Integration with PACT Workflow

### Input from Architecture Phase

**From** `docs/architecture/`:
- Observability requirements and SLAs (e.g., "p95 latency <200ms", "99.9% uptime")
- APM platform selection (if made during architecture phase, otherwise decide during CODE)
- Log aggregation system choice (ELK, Loki, DataDog Logs)
- Metrics strategy: RED method for APIs, USE method for infrastructure
- Tracing requirements: Sampling rate (e.g., 5%), trace retention (e.g., 7 days)

**If architecture phase didn't specify observability stack**: Use decision trees in this skill to choose APM platform, log aggregation system, and sampling strategy during CODE phase.

### Output to Test Phase

**Create** `docs/implementation/observability-implementation.md` with:
- Observability instrumentation code locations (logging, metrics, tracing setup files)
- Metrics endpoints configured (e.g., `/metrics` for Prometheus scraping)
- Structured logging format and essential fields (timestamp, level, message, service, traceId, correlationId)
- Distributed tracing enabled: Auto-instrumentation frameworks, manual spans added
- APM platform integrated: DataDog agent installed, New Relic SDK configured, etc.
- Correlation strategy: How logs/metrics/traces are correlated (traceId in logs, shared labels)

**Hand off to** `pact-test-engineer` for validation with test scenarios:
- Verify metrics emission (request counter increments, latency histogram records values)
- Verify log output (structured JSON format, correlation IDs present, trace context included)
- Verify trace context propagation (W3C traceparent header propagated across services)
- Verify APM platform data ingestion (dashboards populate, traces visible in APM UI)

### Testing Observability Implementation

**See `pact-testing-patterns` skill for**:
- Testing metrics emission: Verify counters increment on API calls, histograms record latency
- Testing log output: Verify structured format, required fields present (timestamp, level, message, traceId)
- Testing trace context propagation: Verify traceparent header extracted from incoming requests, injected into outgoing requests
- Testing correlation: Verify logs include traceId/spanId from OpenTelemetry context
- Performance testing: Verify observability overhead <5% latency increase

### Agents Using This Skill

**pact-backend-coder**: Implements backend service observability (structured logging, RED metrics, distributed tracing spans)

**pact-database-engineer**: Implements database query monitoring (slow query logging, connection pool metrics, database operation spans)

**pact-frontend-coder**: Implements frontend observability (error tracking, Real User Monitoring, frontend performance metrics)

**pact-architect**: Designs observability architecture (APM platform selection, log aggregation system choice, sampling strategy, retention policies)

## Reference Files

Detailed implementation guidance:
- **references/logging-patterns.md**: Structured logging fundamentals, language-specific libraries, correlation ID propagation, log aggregation systems, security and performance
- **references/metrics-collection.md**: Metrics types (counter, gauge, histogram), RED/USE methods, Prometheus implementation, OpenTelemetry Metrics SDK, business metrics, APM integration
- **references/distributed-tracing.md**: Distributed tracing fundamentals, OpenTelemetry auto/manual instrumentation, W3C Trace Context, sampling strategies, trace backends, correlation

## Examples

- **examples/express-observability-example.md**: Full Express.js example demonstrating unified observability with OpenTelemetry, structured logging, Prometheus metrics, Docker Compose stack, and complete debugging scenario
