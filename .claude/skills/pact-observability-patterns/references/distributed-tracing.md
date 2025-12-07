# Distributed Tracing Reference

**Purpose**: Comprehensive guide to distributed tracing implementation, OpenTelemetry integration, W3C Trace Context propagation, sampling strategies, and trace backend selection.

**Use this reference when**: Implementing distributed tracing across microservices, setting up OpenTelemetry instrumentation, propagating trace context between services, configuring sampling strategies, choosing trace storage backends, or debugging performance bottlenecks in distributed systems.

---

## 1. Distributed Tracing Fundamentals

### What is Distributed Tracing?

Distributed tracing tracks individual requests as they flow through multiple services in a distributed system. Unlike traditional logging or metrics, tracing provides **end-to-end visibility** of a single transaction across service boundaries, enabling developers to identify latency bottlenecks and debug complex failures.

**Core Concepts**:

- **Trace**: The complete journey of a single request through your system, identified by a globally unique trace ID. A trace represents the entire execution path from the initial request to the final response.
- **Span**: A single operation within a trace (e.g., HTTP request, database query, external API call). Each span has a unique span ID, start time, duration, and parent-child relationships with other spans.
- **Context**: Metadata propagated across service boundaries containing trace ID, span ID, and sampling decisions. Context enables correlation between spans in different services.

### Why Distributed Tracing is Critical for Microservices

In microservice architectures, a single user request often triggers dozens of inter-service calls. Without distributed tracing, diagnosing issues becomes nearly impossible:

**Challenges without tracing**:
- **Latency investigation**: "Why did this API call take 5 seconds?" requires manually correlating logs across 10+ services
- **Failure attribution**: "Which service caused the 500 error?" is ambiguous when multiple services are involved
- **Dependency analysis**: "Which services does this endpoint depend on?" requires reading code or running production tests
- **Performance optimization**: "Where should we optimize first?" relies on guesswork without visibility into span durations

**Benefits of distributed tracing**:
- **Visual request flow**: See exactly which services were called, in what order, and how long each took
- **Latency attribution**: Identify which service (or which operation within a service) is slow
- **Error propagation**: Trace errors back to their origin, even through multiple service hops
- **Dependency mapping**: Automatically generate service dependency graphs from trace data
- **Performance profiling**: Understand where time is spent in complex workflows

### W3C Trace Context Standard

The **W3C Trace Context** specification (https://www.w3.org/TR/trace-context/) defines a universal standard for propagating trace context across distributed systems. Before W3C Trace Context, every vendor used proprietary headers (X-B3-TraceId for Zipkin, X-Datadog-Trace-Id for DataDog), making cross-vendor tracing impossible.

**Why W3C Trace Context matters**:
- **Vendor interoperability**: A trace can start in DataDog, flow through open-source services instrumented with Jaeger, and end in New Relic
- **Universal adoption**: Supported by all major APM vendors (2025 standard)
- **Future-proof**: Standardized by W3C, not tied to any vendor's roadmap

**traceparent Header Format**:

The `traceparent` HTTP header carries trace context across service boundaries:

```
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
             │  │                                │                  │
             │  │                                │                  └─ Trace Flags (01 = sampled)
             │  │                                └──────────────────── Parent Span ID (16 hex chars, 64 bits)
             │  └───────────────────────────────────────────────────── Trace ID (32 hex chars, 128 bits)
             └────────────────────────────────────────────────────────── Version (00)
```

**Components**:
1. **Version** (`00`): Protocol version, currently always `00`
2. **Trace ID** (32 hex characters): Globally unique identifier for the entire trace (128-bit UUID)
3. **Parent Span ID** (16 hex characters): Identifier of the parent span (64-bit)
4. **Trace Flags** (2 hex characters): Bit flags for sampling and debug state
   - `01`: Trace is sampled (should be recorded)
   - `00`: Trace is not sampled (can be dropped)

**tracestate Header** (optional):

The `tracestate` header carries vendor-specific trace metadata without breaking W3C Trace Context compatibility:

```
tracestate: datadog=s:2;o:rum;p:abc123,othervendor=key:value
```

**Example in practice**:
```http
GET /api/users/123 HTTP/1.1
Host: user-service.example.com
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
tracestate: datadog=s:2;o:rum;p:abc123
```

---

## 2. OpenTelemetry Tracing

### Why OpenTelemetry?

**OpenTelemetry (OTel)** is the industry-standard observability framework (CNCF graduated project, W3C standard). It provides vendor-neutral APIs and SDKs for metrics, logs, and traces.

**Key advantages**:
- **Vendor-neutral**: Instrument once, export to any backend (Jaeger, Zipkin, DataDog, New Relic, Grafana Tempo)
- **Auto-instrumentation**: Zero-code instrumentation for popular frameworks (Express, Flask, Spring Boot, .NET)
- **W3C Trace Context**: Native support for standard context propagation
- **Language coverage**: Official SDKs for 11 languages (JavaScript, Python, Java, Go, .NET, Ruby, PHP, Rust, C++, Swift, Erlang/Elixir)
- **Future-proof**: Not tied to any vendor's roadmap or licensing changes

### Auto-Instrumentation Setup

Auto-instrumentation instruments common frameworks without code changes. It covers ~80% of tracing needs: HTTP servers, HTTP clients, database queries, message queues, caching, and more.

**Critical requirement**: OpenTelemetry **must initialize before** your application framework loads. If Express/Flask/Spring imports before OTel, instrumentation will fail.

#### Node.js Auto-Instrumentation

**Installation**:
```bash
npm install @opentelemetry/sdk-node \
            @opentelemetry/auto-instrumentations-node \
            @opentelemetry/exporter-trace-otlp-http \
            @opentelemetry/resources \
            @opentelemetry/semantic-conventions
```

**Create `tracing.js` (load FIRST before app)**:
```javascript
// tracing.js - Initialize OpenTelemetry BEFORE any other imports
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

const sdk = new NodeSDK({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'payment-service',
    [SemanticResourceAttributes.SERVICE_VERSION]: '1.2.0',
    [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: process.env.NODE_ENV || 'development'
  }),
  traceExporter: new OTLPTraceExporter({
    url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://localhost:4318/v1/traces'
  }),
  instrumentations: [
    getNodeAutoInstrumentations({
      '@opentelemetry/instrumentation-fs': { enabled: false }, // Disable noisy file system instrumentation
      '@opentelemetry/instrumentation-http': { enabled: true },
      '@opentelemetry/instrumentation-express': { enabled: true },
      '@opentelemetry/instrumentation-pg': { enabled: true }, // PostgreSQL
      '@opentelemetry/instrumentation-redis': { enabled: true }
    })
  ]
});

sdk.start();
console.log('OpenTelemetry tracing initialized');

// Graceful shutdown - flush remaining spans before exit
process.on('SIGTERM', () => {
  sdk.shutdown()
    .then(() => console.log('Tracing terminated'))
    .catch((error) => console.error('Error terminating tracing', error))
    .finally(() => process.exit(0));
});
```

**Load tracing.js FIRST in your application entry point**:
```javascript
// app.js or index.js
require('./tracing'); // MUST be first import
const express = require('express');
const app = express();
// ... rest of application code
```

**What auto-instrumentation covers**:
- HTTP server requests (Express, Fastify, Koa)
- Outgoing HTTP requests (http, https, axios, fetch)
- Database queries (PostgreSQL, MySQL, MongoDB, Redis)
- Message queues (RabbitMQ, Kafka)
- GraphQL, gRPC, DNS, file system (can be enabled/disabled)

#### Python Auto-Instrumentation

**Installation**:
```bash
pip install opentelemetry-distro \
            opentelemetry-exporter-otlp \
            opentelemetry-instrumentation-flask \
            opentelemetry-instrumentation-requests \
            opentelemetry-instrumentation-sqlalchemy
```

**Option 1: CLI auto-instrumentation (easiest)**:
```bash
opentelemetry-instrument \
  --traces_exporter otlp \
  --metrics_exporter none \
  --service_name payment-service \
  --exporter_otlp_endpoint http://localhost:4318 \
  python app.py
```

**Option 2: Programmatic auto-instrumentation** (more control):
```python
# tracing.py - Import FIRST before Flask
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure resource (service metadata)
resource = Resource.create({
    "service.name": "payment-service",
    "service.version": "1.2.0",
    "deployment.environment": os.getenv("ENVIRONMENT", "development")
})

# Configure tracer provider
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318/v1/traces")
))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

print("OpenTelemetry tracing initialized")

# Auto-instrument frameworks
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# Apply instrumentation to Flask app
from app import app  # Import app AFTER setting up OTel
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
SQLAlchemyInstrumentor().instrument()
```

**What auto-instrumentation covers**:
- Flask, Django, FastAPI web frameworks
- Outgoing HTTP requests (requests, httpx, urllib3)
- Database queries (SQLAlchemy, psycopg2, pymongo)
- Redis, Celery, gRPC

#### Java Auto-Instrumentation

**Download OpenTelemetry Java Agent**:
```bash
wget https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/latest/download/opentelemetry-javaagent.jar
```

**Run application with Java agent**:
```bash
java -javaagent:opentelemetry-javaagent.jar \
     -Dotel.service.name=payment-service \
     -Dotel.traces.exporter=otlp \
     -Dotel.exporter.otlp.endpoint=http://localhost:4318 \
     -jar your-application.jar
```

**What auto-instrumentation covers**:
- Spring Boot, Jakarta EE, Servlet containers
- JDBC database queries (PostgreSQL, MySQL, Oracle)
- HTTP clients (Apache HttpClient, OkHttp, Netty)
- Redis, Kafka, RabbitMQ, gRPC

**Recommendation**: Start with auto-instrumentation for all new projects. It provides comprehensive coverage without code changes. Add manual instrumentation only for business-specific operations.

### Manual Instrumentation for Custom Spans

Manual instrumentation captures business logic and custom operations not covered by auto-instrumentation (payment processing, order fulfillment, complex calculations).

#### Node.js Manual Spans

```javascript
const { trace, SpanStatusCode } = require('@opentelemetry/api');

const tracer = trace.getTracer('payment-service', '1.2.0');

async function processPayment(userId, amount, currency) {
  // Create span for payment processing
  return tracer.startActiveSpan('processPayment', async (span) => {
    try {
      // Add span attributes (use semantic conventions when available)
      span.setAttribute('payment.user_id', userId);
      span.setAttribute('payment.amount', amount);
      span.setAttribute('payment.currency', currency);
      span.setAttribute('payment.method', 'credit_card');

      // Nested span for payment gateway call
      const chargeResult = await tracer.startActiveSpan('stripe.createCharge', async (chargeSpan) => {
        try {
          chargeSpan.setAttribute('http.method', 'POST');
          chargeSpan.setAttribute('http.url', 'https://api.stripe.com/v1/charges');

          const result = await stripeClient.charges.create({
            amount: amount * 100, // Stripe uses cents
            currency: currency,
            customer: userId
          });

          chargeSpan.setStatus({ code: SpanStatusCode.OK });
          return result;
        } catch (error) {
          // Record exception in span
          chargeSpan.recordException(error);
          chargeSpan.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
          throw error;
        } finally {
          chargeSpan.end();
        }
      });

      // Add event to parent span (significant milestone)
      span.addEvent('payment_succeeded', {
        'charge.id': chargeResult.id,
        'charge.amount': chargeResult.amount
      });

      span.setStatus({ code: SpanStatusCode.OK });
      return chargeResult;
    } catch (error) {
      span.recordException(error);
      span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
      throw error;
    } finally {
      span.end(); // CRITICAL: Always end spans to flush data
    }
  });
}
```

#### Python Manual Spans

```python
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer("payment-service", "1.2.0")

async def process_payment(user_id: str, amount: float, currency: str):
    # Create span with context manager (auto-ends span)
    with tracer.start_as_current_span("processPayment") as span:
        try:
            # Add span attributes
            span.set_attribute("payment.user_id", user_id)
            span.set_attribute("payment.amount", amount)
            span.set_attribute("payment.currency", currency)
            span.set_attribute("payment.method", "credit_card")

            # Nested span for external API call
            with tracer.start_as_current_span("stripe.createCharge") as charge_span:
                charge_span.set_attribute("http.method", "POST")
                charge_span.set_attribute("http.url", "https://api.stripe.com/v1/charges")

                result = await stripe_client.charges.create(
                    amount=int(amount * 100),
                    currency=currency,
                    customer=user_id
                )

                charge_span.set_status(Status(StatusCode.OK))

            # Add event to parent span
            span.add_event("payment_succeeded", {
                "charge.id": result.id,
                "charge.amount": result.amount
            })

            span.set_status(Status(StatusCode.OK))
            return result
        except Exception as error:
            span.record_exception(error)
            span.set_status(Status(StatusCode.ERROR, str(error)))
            raise
```

### Span Attributes (Semantic Conventions)

OpenTelemetry defines **semantic conventions** for standard attribute names. Using semantic conventions ensures consistency across services and enables better tooling support.

**HTTP Attributes** (for HTTP requests/responses):
```javascript
span.setAttribute('http.method', 'POST');
span.setAttribute('http.url', 'https://api.example.com/users');
span.setAttribute('http.target', '/users');
span.setAttribute('http.host', 'api.example.com');
span.setAttribute('http.scheme', 'https');
span.setAttribute('http.status_code', 200);
span.setAttribute('http.user_agent', 'Mozilla/5.0...');
```

**Database Attributes** (for database queries):
```javascript
span.setAttribute('db.system', 'postgresql');
span.setAttribute('db.name', 'payments_db');
span.setAttribute('db.statement', 'SELECT * FROM users WHERE id = $1');
span.setAttribute('db.operation', 'SELECT');
span.setAttribute('db.user', 'app_user');
span.setAttribute('db.connection_string', 'postgresql://localhost:5432/payments_db');
```

**Messaging Attributes** (for message queues):
```javascript
span.setAttribute('messaging.system', 'kafka');
span.setAttribute('messaging.destination', 'order-events');
span.setAttribute('messaging.operation', 'publish');
span.setAttribute('messaging.message_id', 'msg-12345');
```

**Complete semantic conventions**: https://opentelemetry.io/docs/specs/semconv/

### Context Propagation Across Protocols

OpenTelemetry automatically propagates trace context across service boundaries using protocol-specific headers.

#### HTTP Context Propagation

When making HTTP requests, OpenTelemetry automatically injects `traceparent` and `tracestate` headers:

```javascript
// Outgoing HTTP request (auto-instrumented)
const response = await fetch('https://user-service.example.com/api/users/123', {
  method: 'GET'
  // OpenTelemetry automatically adds:
  // traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
  // tracestate: ...
});
```

**Manual HTTP context propagation** (if not using auto-instrumentation):
```javascript
const { propagation, context } = require('@opentelemetry/api');

const headers = {};
propagation.inject(context.active(), headers);
// headers now contains: { traceparent: '00-...', tracestate: '...' }

const response = await fetch('https://user-service.example.com/api/users/123', {
  method: 'GET',
  headers: headers
});
```

#### gRPC Context Propagation

gRPC uses `grpc-trace-bin` metadata (binary format) for trace context:

```javascript
// Node.js gRPC client
const grpc = require('@grpc/grpc-js');
const { GrpcInstrumentation } = require('@opentelemetry/instrumentation-grpc');

// Context automatically propagated in gRPC metadata
const client = new UserServiceClient('localhost:50051', grpc.credentials.createInsecure());
client.getUser({ userId: '123' }, (err, response) => {
  // Trace context included in gRPC metadata automatically
});
```

#### Message Queue Context Propagation

For message queues (Kafka, RabbitMQ), trace context is propagated in message headers:

```javascript
// Kafka producer (auto-instrumented)
await producer.send({
  topic: 'order-events',
  messages: [{
    key: 'order-123',
    value: JSON.stringify({ orderId: '123', amount: 99.99 }),
    // OpenTelemetry automatically adds trace context in headers
  }]
});
```

**Manual Kafka context propagation**:
```javascript
const { propagation, context } = require('@opentelemetry/api');

const headers = {};
propagation.inject(context.active(), headers);

await producer.send({
  topic: 'order-events',
  messages: [{
    key: 'order-123',
    value: JSON.stringify({ orderId: '123', amount: 99.99 }),
    headers: headers // { traceparent: '00-...', tracestate: '...' }
  }]
});
```

---

## 3. Sampling Strategies

Tracing 100% of requests is expensive (storage costs, performance overhead, overwhelming trace backends). **Sampling** reduces trace volume while maintaining observability.

### Head Sampling (Decision at Trace Start)

**Head sampling** makes the sampling decision when a trace starts (at the root span). The decision propagates to all downstream services via the `traceparent` header trace flags.

#### Probabilistic Sampling

Sample a fixed percentage of all traces randomly.

**Example: 5% sampling**:
```javascript
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { TraceIdRatioBasedSampler } = require('@opentelemetry/sdk-trace-node');

const sdk = new NodeSDK({
  sampler: new TraceIdRatioBasedSampler(0.05), // Sample 5% of traces
  // ... other configuration
});
```

**Pros**:
- Simple, predictable storage costs
- No buffering required
- Consistent sampling across all services

**Cons**:
- May miss important traces (errors, slow requests)
- Debugging rare issues becomes difficult

**When to use**: High-volume services (>10,000 requests/second) where storage costs are primary concern.

#### Rate Limiting Sampling

Sample the first N traces per second, drop the rest.

**Example: Max 100 traces/second**:
```javascript
const { ParentBasedSampler, TraceIdRatioBasedSampler } = require('@opentelemetry/sdk-trace-node');

class RateLimitingSampler {
  constructor(maxTracesPerSecond) {
    this.maxTracesPerSecond = maxTracesPerSecond;
    this.tracesThisSecond = 0;
    this.currentSecond = Math.floor(Date.now() / 1000);
  }

  shouldSample(context, traceId, name, spanKind, attributes, links) {
    const now = Math.floor(Date.now() / 1000);
    if (now !== this.currentSecond) {
      this.currentSecond = now;
      this.tracesThisSecond = 0;
    }

    if (this.tracesThisSecond < this.maxTracesPerSecond) {
      this.tracesThisSecond++;
      return { decision: 'RECORD_AND_SAMPLED' };
    }
    return { decision: 'NOT_RECORD' };
  }
}
```

**Pros**:
- Protects trace backend from overload
- Guarantees maximum trace volume

**Cons**:
- Biased sampling (only fast requests if service is slow)
- Complex to implement correctly

**When to use**: Protecting trace backend capacity during traffic spikes.

### Tail Sampling (Decision After Trace Completion)

**Tail sampling** buffers all spans until a trace completes, then decides whether to keep or drop the entire trace based on trace properties (errors, latency, attributes).

#### Error-Based Tail Sampling

Always keep traces with errors, sample others probabilistically.

**Example: Keep all errors + 1% of successful traces**:
```yaml
# OpenTelemetry Collector configuration
processors:
  tail_sampling:
    decision_wait: 10s  # Wait up to 10s for trace to complete
    num_traces: 100000  # Buffer capacity (adjust based on traffic)
    policies:
      # Policy 1: Always sample errors
      - name: error-policy
        type: status_code
        status_code:
          status_codes: [ERROR]
      # Policy 2: Probabilistic sampling for non-errors
      - name: probabilistic-policy
        type: probabilistic
        probabilistic:
          sampling_percentage: 1  # 1% of remaining traces
```

**Pros**:
- Never miss errors or failures
- Maintains representative sample of successful requests

**Cons**:
- Requires buffering (memory overhead)
- 10s delay before trace is exported

**When to use**: Production systems where debugging errors is critical.

#### Latency-Based Tail Sampling

Keep slow traces (SLA violations) for performance investigation.

**Example: Keep traces >2s + 1% of fast traces**:
```yaml
processors:
  tail_sampling:
    decision_wait: 10s
    policies:
      # Policy 1: Always sample slow traces
      - name: latency-policy
        type: latency
        latency:
          threshold_ms: 2000  # Keep traces slower than 2s
      # Policy 2: Probabilistic sampling for fast traces
      - name: probabilistic-policy
        type: probabilistic
        probabilistic:
          sampling_percentage: 1
```

**When to use**: Identifying performance bottlenecks and SLA violations.

#### Hybrid Tail Sampling

Combine multiple policies for comprehensive coverage.

**Example: Errors + Slow traces + Specific endpoints + Probabilistic**:
```yaml
processors:
  tail_sampling:
    decision_wait: 10s
    num_traces: 100000
    policies:
      # Always sample errors
      - name: error-policy
        type: status_code
        status_code:
          status_codes: [ERROR]
      # Always sample slow traces
      - name: latency-policy
        type: latency
        latency:
          threshold_ms: 2000
      # Always sample critical endpoints
      - name: critical-endpoints
        type: string_attribute
        string_attribute:
          key: http.route
          values: ["/api/payments", "/api/auth/login"]
      # 1% sample of everything else
      - name: probabilistic-policy
        type: probabilistic
        probabilistic:
          sampling_percentage: 1
```

**Recommendation**: Use hybrid tail sampling for production systems. Always capture errors, slow traces, and critical endpoints, with probabilistic sampling for baseline visibility.

### Trade-offs: Cost vs Completeness

| Sampling Strategy | Storage Cost | Completeness | Use Case |
|-------------------|--------------|--------------|----------|
| **100% sampling** | Very High ($$$) | 100% | Development, low-traffic staging |
| **Probabilistic 10%** | Medium ($$) | 10% | Moderate traffic, budget-conscious |
| **Probabilistic 1%** | Low ($) | 1% | High traffic (>100k req/s) |
| **Tail sampling (errors + 1%)** | Medium ($$) | 100% errors, 1% success | Production (recommended) |
| **Tail sampling (errors + slow + 1%)** | Medium ($$) | 100% issues, 1% baseline | Production with SLA monitoring |

**Cost calculation example** (Grafana Tempo pricing):
- Traffic: 1,000 requests/second = 86.4 million requests/day
- Average trace size: 10 KB
- 100% sampling: 864 GB/day × $0.50/GB = **$432/day** ($12,960/month)
- 1% sampling: 8.64 GB/day × $0.50/GB = **$4.32/day** ($130/month)
- Tail sampling (5% effective rate): 43.2 GB/day × $0.50/GB = **$21.60/day** ($648/month)

**Recommendation**: Start with 1-5% probabilistic sampling. Move to tail sampling once you implement an OpenTelemetry Collector.

---

## 4. Trace Backends

### Jaeger (Open-Source, Kubernetes-Native)

**Use case**: Self-hosted, Kubernetes-native tracing, cost-conscious teams

**Strengths**:
- **Free and open-source**: No licensing costs
- **Proven at scale**: Originally developed at Uber for massive trace volumes
- **Native OpenTelemetry support**: W3C Trace Context, OTLP ingestion
- **Service dependency graphs**: Automatic visualization of service relationships
- **Kubernetes-native**: Helm charts, Kubernetes operator, sidecar injection

**Weaknesses**:
- **Basic UI**: Functional but less polished than commercial APM tools
- **Limited analysis features**: No anomaly detection, correlation with metrics/logs requires external tools
- **Self-managed**: Requires operational expertise (storage backend, scaling, monitoring)

**Storage backends**:
- **Cassandra**: Production-grade, horizontally scalable, high availability
- **Elasticsearch**: Rich querying, familiar for ELK stack users
- **Badger**: Embedded database, single-node deployment only

**Setup (Docker Compose for development)**:
```yaml
version: '3'
services:
  jaeger:
    image: jaegertracing/all-in-one:1.52
    ports:
      - "16686:16686"  # UI
      - "4317:4317"    # OTLP gRPC
      - "4318:4318"    # OTLP HTTP
    environment:
      - COLLECTOR_OTLP_ENABLED=true
```

**When to choose**: Budget-constrained, Kubernetes environment, strong DevOps team, no need for unified observability platform.

### Zipkin (Legacy, Stable)

**Use case**: Legacy systems, Twitter-lineage projects, simple tracing needs

**Strengths**:
- **Mature and stable**: Over 10 years of development
- **Simple deployment**: Single JAR file, minimal configuration
- **Wide language support**: Libraries for most languages (pre-OpenTelemetry)

**Weaknesses**:
- **Less active development**: Jaeger and Tempo have overtaken Zipkin in adoption
- **Basic features**: No advanced analysis, simple UI
- **Legacy instrumentation**: Most new projects use OpenTelemetry instead of Zipkin libraries

**Storage backends**:
- **MySQL**: Simple, familiar
- **Cassandra**: Scalable
- **Elasticsearch**: Rich querying

**Setup**:
```bash
curl -sSL https://zipkin.io/quickstart.sh | bash -s
java -jar zipkin.jar
```

**When to choose**: Maintaining legacy Zipkin deployments, extremely simple tracing needs, prefer stable over cutting-edge.

### Grafana Tempo (Cost-Effective, Grafana Ecosystem)

**Use case**: Grafana users, cost-effective at scale, Kubernetes

**Strengths**:
- **10x cheaper storage**: Stores traces in object storage (S3, GCS, Azure Blob) with no indexing overhead
- **TraceQL**: Powerful query language inspired by PromQL and LogQL
- **Grafana integration**: Unified dashboards with metrics (Prometheus) and logs (Loki)
- **Scalable**: Horizontally scalable, proven at massive scale

**Weaknesses**:
- **Requires Grafana ecosystem**: Best value when using Grafana, Prometheus, Loki together
- **Query performance**: Trade-off for cost savings - queries slower than Jaeger/Elasticsearch

**Concrete cost comparison**:

**Grafana Cloud Tempo** (managed):
- Trace ingestion: **~$0.50/GB** traces ingested
- No additional storage costs (included in ingestion price)
- Example: 100 GB/month = $50/month

**Self-hosted Tempo with S3**:
- S3 Standard storage: **~$0.023/GB/month**
- Transfer costs: ~$0.09/GB egress (queries)
- Example: 1 TB stored = $23/month storage + query costs

**Jaeger with Elasticsearch** (for comparison):
- Elasticsearch storage: **~$0.10-0.20/GB/month** (EC2 + EBS costs)
- Compute overhead: Additional $100-500/month for ES cluster
- Example: 1 TB stored = $100-200/month storage + $200/month compute

**Result**: Tempo is ~4-10x cheaper than Jaeger with Elasticsearch at scale

**Setup (Docker Compose)**:
```yaml
version: '3'
services:
  tempo:
    image: grafana/tempo:2.3.0
    command: ["-config.file=/etc/tempo.yaml"]
    volumes:
      - ./tempo-config.yaml:/etc/tempo.yaml
      - tempo-data:/var/tempo
    ports:
      - "3200:3200"   # Tempo UI
      - "4317:4317"   # OTLP gRPC
      - "4318:4318"   # OTLP HTTP

  grafana:
    image: grafana/grafana:10.2.0
    ports:
      - "3000:3000"
    environment:
      - GF_AUTH_ANONYMOUS_ENABLED=true
      - GF_AUTH_ANONYMOUS_ORG_ROLE=Admin
    volumes:
      - grafana-data:/var/lib/grafana

volumes:
  tempo-data:
  grafana-data:
```

**tempo-config.yaml**:
```yaml
server:
  http_listen_port: 3200

distributor:
  receivers:
    otlp:
      protocols:
        grpc:
        http:

storage:
  trace:
    backend: local
    local:
      path: /var/tempo/traces
```

**When to choose**: Using Grafana for visualization, high trace volume, cost-conscious, Kubernetes environment.

### DataDog APM (Commercial, Unified Platform)

**Use case**: Already using DataDog, want unified observability platform

**Strengths**:
- **Unified platform**: Traces, metrics, logs, RUM in single dashboard
- **Automatic correlation**: Click from metric spike → related traces → correlated logs
- **APM features**: Profiling, deployment tracking, service maps, AI-powered insights
- **Managed service**: No operational overhead

**Weaknesses**:
- **Expensive**: $31-40/host/month + per-span costs
- **Vendor lock-in**: Difficult to migrate away from DataDog
- **Pricing complexity**: Multiple pricing dimensions (hosts, spans, retention)

**Pricing**:
- APM: $31/host/month (Infrastructure Monitoring included)
- Enterprise: $40/host/month
- Indexed spans: $1.70/million spans retained for search
- Ingested spans: $0.10/GB ingested (sampled before indexing)

**Setup (OpenTelemetry → DataDog)**:
```javascript
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');

const exporter = new OTLPTraceExporter({
  url: 'https://trace.agent.datadoghq.com/v1/traces',
  headers: {
    'DD-API-KEY': process.env.DD_API_KEY
  }
});
```

**When to choose**: Already using DataDog for infrastructure monitoring, want unified observability, budget for commercial APM.

### New Relic (Commercial, All-in-One Pricing)

**Use case**: Predictable pricing, AI-powered insights, simplicity

**Strengths**:
- **All-in-one pricing**: Per-user + per-GB, all features included (no hidden costs)
- **AI insights**: Leading anomaly detection, intelligent root cause analysis
- **NRQL**: Powerful query language for custom analysis
- **Distributed tracing**: Automatic trace correlation with logs, metrics, errors

**Pricing**:
- Standard: 1 user + 100 GB/month free
- Pro: $99/user/month + $0.35/GB ingested (200+ features)
- Enterprise: $549/user/month + $0.50/GB ingested (advanced features, support)

**Setup (OpenTelemetry → New Relic)**:
```javascript
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');

const exporter = new OTLPTraceExporter({
  url: 'https://otlp.nr-data.net/v1/traces',
  headers: {
    'api-key': process.env.NEW_RELIC_LICENSE_KEY
  }
});
```

**When to choose**: Want predictable pricing, smaller teams (<50 people), AI-powered insights, simplicity over deep customization.

### Comparison Table

| Feature | Jaeger | Zipkin | Grafana Tempo | DataDog APM | New Relic |
|---------|--------|--------|---------------|-------------|-----------|
| **Cost (self-hosted)** | Free + infra | Free + infra | Free + infra | N/A | N/A |
| **Cost (managed)** | N/A | N/A | $0.50/GB ingested | $31-40/host + spans | $99/user + $0.35/GB |
| **Storage cost (self-hosted)** | $0.10-0.20/GB + compute | $0.10-0.20/GB + compute | **$0.023/GB (S3)** | N/A | N/A |
| **Cost efficiency** | Medium ($$) | Medium ($$) | **High ($)** | Low ($$$) | Medium ($$) |
| **OpenTelemetry support** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Analysis features** | ⭐⭐⭐ (basic) | ⭐⭐ (basic) | ⭐⭐⭐⭐ (TraceQL) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Unified observability** | ⭐⭐ | ⭐ | ⭐⭐⭐⭐ (with Grafana) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Operational complexity** | ⭐⭐⭐ (moderate) | ⭐⭐⭐ (moderate) | ⭐⭐⭐ (moderate) | ⭐⭐⭐⭐⭐ (managed) | ⭐⭐⭐⭐⭐ (managed) |
| **Kubernetes-native** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 5. Debugging with Traces (Practical Troubleshooting Workflow)

### Scenario: API Latency Investigation

**Problem**: Payment API `/api/payments` p95 latency increased from 200ms to 2,000ms.

**Step 1: Identify latency spike in metrics dashboard**
- Grafana/DataDog/New Relic shows p95 latency spike in `/api/payments` endpoint
- Timeframe: Started 2 hours ago, ongoing
- Hypothesis: Unknown, need traces to investigate

**Step 2: Filter traces for slow requests**
- Jaeger: Filter by service `payment-service`, operation `POST /api/payments`, duration >1s
- Grafana Tempo (TraceQL):
  ```
  { service.name="payment-service" && name="POST /api/payments" && duration > 1s }
  ```
- DataDog: Filter by `service:payment-service`, `resource_name:"POST /api/payments"`, latency >1s

**Step 3: Analyze trace waterfall**

Example trace (2.2s total):
```
payment-service: POST /api/payments (2.2s)
  ├─ user-service: GET /api/users/123 (50ms)
  │   └─ postgresql: SELECT * FROM users WHERE id = $1 (30ms)
  ├─ payment-service: validatePayment (10ms)
  └─ stripe-api: POST /v1/charges (2.1s) ← BOTTLENECK
      └─ http.post (2.1s)
```

**Root cause identified**: Stripe API calls taking 2.1s (previously ~100ms).

**Step 4: Read logs for trace ID**

Extract trace ID from slow trace: `4bf92f3577b34da6a3ce929d0e0e4736`

Query logs by trace ID:
```
traceId:"4bf92f3577b34da6a3ce929d0e0e4736"
```

**Logs reveal**:
```json
{
  "timestamp": "2025-12-07T14:23:15.456Z",
  "level": "ERROR",
  "message": "Stripe API timeout after 2000ms",
  "service": "payment-service",
  "traceId": "4bf92f3577b34da6a3ce929d0e0e4736",
  "error": "StripeConnectionError: Connection timeout",
  "stripe.url": "https://api.stripe.com/v1/charges"
}
```

**Step 5: Root cause and remediation**

- **Root cause**: Stripe API experiencing degraded performance (timeout errors)
- **Immediate action**: Check Stripe status page (https://status.stripe.com) - confirms degraded performance
- **Short-term**: Increase timeout from 2s to 5s, add retry logic with exponential backoff
- **Long-term**: Implement circuit breaker pattern to fail fast when Stripe is degraded

### Correlation: Logs + Metrics + Traces

**Unified debugging workflow**:

1. **Metric alert**: "API latency p95 >1s" (from metrics dashboard)
2. **Find slow trace**: Filter traces by endpoint and latency (tracing backend)
3. **Identify bottleneck span**: Analyze trace waterfall (Stripe API taking 2.1s)
4. **Read correlated logs**: Filter logs by trace ID (log aggregation)
5. **Root cause**: Logs reveal "Stripe API timeout" error
6. **Verify**: Check Stripe status page, confirm degraded performance
7. **Fix**: Implement retry logic + circuit breaker, increase timeout

**Key enablers**:
- **Trace ID in logs**: Every log entry includes OpenTelemetry trace ID
- **Same service name**: Metrics, logs, and traces use identical `service.name` attribute
- **Time correlation**: Logs, metrics, and traces aligned by timestamp

**Example: Logging trace context**:
```javascript
const { trace } = require('@opentelemetry/api');
const logger = require('pino')();

app.use((req, res, next) => {
  const span = trace.getActiveSpan();
  const traceId = span?.spanContext().traceId;
  const spanId = span?.spanContext().spanId;

  req.logger = logger.child({
    traceId,
    spanId,
    correlationId: req.headers['x-correlation-id']
  });

  next();
});

// All logs now include trace context
req.logger.info('Payment processed successfully');
// Output: {"level":"INFO","message":"Payment processed successfully","traceId":"4bf92f35...","spanId":"00f067aa..."}
```

---

## Summary

**Distributed tracing** is essential for understanding request flow in microservices. **OpenTelemetry** is the industry-standard framework, providing vendor-neutral instrumentation with **W3C Trace Context** propagation.

**Key recommendations**:
1. **Start with auto-instrumentation**: Covers 80% of tracing needs without code changes
2. **Use W3C Trace Context**: Ensures interoperability across vendors
3. **Implement tail sampling**: Always capture errors and slow traces, sample 1-5% of successful requests
4. **Choose trace backend based on needs**:
   - Budget-constrained, Kubernetes → **Grafana Tempo**
   - Existing DataDog/New Relic → Use their APM
   - Self-hosted, simple → **Jaeger**
5. **Correlate logs with traces**: Include OpenTelemetry trace ID in every log entry
6. **Monitor trace backend costs**: Sampling is critical for cost control at scale

**See also**:
- `logging-patterns.md` for correlating logs with trace IDs
- `metrics-collection.md` for correlating metrics with traces
- pact-backend-patterns skill for distributed tracing integration in backend services
- pact-api-design skill for API-level tracing patterns
