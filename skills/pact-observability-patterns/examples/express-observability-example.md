# Express.js Observability Example

Complete working example demonstrating observability integration in a production-ready Express.js service. This example shows OpenTelemetry auto-instrumentation, structured logging with Pino, custom metrics using the RED method, distributed tracing, and a local observability stack using Docker Compose.

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Project Setup](#project-setup)
4. [OpenTelemetry Integration](#opentelemetry-integration)
5. [Structured Logging](#structured-logging)
6. [Metrics Collection](#metrics-collection)
7. [Complete Service Implementation](#complete-service-implementation)
8. [Local Observability Stack](#local-observability-stack)
9. [Running the Example](#running-the-example)
10. [Debugging Scenario](#debugging-scenario)

## Overview

This example demonstrates a complete Express.js payment processing service with production-grade observability:

- **Service**: Payment processing API that validates payments and processes transactions
- **OpenTelemetry**: Auto-instrumentation for HTTP and manual spans for business logic
- **Logging**: Structured JSON logging with Pino, including correlation IDs and trace context
- **Metrics**: RED method metrics (Rate, Errors, Duration) using Prometheus
- **Tracing**: Distributed tracing with OpenTelemetry exported to Jaeger
- **Local Stack**: Docker Compose setup with Jaeger, Prometheus, and Grafana

**Key Features**:
- Environment-based configuration (development vs production)
- Automatic correlation between logs, metrics, and traces
- Custom business metrics (payments processed, revenue tracked)
- Graceful shutdown handling for telemetry flushing
- Complete debugging workflow demonstration

## System Architecture

```
Client
  ↓
Express.js Payment Service (localhost:3000)
  ├─ OpenTelemetry SDK
  │   ├─ Auto-instrumentation (HTTP requests)
  │   └─ Manual spans (business logic)
  ├─ Pino Logger (structured JSON)
  └─ Prometheus Metrics (RED method)
       ↓
OpenTelemetry Collector (localhost:4318)
  ├─ Receives: OTLP traces via HTTP
  ├─ Processes: Batching, filtering
  └─ Exports to:
      ├─ Jaeger (traces: localhost:16686)
      └─ Prometheus (scrapes service /metrics: localhost:9090)
           └─ Grafana (visualization: localhost:3001)
```

**Data Flow**:
1. Client sends HTTP request to payment service
2. OpenTelemetry auto-instrumentation creates HTTP span
3. Service logs request with trace context (traceId, spanId, correlationId)
4. Service records metrics (request count, latency histogram)
5. Service creates manual span for payment processing logic
6. OpenTelemetry exports trace to Collector via OTLP
7. Collector forwards trace to Jaeger
8. Prometheus scrapes metrics from service /metrics endpoint
9. Grafana queries Prometheus and Jaeger for unified visualization

## Project Setup

### Directory Structure

```
payment-service/
├── src/
│   ├── tracing.js              # OpenTelemetry initialization (load FIRST)
│   ├── logger.js               # Pino structured logger configuration
│   ├── metrics.js              # Prometheus metrics setup
│   ├── middleware/
│   │   └── correlation.js      # Correlation ID middleware
│   ├── services/
│   │   └── paymentService.js   # Payment processing business logic
│   └── app.js                  # Express application
├── docker-compose.yml          # Local observability stack
├── prometheus.yml              # Prometheus scrape configuration
├── package.json                # Dependencies
└── .env.example                # Environment variables template
```

### Dependencies

```json
{
  "name": "payment-service",
  "version": "1.0.0",
  "description": "Payment processing service with OpenTelemetry observability",
  "main": "src/app.js",
  "scripts": {
    "start": "node -r ./src/tracing.js src/app.js",
    "dev": "NODE_ENV=development node -r ./src/tracing.js src/app.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "pino": "^8.16.2",
    "pino-http": "^8.5.1",
    "prom-client": "^15.1.0",
    "@opentelemetry/sdk-node": "^0.45.1",
    "@opentelemetry/auto-instrumentations-node": "^0.40.3",
    "@opentelemetry/exporter-trace-otlp-http": "^0.45.1",
    "@opentelemetry/resources": "^1.18.1",
    "@opentelemetry/semantic-conventions": "^1.18.1",
    "@opentelemetry/api": "^1.7.0"
  }
}
```

### Environment Variables

Create `.env` file:

```bash
# Service configuration
SERVICE_NAME=payment-service
SERVICE_VERSION=1.0.0
PORT=3000
NODE_ENV=production

# OpenTelemetry configuration
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
OTEL_TRACES_SAMPLER=traceidratio
OTEL_TRACES_SAMPLER_ARG=0.1  # 10% sampling

# Logging configuration
LOG_LEVEL=info
```

## OpenTelemetry Integration

**File**: `src/tracing.js`

**CRITICAL**: This file must be loaded BEFORE any other application code. OpenTelemetry instruments framework modules during import, so late initialization misses instrumentation.

```javascript
// src/tracing.js
// Location: OpenTelemetry initialization (must be loaded FIRST via -r flag or require('./tracing') at top of app.js)
// Used by: app.js (loaded via node -r flag), all instrumented frameworks (Express, HTTP)
// Dependencies: @opentelemetry/sdk-node, @opentelemetry/auto-instrumentations-node

const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

// Configure service resource (identifies service in APM tools)
const resource = new Resource({
  [SemanticResourceAttributes.SERVICE_NAME]: process.env.SERVICE_NAME || 'payment-service',
  [SemanticResourceAttributes.SERVICE_VERSION]: process.env.SERVICE_VERSION || '1.0.0',
  [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: process.env.NODE_ENV || 'development'
});

// Configure trace exporter (OTLP HTTP to Collector)
const traceExporter = new OTLPTraceExporter({
  url: `${process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://localhost:4318'}/v1/traces`,
  headers: {} // Add authentication headers for production
});

// Initialize OpenTelemetry SDK
const sdk = new NodeSDK({
  resource,
  traceExporter,
  // Auto-instrumentation for Express, HTTP, DNS, etc.
  instrumentations: [
    getNodeAutoInstrumentations({
      // Disable instrumentations that are too verbose or not needed
      '@opentelemetry/instrumentation-fs': {
        enabled: false // File system operations create too many spans
      }
    })
  ]
});

// Start SDK (must be called before application imports)
sdk.start();
console.log('OpenTelemetry SDK initialized');

// Graceful shutdown: Flush pending telemetry before exit
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, shutting down OpenTelemetry SDK...');
  try {
    await sdk.shutdown();
    console.log('OpenTelemetry SDK shutdown complete');
    process.exit(0);
  } catch (error) {
    console.error('Error shutting down OpenTelemetry SDK', error);
    process.exit(1);
  }
});

// Handle unhandled rejections
process.on('unhandledRejection', async (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  await sdk.shutdown();
  process.exit(1);
});
```

**Key Implementation Details**:
- **Resource configuration**: Identifies service with semantic attributes (service.name, service.version, deployment.environment)
- **OTLP exporter**: Exports traces to OpenTelemetry Collector via HTTP (port 4318 default)
- **Auto-instrumentation**: Automatically instruments Express, HTTP, DNS, and other Node.js modules
- **Graceful shutdown**: Flushes pending spans on SIGTERM to avoid losing telemetry data
- **Sampling**: Configured via environment variables (OTEL_TRACES_SAMPLER, OTEL_TRACES_SAMPLER_ARG)

## Structured Logging

**File**: `src/logger.js`

```javascript
// src/logger.js
// Location: Pino logger configuration with trace context integration
// Used by: app.js (imported), correlation.js middleware, paymentService.js
// Dependencies: pino, @opentelemetry/api

const pino = require('pino');
const { trace } = require('@opentelemetry/api');

// Configure Pino logger with structured JSON output
const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  // Format log level as uppercase string (ERROR, INFO, etc.)
  formatters: {
    level: (label) => ({ level: label.toUpperCase() })
  },
  // Base fields included in every log entry
  base: {
    service: process.env.SERVICE_NAME || 'payment-service',
    environment: process.env.NODE_ENV || 'development'
  },
  // ISO 8601 timestamp format
  timestamp: () => `,"timestamp":"${new Date().toISOString()}"`,
  // Pretty print in development for readability
  transport: process.env.NODE_ENV === 'development' ? {
    target: 'pino-pretty',
    options: {
      colorize: true,
      translateTime: 'SYS:standard',
      ignore: 'pid,hostname'
    }
  } : undefined
});

// Create child logger with OpenTelemetry trace context
// Use this function to create loggers that automatically include traceId and spanId
function createLogger(additionalContext = {}) {
  const span = trace.getActiveSpan();
  const spanContext = span?.spanContext();

  // Extract trace context from OpenTelemetry
  const traceContext = spanContext ? {
    traceId: spanContext.traceId,
    spanId: spanContext.spanId,
    traceFlags: spanContext.traceFlags
  } : {};

  // Merge trace context with additional context
  return logger.child({
    ...traceContext,
    ...additionalContext
  });
}

module.exports = { logger, createLogger };
```

**File**: `src/middleware/correlation.js`

```javascript
// src/middleware/correlation.js
// Location: Express middleware for correlation ID generation and trace context injection
// Used by: app.js (registered as middleware)
// Dependencies: logger.js, @opentelemetry/api

const { createLogger } = require('../logger');
const { trace } = require('@opentelemetry/api');
const crypto = require('crypto');

// Generate short correlation ID (12 characters, URL-safe)
function generateCorrelationId() {
  return `req_${crypto.randomBytes(6).toString('base64url')}`;
}

// Express middleware: Inject correlation ID and trace context into request
function correlationMiddleware(req, res, next) {
  // Extract correlation ID from header or generate new one
  const correlationId = req.headers['x-correlation-id'] || generateCorrelationId();

  // Store correlation ID on request object
  req.correlationId = correlationId;

  // Return correlation ID in response header (for client-side debugging)
  res.setHeader('X-Correlation-ID', correlationId);

  // Extract OpenTelemetry trace context
  const span = trace.getActiveSpan();
  const spanContext = span?.spanContext();

  // Create request-scoped logger with correlation ID and trace context
  req.logger = createLogger({
    correlationId,
    // Add request metadata for context
    method: req.method,
    path: req.path,
    userAgent: req.headers['user-agent']
  });

  // Log incoming request
  req.logger.info('Incoming request', {
    method: req.method,
    path: req.path,
    query: req.query
  });

  next();
}

module.exports = { correlationMiddleware };
```

**Log Output Example** (production JSON format):

```json
{
  "level": "INFO",
  "timestamp": "2025-12-07T10:30:00.123Z",
  "service": "payment-service",
  "environment": "production",
  "traceId": "4bf92f3577b34da6a3ce929d0e0e4736",
  "spanId": "00f067aa0ba902b7",
  "correlationId": "req_7f8a9b2c",
  "method": "POST",
  "path": "/api/payments",
  "msg": "Incoming request",
  "query": {}
}
```

## Metrics Collection

**File**: `src/metrics.js`

```javascript
// src/metrics.js
// Location: Prometheus metrics setup using RED method (Rate, Errors, Duration)
// Used by: app.js (imported and exposed via /metrics endpoint)
// Dependencies: prom-client

const promClient = require('prom-client');

// Enable default metrics (CPU, memory, event loop, GC)
promClient.collectDefaultMetrics({
  timeout: 5000,
  prefix: 'payment_service_'
});

// Create registry (default registry used automatically)
const register = promClient.register;

// RED Metrics: Rate, Errors, Duration

// 1. RATE: HTTP request counter
const httpRequestsTotal = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code']
});

// 2. DURATION: HTTP request duration histogram
const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request duration in seconds',
  labelNames: ['method', 'route', 'status_code'],
  // Buckets optimized for API latency (10ms to 10s)
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10]
});

// Business Metrics: Domain-specific measurements

// Payments processed counter
const paymentsTotal = new promClient.Counter({
  name: 'payments_total',
  help: 'Total number of payments processed',
  labelNames: ['status', 'payment_method'] // success, failed, pending
});

// Revenue tracking (gauge for current revenue, could use counter for total)
const paymentAmountTotal = new promClient.Counter({
  name: 'payment_amount_usd_total',
  help: 'Total payment amount in USD',
  labelNames: ['status', 'payment_method']
});

// Active payment processing (gauge for concurrent payments)
const activePayments = new promClient.Gauge({
  name: 'active_payments',
  help: 'Number of payments currently being processed'
});

// Express middleware: Instrument HTTP requests with metrics
function metricsMiddleware(req, res, next) {
  const start = Date.now();

  // Track active requests
  activePayments.inc();

  // Capture response finish event
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000; // Convert to seconds
    const route = req.route?.path || req.path || 'unknown';
    const statusCode = res.statusCode.toString();

    // Record metrics
    httpRequestsTotal.inc({
      method: req.method,
      route,
      status_code: statusCode
    });

    httpRequestDuration.observe({
      method: req.method,
      route,
      status_code: statusCode
    }, duration);

    activePayments.dec();
  });

  next();
}

// Expose metrics for Prometheus scraping
async function getMetrics() {
  return register.metrics();
}

module.exports = {
  metricsMiddleware,
  getMetrics,
  metrics: {
    paymentsTotal,
    paymentAmountTotal,
    activePayments
  }
};
```

**Key Implementation Details**:
- **RED method**: Request rate (counter), error rate (derived from status_code label), duration (histogram)
- **Histogram buckets**: Optimized for API latency (10ms to 10s range)
- **Business metrics**: Track payments processed, revenue, active payments
- **Low-cardinality labels**: method, route, status_code (avoid userId, requestId)
- **Default metrics**: CPU, memory, event loop lag automatically collected

## Complete Service Implementation

**File**: `src/services/paymentService.js`

```javascript
// src/services/paymentService.js
// Location: Payment processing business logic with manual OpenTelemetry spans
// Used by: app.js (payment route handler)
// Dependencies: @opentelemetry/api, metrics.js

const { trace } = require('@opentelemetry/api');
const { metrics } = require('../metrics');

// Get tracer for creating manual spans
const tracer = trace.getTracer('payment-service');

// Simulate payment validation (in real service, would call external API)
async function validatePayment(paymentDetails) {
  // Create manual span for validation logic
  return tracer.startActiveSpan('validatePayment', async (span) => {
    try {
      span.setAttribute('payment.amount', paymentDetails.amount);
      span.setAttribute('payment.currency', paymentDetails.currency);
      span.setAttribute('payment.method', paymentDetails.paymentMethod);

      // Simulate validation delay
      await new Promise(resolve => setTimeout(resolve, 50));

      // Validation logic
      if (paymentDetails.amount <= 0) {
        throw new Error('Invalid payment amount');
      }

      if (!['credit_card', 'debit_card', 'paypal'].includes(paymentDetails.paymentMethod)) {
        throw new Error('Invalid payment method');
      }

      span.setStatus({ code: 1 }); // OK
      return { valid: true };
    } catch (error) {
      span.recordException(error);
      span.setStatus({ code: 2, message: error.message }); // ERROR
      throw error;
    } finally {
      span.end();
    }
  });
}

// Simulate payment processing (in real service, would call Stripe/PayPal API)
async function processPayment(paymentDetails) {
  return tracer.startActiveSpan('processPayment', async (span) => {
    try {
      span.setAttribute('payment.amount', paymentDetails.amount);
      span.setAttribute('payment.currency', paymentDetails.currency);
      span.setAttribute('payment.method', paymentDetails.paymentMethod);

      // Increment active payments gauge
      metrics.activePayments.inc();

      // Simulate external API call delay (Stripe, PayPal, etc.)
      await new Promise(resolve => setTimeout(resolve, Math.random() * 200 + 100));

      // Simulate 5% failure rate
      if (Math.random() < 0.05) {
        throw new Error('Payment gateway timeout');
      }

      // Record successful payment metrics
      metrics.paymentsTotal.inc({
        status: 'success',
        payment_method: paymentDetails.paymentMethod
      });

      metrics.paymentAmountTotal.inc({
        status: 'success',
        payment_method: paymentDetails.paymentMethod
      }, paymentDetails.amount);

      span.setStatus({ code: 1 }); // OK

      return {
        transactionId: `txn_${Date.now()}_${Math.random().toString(36).substring(7)}`,
        status: 'success',
        amount: paymentDetails.amount,
        currency: paymentDetails.currency
      };
    } catch (error) {
      // Record failed payment metrics
      metrics.paymentsTotal.inc({
        status: 'failed',
        payment_method: paymentDetails.paymentMethod
      });

      span.recordException(error);
      span.setStatus({ code: 2, message: error.message }); // ERROR
      throw error;
    } finally {
      metrics.activePayments.dec();
      span.end();
    }
  });
}

module.exports = { validatePayment, processPayment };
```

**File**: `src/app.js`

```javascript
// src/app.js
// Location: Express application with observability instrumentation
// Used by: Entry point (node -r ./src/tracing.js src/app.js)
// Dependencies: express, logger.js, metrics.js, correlation.js, paymentService.js

const express = require('express');
const { logger } = require('./logger');
const { metricsMiddleware, getMetrics } = require('./metrics');
const { correlationMiddleware } = require('./middleware/correlation');
const { validatePayment, processPayment } = require('./services/paymentService');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(correlationMiddleware); // Inject correlation ID and trace context
app.use(metricsMiddleware); // Record HTTP metrics

// Health check endpoint (exclude from detailed logging)
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// Metrics endpoint for Prometheus scraping
app.get('/metrics', async (req, res) => {
  try {
    res.set('Content-Type', 'text/plain');
    res.end(await getMetrics());
  } catch (error) {
    res.status(500).end(error.message);
  }
});

// Payment processing endpoint
app.post('/api/payments', async (req, res) => {
  const { amount, currency, paymentMethod, customerId } = req.body;

  // Log request with trace context
  req.logger.info('Processing payment', {
    amount,
    currency,
    paymentMethod,
    customerId
  });

  try {
    // Validate payment
    await validatePayment({ amount, currency, paymentMethod });

    req.logger.info('Payment validated successfully');

    // Process payment
    const result = await processPayment({ amount, currency, paymentMethod });

    req.logger.info('Payment processed successfully', {
      transactionId: result.transactionId,
      amount: result.amount
    });

    res.status(200).json({
      success: true,
      transactionId: result.transactionId,
      status: result.status,
      amount: result.amount,
      currency: result.currency
    });
  } catch (error) {
    req.logger.error('Payment processing failed', {
      error: error.message,
      amount,
      currency,
      paymentMethod
    });

    res.status(400).json({
      success: false,
      error: error.message
    });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  req.logger.error('Unhandled error', {
    error: err.message,
    stack: err.stack
  });

  res.status(500).json({
    success: false,
    error: 'Internal server error'
  });
});

// Start server
app.listen(PORT, () => {
  logger.info(`Payment service started on port ${PORT}`, {
    port: PORT,
    environment: process.env.NODE_ENV
  });
});
```

## Local Observability Stack

**File**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  # OpenTelemetry Collector: Receives traces from application, exports to Jaeger
  otel-collector:
    image: otel/opentelemetry-collector-contrib:0.91.0
    command: ["--config=/etc/otel-collector-config.yaml"]
    volumes:
      - ./otel-collector-config.yaml:/etc/otel-collector-config.yaml
    ports:
      - "4318:4318"   # OTLP HTTP receiver
      - "4317:4317"   # OTLP gRPC receiver
    networks:
      - observability

  # Jaeger: Distributed tracing backend and UI
  jaeger:
    image: jaegertracing/all-in-one:1.52
    environment:
      - COLLECTOR_OTLP_ENABLED=true
    ports:
      - "16686:16686" # Jaeger UI
      - "4317:4317"   # OTLP gRPC
    networks:
      - observability

  # Prometheus: Metrics storage and querying
  prometheus:
    image: prom/prometheus:v2.48.1
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"   # Prometheus UI
    networks:
      - observability

  # Grafana: Visualization and dashboards
  grafana:
    image: grafana/grafana:10.2.3
    environment:
      - GF_AUTH_ANONYMOUS_ENABLED=true
      - GF_AUTH_ANONYMOUS_ORG_ROLE=Admin
      - GF_AUTH_DISABLE_LOGIN_FORM=true
    volumes:
      - grafana-data:/var/lib/grafana
    ports:
      - "3001:3000"   # Grafana UI (port 3001 to avoid conflict with app)
    networks:
      - observability

networks:
  observability:
    driver: bridge

volumes:
  prometheus-data:
  grafana-data:
```

**File**: `otel-collector-config.yaml`

```yaml
receivers:
  otlp:
    protocols:
      http:
        endpoint: 0.0.0.0:4318
      grpc:
        endpoint: 0.0.0.0:4317

processors:
  batch:
    timeout: 10s
    send_batch_size: 1024

exporters:
  otlp:
    endpoint: jaeger:4317
    tls:
      insecure: true
  logging:
    loglevel: debug

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp, logging]
```

**File**: `prometheus.yml`

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'payment-service'
    static_configs:
      - targets: ['host.docker.internal:3000']  # Mac/Windows Docker host
        # For Linux, use: targets: ['172.17.0.1:3000']
        labels:
          service: 'payment-service'
          environment: 'development'
```

## Running the Example

### Step 1: Install Dependencies

```bash
npm install
```

### Step 2: Start Observability Stack

```bash
docker-compose up -d
```

Verify all services are running:

```bash
docker-compose ps
```

Expected output:
```
NAME                COMMAND                  SERVICE         STATUS
jaeger              "/go/bin/all-in-one"     jaeger          Up
otel-collector      "/otelcol-contrib ..."   otel-collector  Up
prometheus          "/bin/prometheus ..."    prometheus      Up
grafana             "/run.sh"                grafana         Up
```

### Step 3: Start Payment Service

```bash
npm run dev
```

Expected output:
```
OpenTelemetry SDK initialized
{"level":"INFO","timestamp":"2025-12-07T10:00:00.000Z","service":"payment-service",...,"msg":"Payment service started on port 3000"}
```

### Step 4: Send Test Requests

**Successful payment**:

```bash
curl -X POST http://localhost:3000/api/payments \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: test_001" \
  -d '{
    "amount": 99.99,
    "currency": "USD",
    "paymentMethod": "credit_card",
    "customerId": "cust_12345"
  }'
```

Response:
```json
{
  "success": true,
  "transactionId": "txn_1701958800000_abc123",
  "status": "success",
  "amount": 99.99,
  "currency": "USD"
}
```

**Failed payment** (invalid amount):

```bash
curl -X POST http://localhost:3000/api/payments \
  -H "Content-Type: application/json" \
  -d '{
    "amount": -10,
    "currency": "USD",
    "paymentMethod": "credit_card",
    "customerId": "cust_12345"
  }'
```

Response:
```json
{
  "success": false,
  "error": "Invalid payment amount"
}
```

### Step 5: View Observability Data

**Jaeger UI** (traces):
- Open http://localhost:16686
- Select service: `payment-service`
- Click "Find Traces"
- View trace showing HTTP request → validatePayment → processPayment spans

**Prometheus UI** (metrics):
- Open http://localhost:9090
- Query: `rate(http_requests_total[1m])` (request rate per second)
- Query: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))` (p95 latency)
- Query: `payments_total` (total payments by status)

**Grafana UI** (dashboards):
- Open http://localhost:3001
- Add Prometheus data source: http://prometheus:9090
- Add Jaeger data source: http://jaeger:16686
- Create dashboard with panels for request rate, error rate, latency, payments

## Debugging Scenario

### Problem: Increased Payment Latency

**Symptom**: Users report slow payment processing. API latency p95 increased from 150ms to 2s.

### Step 1: Check Metrics Dashboard

Open Prometheus and run query:

```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{route="/api/payments"}[5m]))
```

**Observation**: p95 latency is 2.1 seconds (previously 150ms). Something is wrong.

### Step 2: Find Slow Traces

Open Jaeger UI:
1. Service: `payment-service`
2. Operation: `POST /api/payments`
3. Min Duration: `2s` (filter for slow requests)
4. Click "Find Traces"

**Observation**: Multiple traces showing 2-3 second duration.

### Step 3: Analyze Trace Breakdown

Click on a slow trace to see span breakdown:

```
Trace ID: 4bf92f3577b34da6a3ce929d0e0e4736
Total Duration: 2.2s

├─ POST /api/payments (2.2s) [http span]
   ├─ validatePayment (50ms) [manual span]
   └─ processPayment (2.1s) [manual span]  ← BOTTLENECK
```

**Observation**: The `processPayment` span is taking 2.1s (previously 100-200ms).

### Step 4: Read Correlated Logs

Search logs for trace ID `4bf92f3577b34da6a3ce929d0e0e4736`:

```bash
# Assuming logs are aggregated in Loki/ELK
# Or grep application logs directly
grep "4bf92f3577b34da6a3ce929d0e0e4736" logs/app.log
```

Log output:
```json
{
  "level": "ERROR",
  "timestamp": "2025-12-07T10:32:15.456Z",
  "traceId": "4bf92f3577b34da6a3ce929d0e0e4736",
  "spanId": "00f067aa0ba902b7",
  "correlationId": "req_7f8a9b2c",
  "msg": "Payment processing failed",
  "error": "Payment gateway timeout",
  "amount": 99.99,
  "paymentMethod": "credit_card"
}
```

**Observation**: Logs show "Payment gateway timeout" errors, indicating external API (Stripe/PayPal) is slow or unavailable.

### Step 5: Root Cause and Resolution

**Root Cause**: External payment gateway (Stripe API) is experiencing degraded performance, causing 2-3 second timeouts.

**Resolution Options**:
1. **Short-term**: Implement circuit breaker to fail fast instead of waiting for timeout
2. **Medium-term**: Add retry logic with exponential backoff
3. **Long-term**: Implement asynchronous payment processing (message queue)

**Verification**: After implementing circuit breaker, check metrics again:
- Latency p95 back to 150ms (failing fast instead of waiting)
- Error rate increased temporarily (expected, circuit breaker rejecting requests)
- Alert DevOps team to monitor external API recovery

### Key Takeaway

This debugging workflow demonstrates the power of unified observability:
1. **Metrics** identified the symptom (high latency)
2. **Traces** identified the bottleneck (processPayment span)
3. **Logs** provided root cause (payment gateway timeout)

Without correlation (traceId in logs, shared labels in metrics), this investigation would have taken hours instead of minutes.

## Summary

This example demonstrates production-ready observability implementation in Express.js:

- **OpenTelemetry**: Auto-instrumentation for HTTP + manual spans for business logic
- **Structured Logging**: JSON logs with trace context correlation
- **Metrics**: RED method + business metrics (payments, revenue)
- **Distributed Tracing**: W3C Trace Context propagation, exported to Jaeger
- **Local Stack**: Docker Compose with Jaeger, Prometheus, Grafana
- **Debugging Workflow**: Metrics → Traces → Logs unified investigation

**Production Considerations**:
- Replace Docker Compose with managed APM platform (DataDog, New Relic, Grafana Cloud)
- Implement sampling strategy (1-10% probabilistic + tail sampling for errors)
- Add PII redaction in logs (mask credit card numbers, emails)
- Configure retention policies (7-30 days hot storage, 90-365 days cold storage)
- Set up alerting rules (error rate >5%, latency p95 >500ms)
- Implement log rotation and compression for disk space management
- Add authentication for metrics endpoint (basic auth, API key)

**Next Steps**:
- Extend to multi-service architecture (API Gateway, User Service, Payment Service)
- Add database observability (query performance, connection pool metrics)
- Implement frontend observability (Real User Monitoring, error tracking)
- Set up automated dashboards with Grafana provisioning
- Configure alerting with Alertmanager or APM platform alerts
