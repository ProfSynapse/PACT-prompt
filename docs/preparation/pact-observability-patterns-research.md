# PACT Observability Patterns Skill - Preparation Research

**Date**: 2025-12-07
**Phase**: Prepare
**GitHub Issue**: #5

---

## Executive Summary

This research supports the creation of a new `pact-observability-patterns` skill for the PACT framework. The skill will provide comprehensive guidance on logging, metrics, distributed tracing, and APM integration patterns for backend developers.

**Key Findings**:
- Existing PACT skills contain scattered observability content across three skills (API Design, Backend Patterns, Database Patterns)
- Current coverage is introductory (~300 words per skill) and lacks depth for production implementation
- New skill should focus on OpenTelemetry as the universal standard for instrumentation
- Reference files should cover: structured logging patterns, metrics collection (RED/USE), distributed tracing implementation
- Strong integration opportunities with existing backend-coder, api-design, and database-engineer agents

**Recommendation**: Create standalone `pact-observability-patterns` skill with 3 detailed reference files and integration points across all CODE phase agents.

---

## 1. Existing Observability Content Analysis

### 1.1 pact-api-design (Lines 332-383)

**Section**: API Observability
**Word Count**: ~300 words
**Content Quality**: Introductory, focuses on HTTP layer

**Coverage**:
- Request/response logging with correlation IDs
- API-specific metrics (latency, error rate, request rate, payload size)
- Health check endpoints (liveness vs readiness)

**Strengths**:
- Correlation ID propagation example (JavaScript)
- Differentiation between `/health` and `/health/ready`
- Practical metric categories (p50, p95, p99 latencies)

**Gaps**:
- No guidance on log aggregation or structured logging format
- Metrics collection implementation details missing (how to instrument)
- No tracing context propagation beyond correlation IDs
- No APM tool integration guidance

### 1.2 pact-backend-patterns (Lines 343-382)

**Section**: Observability Patterns
**Word Count**: ~400 words
**Content Quality**: Intermediate, broader backend focus

**Coverage**:
- Structured logging with context fields
- Log levels with semantic guidance (ERROR requires action, WARN potential issue, INFO business events, DEBUG troubleshooting)
- Key backend metrics (request rate, error rate, latency percentiles, connection pool, business metrics)
- Distributed tracing basics with span context propagation example

**Strengths**:
- Structured logging example with business context (correlationId, userId, amount, currency, duration)
- Clear log level semantics tied to operational urgency
- Practical distributed tracing code snippet (JavaScript with tracer.extract/startSpan)
- Correlation ID generation and propagation

**Gaps**:
- No structured logging format specification (JSON vs text)
- Missing metrics collection libraries (Prometheus client, StatsD)
- No sampling strategies for tracing
- No guidance on log aggregation systems
- Missing APM integration patterns

### 1.3 pact-database-patterns (Lines 435-467)

**Section**: Database Observability
**Word Count**: ~300 words
**Content Quality**: Intermediate, database-specific

**Coverage**:
- Query performance monitoring (execution time tracking)
- Connection pool metrics (active connections, wait time, lifetime, exhaustion)
- Slow query logging configuration (PostgreSQL examples)
- Query execution context logging

**Strengths**:
- Practical query instrumentation code (JavaScript with duration tracking)
- Database-specific slow query thresholds (100ms)
- PostgreSQL configuration examples (log_min_duration_statement, log_line_prefix)
- Connection pool health metrics

**Gaps**:
- No guidance on query performance metrics aggregation
- Missing database-specific tracing integration
- No discussion of database APM integration
- Limited to PostgreSQL examples (no MySQL, MongoDB, etc.)

### 1.4 Coverage Summary

| Topic | API Design | Backend Patterns | Database Patterns | Total Coverage |
|-------|-----------|-----------------|-------------------|----------------|
| **Logging** | Basic (correlation) | Intermediate (structured) | Basic (slow query) | ~30% |
| **Metrics** | API-specific | Backend-specific | DB-specific | ~40% |
| **Tracing** | Correlation IDs only | Distributed tracing basics | None | ~20% |
| **APM Integration** | None | None | None | 0% |
| **Log Aggregation** | None | None | None | 0% |
| **OpenTelemetry** | None | None | None | 0% |

**Overall Assessment**: Current observability content is **fragmented and introductory**. Each skill provides domain-specific observability guidance, but lacks:
- Unified observability strategy across the stack
- Production-grade implementation patterns
- OpenTelemetry integration (industry standard)
- APM tool selection and configuration
- Log aggregation system integration

---

## 2. Gap Analysis

### 2.1 Critical Gaps (Must Address in New Skill)

**Gap 1: OpenTelemetry Integration**
- **Current State**: No mention of OpenTelemetry (OTel) in any skill
- **Industry Standard**: OTel is the W3C and CNCF standard for observability (2025)
- **Impact**: Developers lack guidance on industry-standard instrumentation
- **Recommendation**: Make OpenTelemetry the primary instrumentation framework in new skill

**Gap 2: APM Tool Selection and Integration**
- **Current State**: Zero coverage of APM platforms (DataDog, New Relic, Application Insights, Grafana)
- **Developer Need**: Teams need guidance choosing and integrating APM tools
- **Impact**: Developers either don't use APM or make uninformed vendor choices
- **Recommendation**: Dedicated reference file comparing APM tools with decision tree

**Gap 3: Log Aggregation Systems**
- **Current State**: No guidance on ELK, Loki, Datadog Logs, or other aggregation platforms
- **Developer Need**: Logs scattered across services without centralized analysis
- **Impact**: Debugging distributed systems becomes nearly impossible
- **Recommendation**: Reference file on log aggregation patterns with system comparison

**Gap 4: Metrics Collection Libraries and Standards**
- **Current State**: Metrics mentioned but no implementation guidance
- **Developer Need**: How to instrument code with Prometheus, StatsD, OpenTelemetry metrics
- **Impact**: Teams either don't collect metrics or use inconsistent approaches
- **Recommendation**: Metrics reference file with RED/USE method and library examples

**Gap 5: Distributed Tracing Production Patterns**
- **Current State**: Basic tracing example without sampling, context propagation standards, or backend integration
- **Developer Need**: Production-ready tracing with W3C Trace Context, sampling strategies, trace storage
- **Impact**: Traces either missing, incomplete, or cause performance overhead
- **Recommendation**: Distributed tracing reference file with OpenTelemetry, sampling, and context propagation

**Gap 6: Observability Strategy and the Three Pillars**
- **Current State**: No unified framework explaining logs, metrics, and traces relationship
- **Developer Need**: Understanding when to use each pillar and how they complement each other
- **Impact**: Over-reliance on one pillar (usually logs) without holistic observability
- **Recommendation**: SKILL.md overview section explaining three pillars integration

### 2.2 Secondary Gaps (Nice to Have)

- **Performance impact of instrumentation**: Overhead of logging, metrics, tracing
- **Observability for serverless/edge**: Lambda, Cloudflare Workers observability patterns
- **Cost optimization**: Managing observability costs at scale (sampling, retention, aggregation)
- **Security considerations**: PII in logs, secure trace propagation, access control for telemetry
- **Alerting patterns**: Thresholds, anomaly detection, on-call workflows
- **SRE/SLO integration**: Service Level Objectives, error budgets, uptime tracking

---

## 3. Technology Research Findings

### 3.1 OpenTelemetry (OTel) - Industry Standard

**Status**: W3C and CNCF standard for observability (2025)
**Adoption**: Universal standard across all major APM vendors

**Key Capabilities**:
- **Unified instrumentation**: Single API for metrics, logs, and traces
- **Vendor-neutral**: Export to any backend (DataDog, New Relic, Grafana, Jaeger, etc.)
- **Auto-instrumentation**: Zero-code instrumentation for many frameworks
- **W3C Trace Context**: Standard for context propagation across services
- **Language support**: SDKs for all major languages (Python, Node.js, Java, Go, .NET, Ruby)

**Best Practices** (Sources: [Grafana Labs](https://grafana.com/blog/2023/12/18/opentelemetry-best-practices-a-users-guide-to-getting-started-with-opentelemetry/), [Better Stack](https://betterstack.com/community/guides/observability/opentelemetry-best-practices/)):
1. **Start with auto-instrumentation**: Covers 80% of use cases without code changes
2. **Initialize before framework**: OTel must initialize before instrumented libraries load
3. **Use semantic conventions**: Standard attribute names for consistency (http.method, db.system, etc.)
4. **Sampling strategies**: Combine probabilistic sampling (1-10% normal traffic) with error/latency-based tail sampling
5. **Context propagation**: Always propagate W3C Trace Context headers across services
6. **Collector deployment**: Use OTel Collector for batching, filtering, and routing telemetry
7. **Correlation**: Log trace IDs in application logs for unified debugging

**Implementation Pattern**:
```javascript
// Initialize OpenTelemetry before framework imports
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({ url: 'http://collector:4318/v1/traces' }),
  instrumentations: [getNodeAutoInstrumentations()],
  serviceName: 'payment-service',
});

sdk.start();

// Now import application framework
import express from 'express';
```

**Recommendation**: Make OpenTelemetry the primary instrumentation approach in the new skill, with language-specific examples.

### 3.2 Structured Logging Standards

**Status**: JSON logging is industry standard (2025)
**Adoption**: All major log aggregation platforms support structured JSON

**Best Practices** (Sources: [Uptrace](https://uptrace.dev/glossary/structured-logging), [Dash0](https://www.dash0.com/guides/structured-logging-for-modern-applications)):
1. **JSON format**: Use JSON for all structured logs (1.5-2x storage overhead vs plain text, 60-80% reduction with compression)
2. **Correlation IDs**: Include `X-Correlation-ID` in every log entry (de facto standard header name)
3. **Essential fields**: timestamp (ISO 8601 UTC), level, message, service, traceId, spanId, userId/sessionId
4. **Consistent naming**: Use same field names across services (avoid `user_id` vs `userId` inconsistency)
5. **Log levels**: ERROR (action required), WARN (potential issue), INFO (business events), DEBUG (troubleshooting)
6. **Security**: Never log passwords, PII, credit cards (implement masking/redaction)
7. **Performance**: Async logging to avoid blocking I/O
8. **OpenTelemetry integration**: Include OTel trace context (traceId, spanId) for correlation

**Example Structured Log Entry**:
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

**Language-Specific Libraries**:
- **Node.js**: Pino, Winston
- **Python**: Loguru, structlog
- **Java**: Logback with JSON encoder
- **C#/.NET**: Serilog
- **Go**: zap, zerolog
- **Ruby**: Semantic Logger

**Recommendation**: Create reference file with structured logging patterns, field naming conventions, and language-specific examples.

### 3.3 Metrics Collection - RED and USE Methods

**Status**: RED (request-driven services) and USE (resource monitoring) are SRE industry standards
**Adoption**: Prometheus is dominant metrics standard (CNCF graduated project)

**RED Method** (Sources: [SUSE/Rancher](https://www.suse.com/c/rancher_blog/red-method-for-prometheus-3-key-metrics-for-monitoring/), [Weave Works](https://www.weave.works/blog/the-red-method-key-metrics-for-microservices-architecture/)):
- **Rate**: Requests per second (throughput)
- **Errors**: Percentage of failed requests (error rate as proportion of request rate)
- **Duration**: Latency distribution (p50, p95, p99)
- **Use case**: Request-driven services (APIs, web servers, microservices)

**USE Method**:
- **Utilization**: Percentage of resource capacity used (CPU, memory, disk)
- **Saturation**: Queue length or waiting work (requests waiting, connection pool exhaustion)
- **Errors**: Error count (connection failures, timeouts)
- **Use case**: Infrastructure and resource monitoring (hosts, databases, caches)

**Prometheus Naming Conventions** (Source: [Prometheus Docs](https://prometheus.io/docs/practices/naming/)):
- Lowercase with underscores: `http_requests_total`, `db_query_duration_seconds`
- Suffix with unit: `_seconds`, `_bytes`, `_total` (counter)
- Use labels for dimensions: `method="POST"`, `status="200"`, `endpoint="/api/users"`

**Example Prometheus Instrumentation**:
```javascript
// Node.js with prom-client
const promClient = require('prom-client');

// RED metrics
const httpRequestsTotal = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total HTTP requests',
  labelNames: ['method', 'endpoint', 'status']
});

const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request duration',
  labelNames: ['method', 'endpoint'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5]
});

// Middleware to instrument
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    httpRequestsTotal.inc({ method: req.method, endpoint: req.route?.path, status: res.statusCode });
    httpRequestDuration.observe({ method: req.method, endpoint: req.route?.path }, duration);
  });
  next();
});
```

**Best Practices**:
1. **Initialize metrics to zero**: Prevent missing metrics in dashboards
2. **Cardinality control**: Avoid high-cardinality labels (user IDs, request IDs) - causes memory explosion
3. **Buckets for histograms**: Choose appropriate latency buckets (0.01s, 0.1s, 1s, 10s)
4. **Business metrics**: Track domain-specific metrics (signups/hour, orders/minute, revenue)

**Recommendation**: Create metrics reference file with RED/USE decision tree, Prometheus examples, and OpenTelemetry metrics SDK.

### 3.4 Distributed Tracing - W3C Trace Context

**Status**: W3C Trace Context is standard for context propagation (2025)
**Adoption**: Supported by all major tracing backends (Jaeger, Zipkin, DataDog, New Relic, Grafana Tempo)

**W3C Trace Context** (Sources: [W3C Spec](https://www.w3.org/TR/trace-context/), [OpenTelemetry Docs](https://opentelemetry.io/docs/concepts/context-propagation/), [Datadog](https://docs.datadoghq.com/tracing/trace_collection/trace_context_propagation/)):
- **Standard headers**: `traceparent` (HTTP), `grpc-trace-bin` (gRPC)
- **traceparent format**: `00-<trace-id>-<parent-id>-<trace-flags>`
  - Example: `00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01`
- **Context propagation**: Automatically propagated by OpenTelemetry SDKs
- **Interoperability**: Single trace can span multiple vendors (DataDog → New Relic → open-source)

**Sampling Strategies** (Source: [Better Stack](https://betterstack.com/community/guides/observability/opentelemetry-best-practices/)):
1. **Head sampling**: Decision at trace start (simple, can miss important traces)
   - Probabilistic: Sample 1-10% of all traces randomly
   - Rate limiting: Sample first N traces per second
2. **Tail sampling**: Decision after trace completion (intelligent, requires buffering)
   - Error-based: Always keep traces with errors
   - Latency-based: Keep slow traces (>2s)
   - Hybrid: Probabilistic + always keep errors/slow traces

**Tracing Best Practices**:
- **Span naming**: Use high-level operation names (`GET /api/users`, `db.query.users.findById`)
- **Span attributes**: Include semantic conventions (http.method, http.status_code, db.system)
- **Correlation with logs**: Log trace ID and span ID in application logs
- **Sampling**: Start with 1-5% probabilistic, adjust based on volume and debugging needs
- **Storage**: Traces are expensive - use retention policies (7-30 days common)

**Example OpenTelemetry Tracing**:
```javascript
import { trace } from '@opentelemetry/api';

const tracer = trace.getTracer('payment-service');

async function processPayment(amount, currency) {
  return tracer.startActiveSpan('processPayment', async (span) => {
    try {
      span.setAttribute('payment.amount', amount);
      span.setAttribute('payment.currency', currency);

      const result = await paymentGateway.charge(amount, currency);
      span.setStatus({ code: SpanStatusCode.OK });
      return result;
    } catch (error) {
      span.recordException(error);
      span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
      throw error;
    } finally {
      span.end();
    }
  });
}
```

**Recommendation**: Create distributed tracing reference file with OpenTelemetry integration, W3C Trace Context propagation, and sampling strategies.

### 3.5 APM Platform Comparison (2025)

**Scope**: Comparing DataDog, New Relic, and Azure Application Insights
**Sources**: [CloudZero](https://www.cloudzero.com/blog/datadog-vs-new-relic/), [SigNoz](https://signoz.io/blog/datadog-vs-newrelic/), [Better Stack](https://betterstack.com/community/comparisons/datadog-vs-newrelic/)

#### DataDog
**Strengths**:
- **Infrastructure monitoring**: Started as infrastructure tool, excels at server/container metrics
- **Integrations**: 800+ integrations (most extensive ecosystem)
- **Customization**: Granular control, advanced analytics, powerful query language (DQL)
- **Multi-cloud**: Best for complex, multi-cloud environments

**Pricing**: Modular (pay per component)
- APM: $31-40/host/month
- Logs: $0.10/GB ingested + $1.70/million events indexed
- Custom metrics: Volume-based pricing
- **Warning**: Pricing complexity and unpredictability are common complaints

**When to choose**: Complex infrastructure, dedicated DevOps team, need deep customization

#### New Relic
**Strengths**:
- **All-in-one pricing**: Consumption-based (per user + per GB), all features included
- **Ease of use**: Simpler interface, better for smaller teams
- **AI analytics**: Leading AI-powered anomaly detection and insights (2025)
- **NRQL**: Powerful yet accessible query language

**Pricing**:
- Standard tier: 1 user + 100 GB/month free
- Pro tier: $99/user/month + $0.35/GB ingested
- Enterprise: $549/user/month + $0.50/GB ingested

**When to choose**: Predictable pricing, smaller teams, want simplicity and AI-powered insights

#### Azure Application Insights
**Strengths**:
- **Azure integration**: Native Azure integration, no agent required for App Service, Functions
- **Cost-effective**: For Azure-heavy workloads, often cheaper than DataDog/New Relic
- **Automatic instrumentation**: Zero-code for Azure services
- **.NET focus**: Best APM for .NET applications

**Pricing**:
- First 5 GB/month free per subscription
- $2.30/GB beyond free tier
- Log Analytics: $2.76/GB ingested + $0.12/GB retention >31 days

**When to choose**: Azure-centric architecture, Microsoft/.NET stack, budget-conscious

#### Open-Source Alternative: Grafana Stack (LGTM)
**Components**: Loki (logs), Grafana (visualization), Tempo (tracing), Mimir (metrics)
**Strengths**:
- **Cost**: Free for self-hosted (infrastructure costs only)
- **Prometheus compatibility**: Native PromQL support
- **Kubernetes-native**: Ideal for Kubernetes/container environments

**Trade-offs**: Requires operational expertise, less polished UX than commercial APM

**When to choose**: Budget constraints, Kubernetes-heavy, strong DevOps team

#### Decision Matrix

| Criterion | DataDog | New Relic | App Insights | Grafana Stack |
|-----------|---------|-----------|--------------|---------------|
| **Infrastructure monitoring** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Ease of use** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Pricing transparency** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **AI/ML insights** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Multi-cloud** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Total cost (high volume)** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Recommendation**: Create APM integration reference file with decision tree based on team size, budget, infrastructure complexity, and cloud platform.

### 3.6 Log Aggregation Systems Comparison

**Scope**: Comparing ELK Stack, Grafana Loki, and DataDog Logs
**Sources**: [Dash0](https://www.dash0.com/comparisons/best-log-monitoring-tools-2025), [SigNoz](https://signoz.io/blog/elk-alternatives/), [SigNoz Datadog vs Elastic](https://signoz.io/comparisons/datadog-vs-elasticstack/)

#### ELK Stack (Elasticsearch, Logstash, Kibana)
**Strengths**:
- **Powerful search**: Elasticsearch full-text search is industry-leading
- **Visualization**: Kibana dashboards are flexible and feature-rich
- **Ecosystem**: Rich plugin ecosystem, established platform
- **On-premises**: Full control for compliance/security requirements

**Weaknesses**:
- **Resource-intensive**: High memory/CPU usage, expensive at scale
- **Operational complexity**: Requires dedicated team to maintain
- **Cost**: Cloud-hosted ELK (Elastic Cloud) is comparable to DataDog pricing

**When to choose**: On-premises requirements, full-text search priority, established ELK expertise

#### Grafana Loki
**Strengths**:
- **Cost-effective**: Indexes only metadata (labels), stores compressed logs in object storage (S3)
- **Prometheus-like**: LogQL inspired by PromQL (low learning curve for Prometheus users)
- **Kubernetes-native**: Ideal for container/Kubernetes logs
- **Storage efficiency**: 10x cheaper storage than Elasticsearch

**Weaknesses**:
- **Limited search**: No full-text indexing (search by labels only, then grep log content)
- **Ecosystem dependency**: Works best with Grafana, less standalone value

**When to choose**: Kubernetes/containers, cost-conscious, already using Prometheus/Grafana

#### DataDog Logs
**Strengths**:
- **Integrated**: Unified with APM, metrics, traces in single platform
- **Ease of use**: Simple configuration, automatic log parsing
- **Correlation**: Native correlation between logs, traces, and metrics

**Pricing**:
- $0.10/GB ingested
- $1.70/million log events indexed

**When to choose**: Already using DataDog APM, want unified observability platform

#### Decision Tree

```
START: Choose log aggregation system

├─ On-premises requirement?
│  └─ YES → ELK Stack (Elasticsearch + Logstash + Kibana)
│
├─ Kubernetes/container-heavy?
│  └─ YES → Grafana Loki (cost-effective, Kubernetes-native)
│
├─ Already using DataDog APM?
│  └─ YES → DataDog Logs (unified platform, automatic correlation)
│
├─ Need full-text search across all logs?
│  └─ YES → ELK Stack or DataDog Logs
│
├─ Budget-constrained with high log volume?
│  └─ YES → Grafana Loki (10x cheaper storage)
│
└─ Default → Start with Grafana Loki, migrate to ELK/DataDog if search needs grow
```

**Recommendation**: Include log aggregation comparison in APM/logging reference file with cost/feature trade-offs.

---

## 4. Recommended Skill Structure

### 4.1 SKILL.md Structure (~3,500 words)

Based on `pact-architecture-patterns` template structure:

**Section 1: Overview** (~300 words)
- Purpose of observability in PACT framework
- Integration with CODE phase (backend, frontend, database)
- When to use this skill

**Section 2: Quick Reference - The Three Pillars** (~600 words)
- **Metrics**: What to measure (RED/USE), when to use
- **Logs**: Structured logging, when to use
- **Traces**: Distributed tracing, when to use
- Decision tree: Which pillar to use for different debugging scenarios

**Section 3: Available MCP Tools** (~200 words)
- sequential-thinking for complex observability architecture decisions

**Section 4: OpenTelemetry Integration** (~500 words)
- Why OpenTelemetry is the standard
- Auto-instrumentation vs manual instrumentation
- Initialization best practices
- Semantic conventions
- Context propagation (W3C Trace Context)

**Section 5: Observability Patterns by Domain** (~800 words)
- **API Observability**: Request/response logging, API metrics, health checks (links to pact-api-design)
- **Backend Observability**: Structured logging, business metrics, distributed tracing (links to pact-backend-patterns)
- **Database Observability**: Query performance, connection pool metrics, slow query logs (links to pact-database-patterns)

**Section 6: APM Platform Selection** (~400 words)
- When to use APM tools vs open-source
- Decision tree: DataDog vs New Relic vs Application Insights vs Grafana
- Cost considerations
- Link to detailed reference file

**Section 7: Decision Tree - Which Reference to Use** (~300 words)
- Implementing structured logging → `references/logging-patterns.md`
- Collecting metrics → `references/metrics-collection.md`
- Implementing distributed tracing → `references/distributed-tracing.md`

**Section 8: Common Anti-Patterns** (~200 words)
- Logging PII/secrets
- High-cardinality metrics labels
- Over-tracing (100% sampling in production)
- Unstructured logs in production

**Section 9: Integration with PACT Workflow** (~200 words)
- Input from Architecture phase
- Output to Test phase
- Cross-references to backend-coder, api-design, database-engineer

### 4.2 Reference Files (3 files)

#### references/logging-patterns.md (~2,500 words)

**Sections**:
1. **Structured Logging Fundamentals** (~500 words)
   - JSON vs plain text comparison
   - Essential fields (timestamp, level, message, service, traceId, correlationId)
   - Field naming conventions
   - Log levels semantic guidance

2. **Language-Specific Implementation** (~800 words)
   - Node.js: Pino, Winston examples
   - Python: Loguru, structlog examples
   - Java: Logback with JSON encoder
   - C#/.NET: Serilog
   - Go: zap, zerolog
   - Ruby: Semantic Logger

3. **Correlation and Context Propagation** (~400 words)
   - Correlation ID generation strategies (UUID, request ID)
   - Propagating correlation IDs across services
   - Integrating OpenTelemetry trace/span IDs in logs
   - Example: Express middleware for correlation

4. **Log Aggregation Systems** (~600 words)
   - ELK Stack: Setup, use cases, pros/cons
   - Grafana Loki: Setup, use cases, pros/cons
   - DataDog Logs: Setup, use cases, pros/cons
   - Decision matrix comparison table
   - Configuration examples for each system

5. **Security and Performance** (~200 words)
   - PII redaction/masking patterns
   - Async logging for performance
   - Log sampling for high-volume services
   - Storage and retention policies

#### references/metrics-collection.md (~2,500 words)

**Sections**:
1. **Metrics Fundamentals** (~400 words)
   - Types: Counter, Gauge, Histogram, Summary
   - RED method (Rate, Errors, Duration) for request-driven services
   - USE method (Utilization, Saturation, Errors) for resources
   - When to use RED vs USE

2. **Prometheus Implementation** (~800 words)
   - Metric naming conventions
   - Label design patterns (avoid high cardinality)
   - Histogram bucket selection
   - Node.js: prom-client examples
   - Python: prometheus_client examples
   - Java: Micrometer examples
   - Exposing /metrics endpoint

3. **OpenTelemetry Metrics** (~600 words)
   - OTel Metrics API vs Prometheus client
   - Semantic conventions for metrics
   - Exporting to Prometheus, DataDog, New Relic
   - Example: Instrumenting Express app with OTel metrics

4. **Business Metrics** (~300 words)
   - Domain-specific metrics (signups, orders, revenue)
   - SLO/SLI tracking (availability, latency)
   - Custom metrics vs standard metrics

5. **Metrics Storage and Visualization** (~400 words)
   - Prometheus + Grafana setup
   - DataDog metrics integration
   - New Relic metrics integration
   - Alerting based on metrics (threshold, anomaly detection)

#### references/distributed-tracing.md (~2,500 words)

**Sections**:
1. **Distributed Tracing Fundamentals** (~400 words)
   - Traces, spans, and context
   - Why tracing is critical for microservices
   - W3C Trace Context standard
   - traceparent header format

2. **OpenTelemetry Tracing** (~900 words)
   - Auto-instrumentation setup (Node.js, Python, Java)
   - Manual instrumentation for custom spans
   - Span attributes (semantic conventions)
   - Context propagation across HTTP, gRPC, message queues
   - Example: Multi-service trace (API Gateway → Service A → Service B → Database)

3. **Sampling Strategies** (~500 words)
   - Head sampling: Probabilistic, rate-limiting
   - Tail sampling: Error-based, latency-based, hybrid
   - Trade-offs: Cost vs completeness
   - Configuration examples for OTel Collector

4. **Trace Backends** (~600 words)
   - Jaeger: Setup, use cases, pros/cons
   - Zipkin: Setup, use cases, pros/cons
   - Grafana Tempo: Setup, use cases, pros/cons
   - DataDog APM: Integration, features
   - New Relic: Integration, features
   - Comparison table

5. **Correlation with Logs and Metrics** (~100 words)
   - Logging trace/span IDs in application logs
   - Linking traces to metrics dashboards
   - Unified debugging workflow (metric alert → trace → logs)

### 4.3 Templates (Optional for Future)

- **templates/observability-setup.md**: Complete observability stack setup guide (OpenTelemetry + Prometheus + Loki + Grafana)
- **templates/apm-integration.md**: APM integration checklist with vendor-specific steps

### 4.4 Examples (Optional for Future)

- **examples/express-observability.md**: Complete Express.js app with OTel, structured logging, Prometheus metrics
- **examples/microservices-tracing.md**: Multi-service distributed tracing example with context propagation

---

## 5. Integration with Existing Skills

### 5.1 Related Skills (Cross-References)

**From pact-observability-patterns to:**
- **pact-backend-patterns**: Reference observability patterns for backend service implementation
- **pact-api-design**: Reference API observability patterns for HTTP layer monitoring
- **pact-database-patterns**: Reference database observability patterns for query monitoring
- **pact-security-patterns**: Secure logging practices (PII redaction, audit logs)
- **pact-testing-patterns**: Testing observability instrumentation (verify metrics emitted, logs generated)

**To pact-observability-patterns from:**
- **pact-backend-coder**: Invoke when implementing logging, metrics, or tracing in backend services
- **pact-frontend-coder**: Invoke when implementing frontend observability (RUM, error tracking)
- **pact-database-engineer**: Invoke when implementing database query monitoring
- **pact-architect**: Invoke when designing observability architecture (log aggregation, APM selection)

### 5.2 Skill Description Field

Following the pattern from other skills, the `description` field should be comprehensive to ensure proper auto-activation:

```yaml
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
```

### 5.3 Update Required in Existing Skills

To maintain consistency, update observability sections in existing skills to reference the new skill:

**pact-api-design (line 332)**: Add cross-reference
```markdown
## API Observability

For comprehensive observability patterns, see the `pact-observability-patterns` skill. This section
covers API-specific observability concerns.

[existing content...]
```

**pact-backend-patterns (line 343)**: Add cross-reference
```markdown
## Observability Patterns

For comprehensive observability patterns including OpenTelemetry integration and APM tools,
see the `pact-observability-patterns` skill. This section covers backend-specific concerns.

[existing content...]
```

**pact-database-patterns (line 435)**: Add cross-reference
```markdown
## Database Observability

For comprehensive observability patterns including log aggregation and distributed tracing,
see the `pact-observability-patterns` skill. This section covers database-specific concerns.

[existing content...]
```

---

## 6. Skill Metadata

### 6.1 SKILL.md Frontmatter

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

### 6.2 Skill File Structure

```
skills/pact-observability-patterns/
├── SKILL.md                              # Main skill definition (~3,500 words)
├── references/
│   ├── logging-patterns.md               # Structured logging reference (~2,500 words)
│   ├── metrics-collection.md             # Metrics and RED/USE method (~2,500 words)
│   └── distributed-tracing.md            # Tracing and OpenTelemetry (~2,500 words)
├── templates/ (future)
│   ├── observability-setup.md            # Complete stack setup guide
│   └── apm-integration.md                # APM integration checklist
└── examples/ (future)
    ├── express-observability.md          # Full Express.js observability example
    └── microservices-tracing.md          # Multi-service tracing example
```

**Total word count**: ~11,500 words (SKILL.md + 3 references)

---

## 7. Quality Standards and Success Criteria

### 7.1 Quality Standards

Following PACT framework principles:

1. **Actionable Guidance**: Every pattern includes code examples in 2+ languages
2. **Decision Support**: Decision trees for choosing between tools/approaches
3. **Current Standards**: Focus on 2025 industry standards (OpenTelemetry, W3C Trace Context)
4. **Vendor-Neutral**: Present open-source and commercial options with objective trade-offs
5. **Integration**: Clear cross-references to other PACT skills
6. **Production-Ready**: Patterns are production-grade, not toy examples
7. **Security-First**: Security considerations integrated throughout (PII redaction, secure propagation)

### 7.2 Success Criteria

The skill is complete when:

- ✅ All 3 reference files created with 2,500 words each
- ✅ SKILL.md overview provides clear decision trees for all major observability decisions
- ✅ OpenTelemetry is positioned as primary instrumentation standard
- ✅ Code examples cover Node.js, Python, Java (minimum 3 languages)
- ✅ APM comparison includes DataDog, New Relic, Application Insights, Grafana Stack
- ✅ Log aggregation comparison includes ELK, Loki, DataDog Logs
- ✅ RED method and USE method clearly explained with examples
- ✅ W3C Trace Context propagation documented with examples
- ✅ Sampling strategies (head vs tail) explained with configuration examples
- ✅ Security considerations (PII redaction, secure logging) integrated throughout
- ✅ Cross-references to pact-backend-patterns, pact-api-design, pact-database-patterns added
- ✅ Existing skills updated with references to new observability skill

---

## 8. Resources and Sources

### 8.1 Web Research Sources

**OpenTelemetry**:
- [OpenTelemetry Best Practices - Grafana Labs](https://grafana.com/blog/2023/12/18/opentelemetry-best-practices-a-users-guide-to-getting-started-with-opentelemetry/)
- [Essential OpenTelemetry Best Practices - Better Stack](https://betterstack.com/community/guides/observability/opentelemetry-best-practices/)
- [OpenTelemetry Tracing Guide - vFunction](https://vfunction.com/blog/opentelemetry-tracing-guide/)
- [OpenTelemetry NestJS Implementation - SigNoz](https://signoz.io/blog/opentelemetry-nestjs/)
- [Context Propagation - OpenTelemetry Docs](https://opentelemetry.io/docs/concepts/context-propagation/)

**Structured Logging**:
- [Structured Logging Best Practices - Uptrace](https://uptrace.dev/glossary/structured-logging)
- [Practical Structured Logging - Dash0](https://www.dash0.com/guides/structured-logging-for-modern-applications)
- [Logging and Correlation ID Patterns - prgrmmng.com](https://prgrmmng.com/logging-correlation-id-pattern-java)
- [Log Formatting in Production - Better Stack](https://betterstack.com/community/guides/logging/log-formatting/)

**Metrics and Monitoring**:
- [RED Method for Prometheus - SUSE/Rancher](https://www.suse.com/c/rancher_blog/red-method-for-prometheus-3-key-metrics-for-monitoring/)
- [RED Method - Weave Works](https://www.weave.works/blog/the-red-method-key-metrics-for-microservices-architecture/)
- [Prometheus Labels Best Practices - CNCF](https://www.cncf.io/blog/2025/07/22/prometheus-labels-understanding-and-best-practices/)
- [Prometheus Best Practices - Better Stack](https://betterstack.com/community/guides/monitoring/prometheus-best-practices/)
- [Metric Naming - Prometheus Docs](https://prometheus.io/docs/practices/naming/)

**Distributed Tracing**:
- [W3C Trace Context Specification](https://www.w3.org/TR/trace-context/)
- [Trace Context Propagation - Datadog](https://docs.datadoghq.com/tracing/trace_collection/trace_context_propagation/)
- [W3C Trace Context Overview - Dapr](https://docs.dapr.io/operations/observability/tracing/w3c-tracing-overview/)
- [Distributed Tracing with W3C Trace Context - Dynatrace](https://www.dynatrace.com/news/blog/distributed-tracing-with-w3c-trace-context-for-improved-end-to-end-visibility/)

**APM Platform Comparisons**:
- [Datadog vs New Relic 2025 - CloudZero](https://www.cloudzero.com/blog/datadog-vs-new-relic/)
- [New Relic vs DataDog - SigNoz](https://signoz.io/blog/datadog-vs-newrelic/)
- [Datadog vs New Relic - Better Stack](https://betterstack.com/community/comparisons/datadog-vs-newrelic/)
- [New Relic vs Datadog - Uptrace](https://uptrace.dev/comparisons/newrelic-vs-datadog)

**Observability Fundamentals**:
- [Three Pillars of Observability - IBM](https://www.ibm.com/think/insights/observability-pillars)
- [Three Pillars Explained - strongDM](https://www.strongdm.com/blog/three-pillars-of-observability)
- [Logs, Metrics, Traces - TechTarget](https://www.techtarget.com/searchitoperations/tip/The-3-pillars-of-observability-Logs-metrics-and-traces)
- [Three Pillars - Netdata](https://www.netdata.cloud/academy/pillars-of-observability/)

**Log Aggregation Systems**:
- [Best Log Monitoring Tools 2025 - Dash0](https://www.dash0.com/comparisons/best-log-monitoring-tools-2025)
- [ELK Alternatives - SigNoz](https://signoz.io/blog/elk-alternatives/)
- [ELK Alternatives 2025 - Medium](https://medium.com/@rostislavdugin/elk-alternatives-in-2025-top-7-tools-for-log-management-caaf54f1379b)
- [Datadog vs Elastic Stack - SigNoz](https://signoz.io/comparisons/datadog-vs-elasticstack/)
- [Grafana + Loki to Replace Datadog - ChaosSearch](https://www.chaossearch.io/blog/why-organizations-use-grafana-loki-to-replace-datadog)

### 8.2 Existing Skill Files

- `/Users/mj/Sites/collab/PACT-prompt/skills/pact-architecture-patterns/SKILL.md` - Template structure
- `/Users/mj/Sites/collab/PACT-prompt/skills/pact-api-design/SKILL.md` - API Observability section (lines 332-383)
- `/Users/mj/Sites/collab/PACT-prompt/skills/pact-backend-patterns/SKILL.md` - Backend Observability section (lines 343-382)
- `/Users/mj/Sites/collab/PACT-prompt/skills/pact-database-patterns/SKILL.md` - Database Observability section (lines 435-467)

### 8.3 Review Documentation

- `/Users/mj/Sites/collab/PACT-prompt/docs/reviews/backend-coder-skill-review.md` - Original recommendation (lines 203-209)

---

## 9. Next Steps for Architect Phase

### 9.1 Immediate Actions for pact-architect

1. **Create SKILL.md structure** (~3,500 words)
   - Follow pact-architecture-patterns template
   - Include all sections outlined in Section 4.1
   - Add decision trees for tool selection
   - Write MCP tools guidance section

2. **Create reference files** (3 files, ~2,500 words each)
   - `references/logging-patterns.md`: Structured logging, correlation, log aggregation
   - `references/metrics-collection.md`: RED/USE, Prometheus, OpenTelemetry metrics
   - `references/distributed-tracing.md`: W3C Trace Context, OpenTelemetry, sampling, backends

3. **Update existing skills** (cross-references)
   - Add reference to pact-observability-patterns in pact-api-design (line 332)
   - Add reference to pact-observability-patterns in pact-backend-patterns (line 343)
   - Add reference to pact-observability-patterns in pact-database-patterns (line 435)

4. **Create GitHub issue checklist** (tracking document)
   - Task list for skill completion
   - Quality gates for review
   - Integration testing checklist

### 9.2 Future Enhancements (Post-v1.0)

**Templates**:
- `templates/observability-setup.md`: Step-by-step OpenTelemetry + Prometheus + Loki + Grafana setup
- `templates/apm-integration.md`: Vendor-specific APM integration checklists

**Examples**:
- `examples/express-observability.md`: Complete Express.js app with full observability stack
- `examples/microservices-tracing.md`: Multi-service example with trace propagation across HTTP, gRPC, message queue

**Additional Topics** (if skill grows):
- Cost optimization strategies (sampling, retention, aggregation)
- Observability for serverless/edge computing
- SRE practices (SLO/SLI tracking, error budgets)
- Advanced alerting patterns (anomaly detection, alert fatigue reduction)

---

## 10. Handoff to Orchestrator

**Status**: ✅ PREPARE PHASE COMPLETE

**Deliverables Created**:
- Comprehensive preparation documentation saved to `/Users/mj/Sites/collab/PACT-prompt/docs/preparation/pact-observability-patterns-research.md`

**Key Findings Summary**:
- Existing observability content is fragmented across 3 skills (~1,000 words total)
- OpenTelemetry is the 2025 industry standard for instrumentation (W3C, CNCF)
- New skill should focus on OpenTelemetry, structured logging, RED/USE metrics, distributed tracing
- Recommended structure: SKILL.md (~3,500 words) + 3 reference files (~2,500 words each)
- Strong integration points with pact-backend-coder, pact-api-design, pact-database-engineer

**Recommendations for Architect Phase**:
1. Create `pact-observability-patterns` skill following pact-architecture-patterns template
2. Make OpenTelemetry the primary instrumentation approach
3. Include decision trees for APM platform selection (DataDog, New Relic, App Insights, Grafana)
4. Provide multi-language code examples (Node.js, Python, Java minimum)
5. Cross-reference existing skills to avoid duplication

**Next Phase**: Ready for **ARCHITECT phase** to design skill structure and create SKILL.md + reference files.

---

*Research completed by 📚 PACT Preparer on 2025-12-07*
