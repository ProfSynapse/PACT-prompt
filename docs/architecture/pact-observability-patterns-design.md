# PACT Observability Patterns Skill - Architecture Design

**Date**: 2025-12-07
**Phase**: Architect
**GitHub Issue**: #5
**Preparation Document**: `/Users/mj/Sites/collab/PACT-prompt/docs/preparation/pact-observability-patterns-research.md`

---

## Executive Summary

This document specifies the complete architecture for the `pact-observability-patterns` skill, a CODE phase cross-cutting skill providing comprehensive observability guidance for logging, metrics, and distributed tracing. The skill positions OpenTelemetry as the industry-standard instrumentation framework and provides practical patterns for APM platform integration and log aggregation systems.

**Architecture Highlights**:
- SKILL.md main file with progressive disclosure (~3,500 words)
- Three comprehensive reference files covering logging, metrics, and tracing (~2,500 words each)
- Multi-language code examples (Node.js, Python, Java minimum)
- Decision trees for tool selection (APM platforms, log aggregation systems)
- Integration with existing pact-backend-coder, pact-api-design, and pact-database-engineer agents
- One practical template for observability stack setup
- One complete implementation example demonstrating full observability integration

---

## 1. Skill Metadata

### 1.1 Frontmatter

```yaml
---
name: pact-observability-patterns
description: |
  CODE PHASE (Cross-cutting): Observability patterns for logging, metrics, and distributed tracing.

  Provides structured logging patterns, metrics collection strategies (RED/USE method),
  distributed tracing implementation (OpenTelemetry), APM platform integration, and
  log aggregation system guidance.

  Use when: implementing logging, collecting metrics, setting up distributed tracing,
  integrating APM tools (DataDog, New Relic, Application Insights), choosing log
  aggregation systems (ELK, Loki), implementing OpenTelemetry instrumentation,
  correlating logs/metrics/traces, or when user mentions: observability, logging,
  metrics, tracing, monitoring, APM, telemetry, OpenTelemetry, Prometheus, structured
  logging, correlation IDs, distributed tracing, Jaeger, Grafana, DataDog, New Relic.

  Use for: structured logging, JSON logging, correlation IDs, log aggregation, metrics
  collection, Prometheus integration, RED method, USE method, distributed tracing,
  W3C Trace Context, OpenTelemetry setup, APM integration, observability strategy.

  DO NOT use for: security logging patterns (use pact-security-patterns), testing
  observability instrumentation (use pact-testing-patterns), infrastructure monitoring
  (use cloud provider documentation).
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
```

### 1.2 Skill Purpose

The `pact-observability-patterns` skill consolidates fragmented observability guidance currently scattered across three skills (pact-api-design, pact-backend-patterns, pact-database-patterns) into a comprehensive reference focused on production-grade observability implementation. It emphasizes OpenTelemetry as the 2025 industry standard while providing vendor-neutral guidance for APM and logging platforms.

---

## 2. SKILL.md Structure

### 2.1 Section Breakdown (~3,500 words total)

#### Section 1: Overview (~300 words)

**Purpose**: Establish observability context within PACT framework and define skill scope.

**Content**:
- Definition of observability vs monitoring
- Importance in CODE phase for all domains (API, backend, database)
- Integration points with existing skills (pact-api-design, pact-backend-patterns, pact-database-patterns)
- When to use this skill (implementation phase, APM selection, observability architecture)
- Cross-references to related skills:
  - `pact-security-patterns` for secure logging (PII redaction, audit logs)
  - `pact-testing-patterns` for testing observability instrumentation

**Structure**:
```markdown
## Overview

### What is Observability?
[Definition and distinction from monitoring]

### Observability in the PACT Framework
[How observability fits into CODE phase]

### When to Use This Skill
- Implementing structured logging in backend services
- Collecting metrics for APIs and databases
- Setting up distributed tracing for microservices
- Choosing APM platforms or log aggregation systems
- Integrating OpenTelemetry instrumentation

### Integration with Other Skills
[Cross-references to pact-api-design, pact-backend-patterns, pact-database-patterns, pact-security-patterns, pact-testing-patterns]
```

---

#### Section 2: Quick Reference - The Three Pillars (~600 words)

**Purpose**: Provide decision-making framework for choosing between logs, metrics, and traces.

**Content**:
- **Metrics**: What to measure, when to use (monitoring trends, alerting, dashboards)
- **Logs**: What to log, when to use (debugging, audit trails, error investigation)
- **Traces**: What to trace, when to use (request flow analysis, latency investigation, distributed debugging)
- Decision tree: Which pillar for different debugging scenarios
- How pillars complement each other (unified debugging workflow: metric alert → trace → logs)

**Structure**:
```markdown
## Quick Reference: The Three Pillars

### Metrics - What is Happening
**Use metrics when**: [scenarios]
**Examples**: Request rate, error rate, latency percentiles, CPU utilization
**Tools**: Prometheus, OpenTelemetry Metrics, DataDog, New Relic

### Logs - What Happened
**Use logs when**: [scenarios]
**Examples**: Error details, business events, audit trails, user actions
**Tools**: Pino, Winston, Loguru, ELK Stack, Grafana Loki

### Traces - Why It Happened
**Use traces when**: [scenarios]
**Examples**: Request flow across services, latency bottlenecks, dependency analysis
**Tools**: OpenTelemetry, Jaeger, Zipkin, DataDog APM, Grafana Tempo

### Decision Tree: Which Pillar to Use

```
START: Observability need

├─ Need to know "is the system healthy right now?"
│  └─ Use METRICS (dashboards, alerts)

├─ Need to know "what went wrong with this specific request?"
│  └─ Use LOGS (error details, context)

├─ Need to know "which service caused the latency?"
│  └─ Use TRACES (request flow, span durations)

└─ Need complete context for production incident?
   └─ Use ALL THREE (metric alert → find slow trace → read correlated logs)
```

### Unified Debugging Workflow
[How to use metrics, logs, and traces together]
```

---

#### Section 3: Available MCP Tools (~200 words)

**Purpose**: Document when to use sequential-thinking for complex observability architecture decisions.

**Content**:
- When to use sequential-thinking for observability decisions
- Example: Choosing between APM platforms (DataDog vs New Relic vs Application Insights)
- Example: Designing sampling strategy for high-volume tracing
- Fallback strategies if sequential-thinking unavailable

**Structure**:
```markdown
## Available MCP Tools

### sequential-thinking

**Purpose**: Complex observability architecture decisions requiring systematic trade-off analysis

**When to use**:
- Choosing between APM platforms (DataDog, New Relic, Application Insights, Grafana)
- Designing sampling strategies for distributed tracing
- Evaluating log aggregation systems (ELK, Loki, cloud providers)
- Balancing observability cost vs visibility needs
- Planning observability architecture for multi-service systems

**Example prompt**:
> "I need to choose an APM platform for a microservices system with 15 services, 5-person DevOps team, budget constraints, and Azure-based infrastructure. Let me systematically evaluate DataDog, New Relic, and Application Insights..."

**See pact-backend-coder agent for invocation syntax and workflow integration.**
```

---

#### Section 4: OpenTelemetry Integration (~500 words)

**Purpose**: Establish OpenTelemetry as the primary instrumentation standard.

**Content**:
- Why OpenTelemetry is the industry standard (W3C, CNCF, vendor-neutral)
- Auto-instrumentation vs manual instrumentation trade-offs
- Initialization best practices (initialize before framework)
- Semantic conventions for consistent attribute naming
- W3C Trace Context propagation
- OTel Collector deployment patterns (batching, filtering, routing)
- Links to detailed reference files for implementation

**Structure**:
```markdown
## OpenTelemetry Integration

### Why OpenTelemetry?
[Industry standard status, vendor neutrality, unified API]

### Auto-Instrumentation vs Manual
**Auto-instrumentation**: Zero-code, covers common frameworks
**Manual instrumentation**: Custom spans, business context
**Recommendation**: Start with auto, add manual for business logic

### Initialization Best Practices
[Critical: Initialize before framework imports]

### Semantic Conventions
[Standard attribute names for consistency]

### W3C Trace Context Propagation
[traceparent header, cross-service context]

### OpenTelemetry Collector
[Batching, filtering, routing telemetry data]

**For implementation details**: See `references/distributed-tracing.md`
```

---

#### Section 5: Observability Patterns by Domain (~800 words)

**Purpose**: Connect observability patterns to existing domain-specific skills.

**Content**:
- **API Observability**: Request/response logging, API metrics (rate, errors, duration), health checks
  - Links to `pact-api-design` skill for API-specific patterns
  - Correlation ID propagation in HTTP headers
  - API gateway instrumentation
- **Backend Observability**: Structured logging, business metrics, distributed tracing
  - Links to `pact-backend-patterns` skill for backend-specific patterns
  - Service-level metrics (RED method)
  - Error handling and logging integration
- **Database Observability**: Query performance, connection pool metrics, slow query logging
  - Links to `pact-database-patterns` skill for database-specific patterns
  - Query instrumentation and tracing
  - Database connection pool monitoring

**Structure**:
```markdown
## Observability Patterns by Domain

### API Observability
**Key Concerns**: Request/response logging, endpoint metrics, health checks
**Metrics**: Request rate, error rate by endpoint, latency by route
**Logging**: Correlation IDs, request/response payloads (sanitized), error details
**Tracing**: API gateway spans, downstream service calls

**See `pact-api-design` skill for**: [specific cross-references]

### Backend Observability
**Key Concerns**: Structured logging, business metrics, distributed tracing
**Metrics**: Service-level metrics (RED method), resource utilization
**Logging**: Structured JSON logs with trace context, business events
**Tracing**: Service spans, external API calls, message queue integration

**See `pact-backend-patterns` skill for**: [specific cross-references]

### Database Observability
**Key Concerns**: Query performance, connection pool health, slow queries
**Metrics**: Query duration, connection pool utilization, query count
**Logging**: Slow query logs, connection errors, transaction context
**Tracing**: Database operation spans, query parameter capture

**See `pact-database-patterns` skill for**: [specific cross-references]
```

---

#### Section 6: APM Platform Selection (~400 words)

**Purpose**: Provide objective comparison of APM platforms with decision framework.

**Content**:
- When to use APM tools vs open-source observability stack
- Platform comparison: DataDog, New Relic, Azure Application Insights, Grafana Stack
- Decision tree based on:
  - Team size and expertise
  - Budget constraints
  - Cloud platform (Azure, AWS, GCP, multi-cloud)
  - Infrastructure complexity
- Cost considerations (per-host, per-user, per-GB pricing models)
- Link to detailed reference file for platform comparison

**Structure**:
```markdown
## APM Platform Selection

### When to Use APM Platforms
[Scenarios favoring commercial APM vs open-source]

### Platform Comparison
**DataDog**: Infrastructure monitoring, 800+ integrations, complex pricing
**New Relic**: All-in-one pricing, AI insights, simpler UX
**Azure Application Insights**: Azure-native, .NET focus, cost-effective for Azure
**Grafana Stack (LGTM)**: Open-source, Kubernetes-native, operational expertise required

### Decision Tree

```
START: Choose APM platform

├─ Azure-centric architecture?
│  └─ YES → Azure Application Insights (native integration, cost-effective)

├─ Complex multi-cloud infrastructure?
│  └─ YES → DataDog (800+ integrations, infrastructure monitoring)

├─ Budget-conscious with Kubernetes?
│  └─ YES → Grafana Stack (self-hosted, Kubernetes-native)

├─ Want simplicity and predictable pricing?
│  └─ YES → New Relic (all-in-one pricing, AI insights)

└─ Default → Grafana Stack for prototyping, evaluate commercial options for production
```

**For detailed comparison**: See `references/metrics-collection.md` (APM integration section)
```

---

#### Section 7: Decision Tree - Which Reference to Use (~300 words)

**Purpose**: Route users to appropriate reference files based on implementation needs.

**Content**:
- Clear routing based on task:
  - Implementing structured logging → `references/logging-patterns.md`
  - Collecting metrics → `references/metrics-collection.md`
  - Implementing distributed tracing → `references/distributed-tracing.md`
- Brief description of what each reference covers
- When to use templates vs references

**Structure**:
```markdown
## Decision Tree: Which Reference to Use

**Implementing structured logging?**
→ See `references/logging-patterns.md`
  - JSON logging format and field conventions
  - Language-specific libraries (Pino, Loguru, Serilog)
  - Correlation ID propagation
  - Log aggregation systems (ELK, Loki, DataDog Logs)
  - Security (PII redaction, async logging)

**Collecting metrics?**
→ See `references/metrics-collection.md`
  - RED method (Rate, Errors, Duration) for APIs
  - USE method (Utilization, Saturation, Errors) for resources
  - Prometheus implementation and naming conventions
  - OpenTelemetry Metrics SDK
  - APM platform integration

**Implementing distributed tracing?**
→ See `references/distributed-tracing.md`
  - OpenTelemetry auto-instrumentation and manual spans
  - W3C Trace Context propagation
  - Sampling strategies (head vs tail sampling)
  - Trace backends (Jaeger, Zipkin, Grafana Tempo, APM platforms)
  - Correlation with logs and metrics

**Setting up complete observability stack?**
→ See `templates/observability-stack-setup.md`
  - OpenTelemetry + Prometheus + Loki + Grafana configuration
  - Docker Compose setup for local development
  - Production deployment considerations
```

---

#### Section 8: Common Anti-Patterns (~200 words)

**Purpose**: Warn against common observability mistakes that cause production issues.

**Content**:
- Logging PII/secrets (security risk, compliance violation)
- High-cardinality metrics labels (memory explosion, cardinality limits)
- Over-tracing (100% sampling in production causing performance degradation)
- Unstructured logs in production (impossible to query/aggregate)
- Missing correlation IDs (cannot connect related logs across services)
- Ignoring sampling strategies (trace storage costs spiral)

**Structure**:
```markdown
## Common Anti-Patterns

### 🚫 Logging PII and Secrets
**Problem**: Compliance violations, security risks
**Solution**: Implement PII redaction, use secret masking libraries
**See**: `pact-security-patterns` skill for secure logging

### 🚫 High-Cardinality Metrics Labels
**Problem**: Memory explosion, cardinality limit errors
**Example**: Using user IDs or request IDs as Prometheus labels
**Solution**: Use labels for low-cardinality dimensions (endpoint, status, method)

### 🚫 100% Sampling in Production
**Problem**: Performance overhead, trace storage costs
**Solution**: Probabilistic sampling (1-10%) + tail sampling for errors/slow requests

### 🚫 Unstructured Logs
**Problem**: Cannot query, aggregate, or correlate logs
**Solution**: Use JSON structured logging with consistent field names

### 🚫 Missing Correlation IDs
**Problem**: Cannot trace requests across services
**Solution**: Generate correlation IDs at API gateway, propagate in headers

### 🚫 No Sampling Strategy
**Problem**: Trace storage costs spiral, overwhelming backends
**Solution**: Configure head or tail sampling based on volume and debugging needs
```

---

#### Section 9: Integration with PACT Workflow (~200 words)

**Purpose**: Define skill's role in PACT methodology and handoff protocols.

**Content**:
- Input from Architecture phase (observability requirements, APM selection)
- Output to Test phase (testing observability instrumentation)
- Cross-references to agents that use this skill (backend-coder, database-engineer, frontend-coder)
- Quality gates for observability implementation

**Structure**:
```markdown
## Integration with PACT Workflow

### Input from Architecture Phase
- Observability requirements and SLAs
- APM platform selection (if made during architecture)
- Log aggregation system choice
- Metrics strategy (RED/USE method)
- Tracing requirements (sampling rate, trace retention)

### Output to Test Phase
- Observability instrumentation code
- Metrics endpoints configured
- Structured logging implemented
- Distributed tracing enabled
- APM platform integrated

### Testing Observability Implementation
**See `pact-testing-patterns` skill for**:
- Testing metrics emission (verify counters increment)
- Testing log output (verify structured format, correlation IDs)
- Testing trace context propagation (verify W3C traceparent header)

### Agents Using This Skill
- **pact-backend-coder**: Backend service observability implementation
- **pact-database-engineer**: Database query monitoring and logging
- **pact-frontend-coder**: Frontend error tracking and RUM (Real User Monitoring)
- **pact-architect**: Observability architecture design and APM selection
```

---

### 2.2 Word Count Summary

| Section | Word Count |
|---------|------------|
| 1. Overview | ~300 |
| 2. Quick Reference - Three Pillars | ~600 |
| 3. Available MCP Tools | ~200 |
| 4. OpenTelemetry Integration | ~500 |
| 5. Observability Patterns by Domain | ~800 |
| 6. APM Platform Selection | ~400 |
| 7. Decision Tree - Which Reference to Use | ~300 |
| 8. Common Anti-Patterns | ~200 |
| 9. Integration with PACT Workflow | ~200 |
| **Total** | **~3,500 words** |

---

## 3. Reference Files Specification

### 3.1 references/logging-patterns.md (~2,500 words)

**Purpose**: Comprehensive guide to structured logging, correlation, and log aggregation.

**Sections**:

#### 1. Structured Logging Fundamentals (~500 words)
- JSON vs plain text comparison (storage overhead, queryability, compression)
- Essential fields specification:
  - `timestamp` (ISO 8601 UTC)
  - `level` (ERROR, WARN, INFO, DEBUG)
  - `message` (human-readable summary)
  - `service` (service identifier)
  - `traceId` (OpenTelemetry trace ID)
  - `spanId` (OpenTelemetry span ID)
  - `correlationId` (request correlation ID)
  - `userId`, `sessionId` (context fields)
- Field naming conventions (camelCase vs snake_case consistency)
- Log levels semantic guidance:
  - **ERROR**: Action required, service degraded
  - **WARN**: Potential issue, no immediate action
  - **INFO**: Business events, significant state changes
  - **DEBUG**: Troubleshooting details, verbose context

**Code Example**:
```json
{
  "timestamp": "2025-12-07T10:30:00.123Z",
  "level": "INFO",
  "message": "Payment processed successfully",
  "service": "payment-service",
  "traceId": "4bf92f3577b34da6a3ce929d0e0e4736",
  "spanId": "00f067aa0ba902b7",
  "correlationId": "req_7f8a9b2c3d4e",
  "userId": "user_12345",
  "amount": 99.99,
  "currency": "USD",
  "duration": 145
}
```

---

#### 2. Language-Specific Implementation (~800 words)

**Node.js - Pino** (~150 words + code):
```javascript
const pino = require('pino');

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  formatters: {
    level: (label) => ({ level: label.toUpperCase() })
  },
  base: {
    service: 'payment-service'
  },
  timestamp: () => `,"timestamp":"${new Date().toISOString()}"`
});

// Usage with context
logger.info({
  correlationId: req.headers['x-correlation-id'],
  userId: req.user.id,
  amount: payment.amount,
  currency: payment.currency
}, 'Payment processed successfully');
```

**Python - Loguru** (~150 words + code):
```python
import sys
from loguru import logger

# Configure structured JSON logging
logger.configure(
    handlers=[
        {
            "sink": sys.stdout,
            "format": "{message}",
            "serialize": True  # JSON output
        }
    ]
)

# Add context fields
logger = logger.bind(service="payment-service")

# Usage with context
logger.info(
    "Payment processed successfully",
    correlation_id=correlation_id,
    user_id=user_id,
    amount=99.99,
    currency="USD"
)
```

**Java - Logback with JSON encoder** (~150 words + code):
```xml
<!-- logback.xml -->
<configuration>
  <appender name="JSON" class="ch.qos.logback.core.ConsoleAppender">
    <encoder class="net.logstash.logback.encoder.LogstashEncoder">
      <customFields>{"service":"payment-service"}</customFields>
    </encoder>
  </appender>
  <root level="INFO">
    <appender-ref ref="JSON" />
  </root>
</configuration>
```

```java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import net.logstash.logback.argument.StructuredArguments;

Logger logger = LoggerFactory.getLogger(PaymentService.class);

logger.info("Payment processed successfully",
  StructuredArguments.keyValue("correlationId", correlationId),
  StructuredArguments.keyValue("userId", userId),
  StructuredArguments.keyValue("amount", 99.99),
  StructuredArguments.keyValue("currency", "USD")
);
```

**C#/.NET - Serilog** (~150 words + code):
```csharp
using Serilog;

Log.Logger = new LoggerConfiguration()
    .Enrich.WithProperty("service", "payment-service")
    .WriteTo.Console(new JsonFormatter())
    .CreateLogger();

Log.Information(
    "Payment processed successfully",
    correlationId,
    userId,
    amount,
    currency
);
```

**Summary table**:
| Language | Library | JSON Output | Performance | Learning Curve |
|----------|---------|-------------|-------------|----------------|
| Node.js | Pino | Native | Fastest | Low |
| Python | Loguru | Via serialize | Fast | Low |
| Java | Logback + Logstash encoder | Native | Good | Medium |
| C#/.NET | Serilog | Via JsonFormatter | Good | Low |
| Go | zap | Native | Fastest | Medium |

---

#### 3. Correlation and Context Propagation (~400 words)

**Correlation ID generation strategies**:
- UUID v4 (random, globally unique, 36 characters)
- Prefixed UUID (e.g., `req_7f8a9b2c`, human-readable, sortable)
- Snowflake IDs (ordered, distributed ID generation)

**Propagating correlation IDs across services**:
- HTTP header: `X-Correlation-ID` (de facto standard)
- Generate at API gateway if not present
- Propagate in all downstream HTTP requests
- Include in all log entries

**Integrating OpenTelemetry trace/span IDs in logs**:
- Extract `traceId` and `spanId` from OpenTelemetry context
- Add to every log entry for correlation
- Enables linking logs to traces in APM platforms

**Code Example - Express middleware**:
```javascript
const { trace } = require('@opentelemetry/api');

app.use((req, res, next) => {
  // Generate correlation ID if not present
  const correlationId = req.headers['x-correlation-id'] || `req_${uuidv4().substring(0, 12)}`;
  req.correlationId = correlationId;
  res.setHeader('X-Correlation-ID', correlationId);

  // Extract OpenTelemetry trace context
  const span = trace.getActiveSpan();
  const traceId = span?.spanContext().traceId;
  const spanId = span?.spanContext().spanId;

  // Add to logger context
  req.logger = logger.child({
    correlationId,
    traceId,
    spanId
  });

  next();
});
```

---

#### 4. Log Aggregation Systems (~600 words)

**ELK Stack (Elasticsearch + Logstash + Kibana)**:
- **Use case**: On-premises, full-text search priority, established ELK expertise
- **Strengths**: Powerful search, flexible dashboards, rich plugin ecosystem
- **Weaknesses**: Resource-intensive (high memory/CPU), operational complexity
- **Cost**: Self-hosted (infrastructure) or Elastic Cloud (~$95/month per GB indexed)
- **Setup**: Filebeat → Logstash → Elasticsearch → Kibana visualization

**Grafana Loki**:
- **Use case**: Kubernetes/containers, cost-conscious, Prometheus users
- **Strengths**: 10x cheaper storage (indexes labels only, not full text), LogQL query language (like PromQL)
- **Weaknesses**: Limited full-text search (grep log content after label filtering)
- **Cost**: Self-hosted (object storage costs: ~$0.02/GB S3) or Grafana Cloud (from $0.50/GB)
- **Setup**: Promtail → Loki → Grafana visualization

**DataDog Logs**:
- **Use case**: Already using DataDog APM, want unified platform
- **Strengths**: Integrated with metrics/traces, automatic log parsing, native correlation
- **Weaknesses**: Expensive at scale, vendor lock-in
- **Cost**: $0.10/GB ingested + $1.70/million log events indexed
- **Setup**: DataDog agent → DataDog Logs → DataDog dashboard

**Decision Matrix**:
| Feature | ELK Stack | Grafana Loki | DataDog Logs |
|---------|-----------|--------------|--------------|
| **Full-text search** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Cost (high volume)** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Kubernetes-native** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Operational complexity** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Unified observability** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Configuration Example - Loki with Promtail**:
```yaml
# promtail-config.yaml
server:
  http_listen_port: 9080

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: payment-service
    static_configs:
      - targets:
          - localhost
        labels:
          job: payment-service
          __path__: /var/log/payment-service/*.log
```

---

#### 5. Security and Performance (~200 words)

**PII redaction/masking patterns**:
- Automatic masking of sensitive fields (credit cards, SSN, passwords)
- Field-level redaction libraries (pino-noir for Node.js, python-json-logger filters)
- Example patterns: `****1234` for credit cards, `***@email.com` for emails

**Async logging for performance**:
- Avoid blocking I/O on log writes
- Use async transports (Pino async, Winston async)
- Buffer logs in memory, flush periodically
- Trade-off: Risk of log loss on crash (acceptable for most non-audit logs)

**Log sampling for high-volume services**:
- Sample DEBUG logs (e.g., keep 1% of DEBUG entries)
- Always keep ERROR and WARN logs
- Dynamic sampling based on error rate

**Storage and retention policies**:
- Hot storage: 7-30 days (queryable, indexed)
- Cold storage: 90-365 days (archived, compliance)
- Delete after retention period (GDPR compliance)

---

### 3.2 references/metrics-collection.md (~2,500 words)

**Purpose**: Comprehensive guide to metrics collection, RED/USE methods, and APM integration.

**Sections**:

#### 1. Metrics Fundamentals (~400 words)

**Types of Metrics**:
- **Counter**: Monotonically increasing value (total requests, total errors)
  - Use for: Event counts, cumulative totals
  - Example: `http_requests_total`
- **Gauge**: Point-in-time value that can go up or down (CPU usage, memory, queue length)
  - Use for: Current state, resource utilization
  - Example: `cpu_usage_percent`, `active_connections`
- **Histogram**: Distribution of values (latency, request size)
  - Use for: Duration measurements, size distributions
  - Example: `http_request_duration_seconds` (with buckets for p50, p95, p99)
- **Summary**: Similar to histogram, calculates percentiles on client side
  - Use for: Streaming percentiles (less common than histogram)

**RED Method** (for request-driven services):
- **Rate**: Requests per second (throughput)
  - Metric: `http_requests_total` counter, calculate rate over time window
- **Errors**: Percentage of failed requests
  - Metric: `http_requests_total{status="5xx"}` divided by total requests
- **Duration**: Latency distribution (p50, p95, p99)
  - Metric: `http_request_duration_seconds` histogram

**USE Method** (for infrastructure resources):
- **Utilization**: Percentage of resource capacity used
  - Metrics: `cpu_usage_percent`, `memory_usage_percent`
- **Saturation**: Queue length or waiting work
  - Metrics: `db_connection_pool_wait_count`, `request_queue_length`
- **Errors**: Error count
  - Metrics: `db_connection_errors_total`, `disk_io_errors_total`

**When to use RED vs USE**:
- RED: APIs, web servers, microservices (request-driven)
- USE: Hosts, databases, caches, message queues (resource-focused)

---

#### 2. Prometheus Implementation (~800 words)

**Metric naming conventions**:
- Lowercase with underscores: `http_requests_total`, `db_query_duration_seconds`
- Include unit suffix: `_seconds`, `_bytes`, `_total`, `_ratio`
- Avoid redundancy: `api_http_requests_total` (redundant), prefer `http_requests_total`

**Label design patterns**:
- Use labels for low-cardinality dimensions (method, endpoint, status)
- Avoid high-cardinality labels (user IDs, request IDs) - causes memory explosion
- Example good labels: `method="POST"`, `endpoint="/api/users"`, `status="200"`
- Example bad labels: `user_id="12345"`, `request_id="abc-123"` (unbounded cardinality)

**Histogram bucket selection**:
- Choose buckets based on SLA targets
- Example for API latency: `[0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10]` (seconds)
- Include upper bound (Infinity) automatically
- More buckets = better accuracy but more storage

**Node.js - prom-client**:
```javascript
const promClient = require('prom-client');

// Enable default metrics (CPU, memory, event loop)
promClient.collectDefaultMetrics({ timeout: 5000 });

// RED metrics
const httpRequestsTotal = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total HTTP requests',
  labelNames: ['method', 'endpoint', 'status']
});

const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request duration in seconds',
  labelNames: ['method', 'endpoint'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5]
});

// Middleware to instrument
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    httpRequestsTotal.inc({
      method: req.method,
      endpoint: req.route?.path || 'unknown',
      status: res.statusCode
    });
    httpRequestDuration.observe({
      method: req.method,
      endpoint: req.route?.path || 'unknown'
    }, duration);
  });
  next();
});

// Expose /metrics endpoint
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', promClient.register.contentType);
  res.end(await promClient.register.metrics());
});
```

**Python - prometheus_client**:
```python
from prometheus_client import Counter, Histogram, start_http_server
import time

# RED metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1, 2, 5]
)

# Flask middleware
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    http_requests_total.labels(
        method=request.method,
        endpoint=request.endpoint,
        status=response.status_code
    ).inc()
    http_request_duration.labels(
        method=request.method,
        endpoint=request.endpoint
    ).observe(duration)
    return response

# Start metrics server on port 8000
start_http_server(8000)
```

**Java - Micrometer**:
```java
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;

@RestController
public class PaymentController {
    private final MeterRegistry registry;

    public PaymentController(MeterRegistry registry) {
        this.registry = registry;
    }

    @PostMapping("/payments")
    public Payment processPayment(@RequestBody PaymentRequest request) {
        Timer.Sample sample = Timer.start(registry);
        try {
            Payment payment = paymentService.process(request);
            registry.counter("http.requests.total",
                "method", "POST",
                "endpoint", "/payments",
                "status", "200"
            ).increment();
            return payment;
        } catch (Exception e) {
            registry.counter("http.requests.total",
                "method", "POST",
                "endpoint", "/payments",
                "status", "500"
            ).increment();
            throw e;
        } finally {
            sample.stop(Timer.builder("http.request.duration")
                .tag("method", "POST")
                .tag("endpoint", "/payments")
                .register(registry));
        }
    }
}
```

---

#### 3. OpenTelemetry Metrics (~600 words)

**OTel Metrics API vs Prometheus client**:
- OpenTelemetry: Vendor-neutral, export to any backend (Prometheus, DataDog, New Relic)
- Prometheus client: Prometheus-specific, pull-based scraping
- Recommendation: Use OpenTelemetry for multi-backend flexibility

**Semantic conventions for metrics**:
- Standard attribute names for consistency
- `http.method`, `http.status_code`, `http.route`
- `db.system`, `db.operation`, `db.statement`
- See OpenTelemetry semantic conventions documentation

**Exporting to multiple backends**:
- Configure OTel Metrics Exporter for each backend
- Example: Prometheus (pull), DataDog (push), New Relic (push)
- Use OTel Collector for centralized routing

**Example - Node.js with OpenTelemetry Metrics**:
```javascript
const { MeterProvider, PeriodicExportingMetricReader } = require('@opentelemetry/sdk-metrics');
const { PrometheusExporter } = require('@opentelemetry/exporter-prometheus');

// Configure Prometheus exporter
const prometheusExporter = new PrometheusExporter({ port: 9464 });

// Create meter provider
const meterProvider = new MeterProvider({
  readers: [new PeriodicExportingMetricReader({ exporter: prometheusExporter })]
});

// Get meter
const meter = meterProvider.getMeter('payment-service');

// Create metrics
const httpRequestsTotal = meter.createCounter('http.requests.total', {
  description: 'Total HTTP requests'
});

const httpRequestDuration = meter.createHistogram('http.request.duration', {
  description: 'HTTP request duration',
  unit: 'seconds'
});

// Instrument Express app
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    httpRequestsTotal.add(1, {
      'http.method': req.method,
      'http.route': req.route?.path || 'unknown',
      'http.status_code': res.statusCode
    });
    httpRequestDuration.record(duration, {
      'http.method': req.method,
      'http.route': req.route?.path || 'unknown'
    });
  });
  next();
});
```

---

#### 4. Business Metrics (~300 words)

**Domain-specific metrics**:
- Track business outcomes, not just technical metrics
- Examples:
  - E-commerce: `orders_total`, `revenue_usd_total`, `cart_abandonment_rate`
  - SaaS: `signups_total`, `active_users`, `subscription_churn_rate`
  - API: `api_calls_by_customer`, `quota_usage_percent`

**SLO/SLI tracking**:
- Service Level Indicators (SLIs): Measurable metrics (availability, latency, error rate)
- Service Level Objectives (SLOs): Target thresholds (99.9% availability, p95 latency <100ms)
- Error budget: Allowed downtime based on SLO (0.1% = 43 minutes/month for 99.9% SLO)

**Custom metrics vs standard metrics**:
- Standard metrics: Infrastructure, HTTP, database (use OpenTelemetry semantic conventions)
- Custom metrics: Business logic, domain-specific events
- Balance: Don't over-instrument, focus on metrics that inform decisions

**Example - Business metrics**:
```javascript
const ordersTotal = meter.createCounter('orders.total', {
  description: 'Total orders processed'
});

const revenueTotal = meter.createCounter('revenue.usd.total', {
  description: 'Total revenue in USD'
});

// Track business events
ordersTotal.add(1, {
  'payment.method': 'credit_card',
  'order.type': 'subscription'
});

revenueTotal.add(orderAmount, {
  'payment.method': 'credit_card',
  'currency': 'USD'
});
```

---

#### 5. Metrics Storage and Visualization (~400 words)

**Prometheus + Grafana setup**:
- Prometheus: Scrapes /metrics endpoints, stores time-series data
- Grafana: Visualization, dashboards, alerting
- Configuration: prometheus.yml defines scrape targets

**DataDog metrics integration**:
- DataDog Agent scrapes metrics or OpenTelemetry pushes to DataDog
- Automatic dashboard creation
- Anomaly detection and forecasting

**New Relic metrics integration**:
- OpenTelemetry OTLP exporter to New Relic
- Unified metrics, logs, traces in single platform
- NRQL query language for custom dashboards

**Alerting based on metrics**:
- Threshold alerts: CPU >80%, error rate >5%
- Anomaly detection: ML-based detection of unusual patterns
- Alert fatigue reduction: Use alert grouping, de-duplication, intelligent routing

**Example - Prometheus scrape config**:
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'payment-service'
    static_configs:
      - targets: ['localhost:9464']
        labels:
          environment: 'production'
          service: 'payment-service'
```

**Example - Grafana dashboard PromQL queries**:
```promql
# Request rate (requests per second)
rate(http_requests_total[5m])

# Error rate (percentage of 5xx responses)
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100

# P95 latency
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint))
```

---

### 3.3 references/distributed-tracing.md (~2,500 words)

**Purpose**: Comprehensive guide to distributed tracing, OpenTelemetry implementation, and trace backends.

**Sections**:

#### 1. Distributed Tracing Fundamentals (~400 words)

**Traces, spans, and context**:
- **Trace**: End-to-end request journey across services (unique trace ID)
- **Span**: Single operation within a trace (unique span ID, has start time, duration, parent span)
- **Context**: Propagated metadata (trace ID, span ID, sampling decision)

**Why tracing is critical for microservices**:
- Understand request flow across 10+ services
- Identify latency bottlenecks (which service is slow?)
- Debug distributed failures (which service failed first?)
- Visualize dependencies and call graphs

**W3C Trace Context standard**:
- Universal standard for context propagation (supported by all APM vendors)
- Replaces vendor-specific headers (X-B3-TraceId, X-Datadog-Trace-Id)
- Interoperability: Single trace can span multiple vendors

**traceparent header format**:
- Format: `00-<trace-id>-<parent-span-id>-<trace-flags>`
- Example: `00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01`
- Components:
  - Version: `00`
  - Trace ID: 32 hex characters (128 bits)
  - Parent Span ID: 16 hex characters (64 bits)
  - Trace Flags: 2 hex characters (sampled flag: 01 = sampled, 00 = not sampled)

---

#### 2. OpenTelemetry Tracing (~900 words)

**Auto-instrumentation setup**:
- Zero-code instrumentation for common frameworks (Express, Flask, Spring Boot)
- Covers HTTP requests, database queries, external API calls
- Initialize before application framework imports

**Node.js auto-instrumentation**:
```javascript
// tracing.js - Load FIRST before any other imports
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

const sdk = new NodeSDK({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'payment-service',
    [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0'
  }),
  traceExporter: new OTLPTraceExporter({
    url: 'http://localhost:4318/v1/traces'
  }),
  instrumentations: [getNodeAutoInstrumentations()]
});

sdk.start();

// Graceful shutdown
process.on('SIGTERM', () => {
  sdk.shutdown()
    .then(() => console.log('Tracing terminated'))
    .catch((error) => console.log('Error terminating tracing', error))
    .finally(() => process.exit(0));
});

// Now import application
require('./app.js');
```

**Python auto-instrumentation**:
```python
# Run with: opentelemetry-instrument --traces_exporter otlp python app.py

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure tracer provider
resource = Resource.create({"service.name": "payment-service"})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces"))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Auto-instrumentation for Flask, requests, SQLAlchemy, etc.
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
```

**Manual instrumentation for custom spans**:
```javascript
const { trace } = require('@opentelemetry/api');

const tracer = trace.getTracer('payment-service');

async function processPayment(amount, currency) {
  return tracer.startActiveSpan('processPayment', async (span) => {
    try {
      // Add span attributes (semantic conventions)
      span.setAttribute('payment.amount', amount);
      span.setAttribute('payment.currency', currency);
      span.setAttribute('payment.method', 'credit_card');

      // Business logic
      const result = await chargeCard(amount, currency);

      // Record successful completion
      span.setStatus({ code: SpanStatusCode.OK });
      return result;
    } catch (error) {
      // Record exception
      span.recordException(error);
      span.setStatus({
        code: SpanStatusCode.ERROR,
        message: error.message
      });
      throw error;
    } finally {
      span.end();
    }
  });
}
```

**Span attributes (semantic conventions)**:
- Use standard attribute names for consistency
- HTTP: `http.method`, `http.status_code`, `http.url`, `http.route`
- Database: `db.system`, `db.statement`, `db.operation`, `db.name`
- Messaging: `messaging.system`, `messaging.destination`, `messaging.operation`
- See OpenTelemetry semantic conventions: https://opentelemetry.io/docs/specs/semconv/

**Context propagation across protocols**:
- **HTTP**: W3C Trace Context headers (`traceparent`, `tracestate`)
- **gRPC**: `grpc-trace-bin` metadata (binary format)
- **Message queues**: Trace context in message headers (Kafka, RabbitMQ)
- Automatic propagation by OpenTelemetry SDK

**Example - Multi-service trace flow**:
```
API Gateway (span: gateway.request)
    ↓ HTTP request with traceparent header
User Service (span: user.authenticate)
    ↓ Database query
PostgreSQL (span: db.query.users.findById)
    ↓ Return to User Service
User Service returns
    ↓ Return to API Gateway
API Gateway returns to client
```

All spans share same trace ID, enabling end-to-end visibility.

---

#### 3. Sampling Strategies (~500 words)

**Head sampling**: Decision at trace start
- **Probabilistic**: Sample N% of all traces randomly
  - Example: 1% sampling for high-volume services
  - Simple, predictable load on trace backend
  - Risk: Miss important traces (errors, slow requests)
- **Rate limiting**: Sample first N traces per second
  - Example: Max 100 traces/second
  - Protects backend from overload
  - Risk: Biased sampling (only fast requests if service is slow)

**Tail sampling**: Decision after trace completion
- **Error-based**: Always keep traces with errors
  - Ensure all failures are captured
  - Critical for debugging production issues
- **Latency-based**: Keep slow traces (>2s, >5s)
  - Identify performance bottlenecks
  - Define latency thresholds based on SLAs
- **Hybrid**: Probabilistic (1%) + always keep errors/slow traces
  - Best of both worlds
  - Requires buffering traces until completion (memory overhead)

**Trade-offs: Cost vs completeness**:
- 100% sampling: Complete visibility, but expensive storage and performance overhead
- 1% sampling: Cost-effective, but may miss rare issues
- Tail sampling: Intelligent sampling, but requires OTel Collector and buffering

**Configuration example - OTel Collector tail sampling**:
```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      http:
        endpoint: 0.0.0.0:4318

processors:
  tail_sampling:
    decision_wait: 10s  # Wait 10s for trace to complete
    policies:
      - name: error-policy
        type: status_code
        status_code:
          status_codes: [ERROR]
      - name: latency-policy
        type: latency
        latency:
          threshold_ms: 2000  # Keep traces >2s
      - name: probabilistic-policy
        type: probabilistic
        probabilistic:
          sampling_percentage: 1  # Keep 1% of remaining traces

exporters:
  otlp:
    endpoint: jaeger:4317

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [tail_sampling]
      exporters: [otlp]
```

---

#### 4. Trace Backends (~600 words)

**Jaeger**:
- **Use case**: Open-source, Kubernetes-native, cost-conscious
- **Strengths**: Free, native OpenTelemetry support, Uber-proven at scale
- **Weaknesses**: Limited analysis features, basic UI
- **Storage**: Cassandra (production), Elasticsearch, Badger (single-node)
- **Setup**: Deploy Jaeger all-in-one (development) or production deployment with Cassandra

**Zipkin**:
- **Use case**: Legacy tracing systems, Twitter-lineage projects
- **Strengths**: Mature, stable, simple deployment
- **Weaknesses**: Less active development than Jaeger, basic features
- **Storage**: MySQL, Cassandra, Elasticsearch
- **Setup**: Zipkin server (single JAR), configure storage backend

**Grafana Tempo**:
- **Use case**: Grafana users, cost-effective at scale, Kubernetes
- **Strengths**: 10x cheaper storage (object storage: S3, GCS), integrates with Grafana, TraceQL query language
- **Weaknesses**: Requires Grafana ecosystem, less mature than Jaeger
- **Storage**: Object storage (S3, GCS, Azure Blob, local disk)
- **Setup**: Grafana Tempo server + Grafana for visualization

**DataDog APM**:
- **Use case**: Already using DataDog, want unified observability platform
- **Strengths**: Automatic correlation with logs/metrics, APM features (profiling, service map), AI insights
- **Weaknesses**: Expensive ($31-40/host/month), vendor lock-in
- **Storage**: Managed by DataDog
- **Setup**: DataDog agent + OpenTelemetry exporter to DataDog

**New Relic**:
- **Use case**: Want simplicity, predictable pricing, AI-powered insights
- **Strengths**: All-in-one pricing, distributed tracing + logs + metrics, NRQL query language
- **Weaknesses**: Vendor lock-in, cost scales with data volume
- **Storage**: Managed by New Relic
- **Setup**: New Relic agent + OpenTelemetry exporter to New Relic

**Comparison Table**:
| Feature | Jaeger | Zipkin | Grafana Tempo | DataDog APM | New Relic |
|---------|--------|--------|---------------|-------------|-----------|
| **Cost (self-hosted)** | Free | Free | Free | N/A | N/A |
| **Cost (managed)** | N/A | N/A | From $0.50/GB | $31-40/host | $0.35-0.50/GB |
| **OpenTelemetry support** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Storage cost** | Medium | Medium | Low | N/A | N/A |
| **Analysis features** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Unified observability** | ⭐⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Operational complexity** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

#### 5. Correlation with Logs and Metrics (~100 words)

**Logging trace/span IDs in application logs**:
- Extract trace ID and span ID from OpenTelemetry context
- Add to every log entry for correlation
- Enables linking logs to traces in APM platforms

**Linking traces to metrics dashboards**:
- Use same labels/attributes in metrics and traces (service name, endpoint)
- Click-through from metrics dashboard to related traces
- Example: High p95 latency metric → filter traces by endpoint → find slow spans

**Unified debugging workflow**:
1. Metric alert: API latency p95 >1s (metrics dashboard)
2. Filter traces for slow requests (tracing backend)
3. Identify slow span (database query taking 800ms)
4. Read logs for that trace ID (log aggregation)
5. Root cause: Missing database index on user_id column

---

## 4. Template Specification

### 4.1 templates/observability-stack-setup.md

**Purpose**: Step-by-step guide for setting up complete observability stack (OpenTelemetry + Prometheus + Loki + Grafana) for local development and production.

**Sections**:

#### 1. Overview (~200 words)
- Complete observability stack components
- Architecture diagram showing flow
- Prerequisites (Docker, Docker Compose)

#### 2. Docker Compose Setup (~400 words)
- docker-compose.yml with all services:
  - OpenTelemetry Collector
  - Prometheus
  - Loki
  - Grafana
  - Jaeger (optional, for trace visualization)
- Volume mounts and configuration

#### 3. OpenTelemetry Collector Configuration (~300 words)
- otel-collector-config.yaml
- Receivers: OTLP (HTTP, gRPC)
- Processors: Batch, tail sampling
- Exporters: Prometheus, Loki, Jaeger

#### 4. Application Instrumentation (~400 words)
- Node.js example with OpenTelemetry SDK
- Environment variables for endpoints
- Correlation between logs, metrics, traces

#### 5. Grafana Dashboards (~300 words)
- Pre-configured dashboards for:
  - RED metrics (Prometheus data source)
  - Logs (Loki data source)
  - Traces (Jaeger data source)
- Importing dashboard JSON

#### 6. Production Considerations (~200 words)
- Scaling OTel Collector (horizontal scaling)
- Prometheus retention and storage
- Loki object storage configuration (S3)
- Security (authentication, TLS)

**Total**: ~1,800 words

---

## 5. Example Specification

### 5.1 examples/express-microservices-observability.md

**Purpose**: Complete working example demonstrating observability integration in an Express.js microservices architecture (API Gateway + User Service + Payment Service).

**Sections**:

#### 1. Overview (~200 words)
- System architecture: API Gateway → User Service → Payment Service → PostgreSQL
- Observability goals: Track request flow, identify latency bottlenecks, correlate logs
- Technologies: Express.js, OpenTelemetry, Prometheus, Loki, Grafana

#### 2. System Architecture Diagram (~100 words + diagram)
```
Client
  ↓
API Gateway (Express.js)
  ↓ HTTP
  ├─ User Service (Express.js)
  │   ↓ Database query
  │   PostgreSQL
  └─ Payment Service (Express.js)
      ↓ External API
      Stripe API
```

#### 3. OpenTelemetry Setup (~400 words)
- tracing.js initialization (shared across services)
- Auto-instrumentation for Express, PostgreSQL, HTTP
- Service name configuration
- Exporting to OTel Collector

**Code**: Complete tracing.js file with comments

#### 4. Structured Logging Implementation (~400 words)
- Pino logger configuration
- Middleware to inject correlation ID and trace context
- Log correlation with OpenTelemetry trace ID

**Code**: logger.js and correlation middleware

#### 5. Metrics Collection (~400 words)
- Prometheus metrics setup
- RED metrics for each service
- Custom business metrics (user registrations, payments processed)

**Code**: metrics.js with prom-client instrumentation

#### 6. Request Flow Example (~500 words)
- End-to-end request: POST /api/payments
- Trace visualization showing all spans:
  - API Gateway: gateway.request (200ms total)
  - User Service: user.authenticate (50ms)
  - PostgreSQL: db.query.users.findById (30ms)
  - Payment Service: payment.processPayment (120ms)
  - Stripe API: http.post.stripe.charges (100ms)
- Logs correlated by trace ID
- Metrics showing request rate, latency, errors

#### 7. Debugging Scenario (~300 words)
- Problem: Payment endpoint p95 latency increased to 2s
- Step 1: Check Grafana metrics dashboard (identify spike)
- Step 2: Filter traces for slow payments (find 2s trace)
- Step 3: Identify bottleneck span (Stripe API call taking 1.8s)
- Step 4: Read logs for that trace ID (see Stripe timeout errors)
- Step 5: Root cause: Stripe API degradation, implement retry logic

#### 8. Configuration Files (~400 words)
- docker-compose.yml (all services)
- otel-collector-config.yaml
- prometheus.yml
- loki-config.yaml
- Grafana dashboard JSON

**Total**: ~2,700 words

---

## 6. Integration Design

### 6.1 Cross-Skill References

**From pact-observability-patterns TO other skills**:

- **pact-backend-patterns**:
  - Reference: Backend service observability patterns (structured logging, RED metrics)
  - Link: "See pact-backend-patterns for backend-specific implementation guidance"

- **pact-api-design**:
  - Reference: API observability patterns (request/response logging, API metrics, health checks)
  - Link: "See pact-api-design for API-specific observability patterns"

- **pact-database-patterns**:
  - Reference: Database observability patterns (query monitoring, connection pool metrics)
  - Link: "See pact-database-patterns for database-specific observability patterns"

- **pact-security-patterns**:
  - Reference: Secure logging (PII redaction, audit logs, secure trace propagation)
  - Link: "See pact-security-patterns for secure logging and audit trail patterns"

- **pact-testing-patterns**:
  - Reference: Testing observability instrumentation (verify metrics, logs, traces)
  - Link: "See pact-testing-patterns for testing observability implementation"

**FROM other skills TO pact-observability-patterns**:

Skills should add cross-references in their observability sections:

**pact-api-design** (line 332 - API Observability section):
```markdown
## API Observability

For comprehensive observability patterns including OpenTelemetry integration, APM platform
selection, and log aggregation systems, see the `pact-observability-patterns` skill.
This section covers API-specific observability concerns.

[existing content...]
```

**pact-backend-patterns** (line 343 - Observability Patterns section):
```markdown
## Observability Patterns

For comprehensive observability patterns including structured logging, metrics collection
(RED/USE method), distributed tracing, and APM integration, see the `pact-observability-patterns`
skill. This section covers backend-specific observability concerns.

[existing content...]
```

**pact-database-patterns** (line 435 - Database Observability section):
```markdown
## Database Observability

For comprehensive observability patterns including log aggregation, metrics collection, and
distributed tracing integration, see the `pact-observability-patterns` skill. This section
covers database-specific observability concerns.

[existing content...]
```

---

### 6.2 Agent Integration

**Agents that should reference this skill**:

1. **pact-backend-coder**:
   - When: Implementing backend services with logging, metrics, or tracing
   - Usage: Reference for OpenTelemetry setup, structured logging, RED metrics
   - Invocation: Automatic when user mentions observability/logging/metrics/tracing

2. **pact-database-engineer**:
   - When: Implementing database query monitoring or connection pool metrics
   - Usage: Reference for database observability patterns, slow query logging
   - Invocation: Automatic when user mentions database monitoring/performance

3. **pact-frontend-coder**:
   - When: Implementing frontend error tracking or Real User Monitoring (RUM)
   - Usage: Reference for frontend observability patterns (future scope)
   - Invocation: Automatic when user mentions frontend observability/error tracking

4. **pact-architect**:
   - When: Designing observability architecture, selecting APM platforms
   - Usage: Reference for APM comparison, log aggregation selection, observability strategy
   - Invocation: Manual or automatic when designing observability architecture

---

## 7. Complete File Tree

```
skills/pact-observability-patterns/
├── SKILL.md                                    # Main skill definition (~3,500 words)
│                                               # Sections: Overview, Three Pillars, MCP Tools,
│                                               # OpenTelemetry, Domain Patterns, APM Selection,
│                                               # Decision Tree, Anti-Patterns, PACT Integration
│
├── references/                                 # Detailed reference files
│   ├── logging-patterns.md                    # Structured logging reference (~2,500 words)
│   │                                           # Sections: JSON logging, language examples,
│   │                                           # correlation IDs, log aggregation (ELK/Loki/DataDog),
│   │                                           # security (PII redaction, async logging)
│   │
│   ├── metrics-collection.md                  # Metrics and RED/USE method (~2,500 words)
│   │                                           # Sections: Metric types, RED/USE methods,
│   │                                           # Prometheus implementation (Node.js, Python, Java),
│   │                                           # OpenTelemetry Metrics, business metrics,
│   │                                           # APM integration, visualization (Grafana)
│   │
│   └── distributed-tracing.md                 # Tracing and OpenTelemetry (~2,500 words)
│                                               # Sections: Tracing fundamentals, W3C Trace Context,
│                                               # OpenTelemetry auto/manual instrumentation,
│                                               # sampling strategies (head/tail), trace backends
│                                               # (Jaeger, Zipkin, Tempo, DataDog, New Relic),
│                                               # correlation with logs/metrics
│
├── templates/                                  # Implementation templates
│   └── observability-stack-setup.md           # Complete stack setup guide (~1,800 words)
│                                               # Docker Compose: OTel Collector + Prometheus +
│                                               # Loki + Grafana, production deployment considerations
│
└── examples/                                   # Working examples
    └── express-microservices-observability.md # Full Express.js example (~2,700 words)
                                                # API Gateway + User Service + Payment Service
                                                # with OpenTelemetry, Prometheus, Loki, complete
                                                # debugging scenario demonstrating unified workflow
```

**Total Content**: ~13,500 words across all files

**File Structure Rationale**:
- **SKILL.md**: Progressive disclosure (quick reference → detailed sections → route to references)
- **references/**: Self-contained deep dives (one topic per file, no cross-references between references)
- **templates/**: Practical setup guides (copy-paste configuration)
- **examples/**: Complete working implementations (learn by example)

---

## 8. Quality Gates

### 8.1 Completeness Checklist

Before marking skill complete, verify:

- ✅ **SKILL.md**:
  - [ ] Frontmatter with name, description, allowed-tools, metadata
  - [ ] All 9 sections completed with target word counts
  - [ ] Decision trees for pillar selection, APM selection, reference routing
  - [ ] Cross-references to all related skills
  - [ ] MCP tools section (sequential-thinking guidance)

- ✅ **Reference Files**:
  - [ ] logging-patterns.md (~2,500 words) with 5 sections
  - [ ] metrics-collection.md (~2,500 words) with 5 sections
  - [ ] distributed-tracing.md (~2,500 words) with 5 sections
  - [ ] Code examples in Node.js, Python, Java (minimum 3 languages)
  - [ ] Each reference is self-contained (no cross-references to other references)

- ✅ **Template**:
  - [ ] observability-stack-setup.md (~1,800 words)
  - [ ] Docker Compose configuration for complete stack
  - [ ] Production deployment considerations

- ✅ **Example**:
  - [ ] express-microservices-observability.md (~2,700 words)
  - [ ] Working code examples for all three services
  - [ ] Complete debugging scenario demonstrating unified workflow

- ✅ **Integration**:
  - [ ] Cross-references added to pact-api-design, pact-backend-patterns, pact-database-patterns
  - [ ] Agent integration documented (backend-coder, database-engineer, frontend-coder, architect)

### 8.2 Quality Standards

Every code example must:
- [ ] Be executable (no pseudocode)
- [ ] Include error handling
- [ ] Follow language-specific best practices
- [ ] Include comments explaining key concepts

Every decision tree must:
- [ ] Cover all common scenarios
- [ ] Provide clear routing based on criteria
- [ ] Include default recommendations

Every platform comparison must:
- [ ] Be vendor-neutral (present objective trade-offs)
- [ ] Include cost considerations
- [ ] Specify when to choose each option

### 8.3 Production-Ready Validation

Patterns must be:
- [ ] Based on 2025 industry standards (OpenTelemetry, W3C Trace Context)
- [ ] Production-tested (not toy examples)
- [ ] Security-conscious (PII redaction, secure propagation)
- [ ] Performance-aware (async logging, sampling strategies)
- [ ] Cost-conscious (sampling, retention, storage considerations)

---

## 9. Implementation Roadmap

### Phase 1: Core Content Creation
1. Create SKILL.md with all 9 sections
2. Create logging-patterns.md reference file
3. Create metrics-collection.md reference file
4. Create distributed-tracing.md reference file

### Phase 2: Templates and Examples
5. Create observability-stack-setup.md template
6. Create express-microservices-observability.md example

### Phase 3: Integration
7. Update pact-api-design with cross-reference
8. Update pact-backend-patterns with cross-reference
9. Update pact-database-patterns with cross-reference
10. Document agent integration in agent files (if needed)

### Phase 4: Review and Refinement
11. Verify all quality gates
12. Test code examples in each language
13. Validate decision trees with real-world scenarios
14. Peer review for completeness and accuracy

---

## 10. Handoff to Code Phase

**Status**: ✅ ARCHITECT PHASE COMPLETE

**Deliverables Created**:
- Comprehensive architecture specification saved to `/Users/mj/Sites/collab/PACT-prompt/docs/architecture/pact-observability-patterns-design.md`

**Architecture Summary**:
- **Skill Structure**: SKILL.md (~3,500 words) + 3 reference files (~2,500 words each) + 1 template (~1,800 words) + 1 example (~2,700 words)
- **Total Content**: ~13,500 words across 6 files
- **Approach**: Progressive disclosure (quick reference → detailed guidance → deep references)
- **Standards**: OpenTelemetry as primary instrumentation, vendor-neutral platform comparisons
- **Integration**: Cross-references to 5 existing skills, used by 4 agents

**Ready for CODE Phase**:
- All sections outlined with word count targets
- Code examples specified for Node.js, Python, Java
- Decision trees defined for tool selection
- Template and example scoped and outlined
- Quality gates and success criteria established

**Next Phase**: CODE phase to implement skill files following this architecture specification.

---

*Architecture design completed by 🏛️ PACT Architect on 2025-12-07*
