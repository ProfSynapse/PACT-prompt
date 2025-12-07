# Logging Patterns Reference

## 1. Structured Logging Fundamentals

### JSON vs Plain Text

Structured logging uses JSON format instead of plain text to enable queryable, machine-readable logs. While JSON adds ~50-100% storage overhead compared to plain text, modern compression reduces this to ~20-30% after gzip compression. The trade-off is worthwhile for production systems:

**Plain Text Log** (Hard to Query):
```
2025-12-07 10:30:00 INFO Payment processed successfully for user user_12345 amount 99.99 USD duration 145ms
```

**Structured JSON Log** (Queryable):
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

### Essential Field Specification

Every structured log entry should include these standard fields:

| Field | Type | Purpose | Format Example |
|-------|------|---------|----------------|
| `timestamp` | ISO 8601 UTC | When event occurred | `2025-12-07T10:30:00.123Z` |
| `level` | String | Log severity | `ERROR`, `WARN`, `INFO`, `DEBUG` |
| `message` | String | Human-readable summary | `Payment processed successfully` |
| `service` | String | Service identifier | `payment-service` |
| `traceId` | String | OpenTelemetry trace ID | `4bf92f3577b34da6a3ce929d0e0e4736` |
| `spanId` | String | OpenTelemetry span ID | `00f067aa0ba902b7` |
| `correlationId` | String | Request correlation ID | `req_7f8a9b2c3d4e` |
| `userId` | String (optional) | User context | `user_12345` |
| `sessionId` | String (optional) | Session context | `sess_abc123` |
| `error` | Object (optional) | Error details | `{"name": "ValidationError", "message": "..."}` |

### Field Naming Conventions

Use consistent naming across all services to enable unified queries:

- **Case style**: Choose camelCase or snake_case and stick to it across all services
- **Avoid abbreviations**: Use `correlationId` not `corrId`, `userId` not `uid`
- **Standard names**: Use `traceId` (not `trace_id` or `trace-id`), `spanId` (not `span_id`)
- **Nested objects**: Group related fields (e.g., `error.name`, `error.message`, `error.stack`)

**Bad - Inconsistent naming**:
```json
{
  "user_id": "123",        // snake_case
  "sessionID": "abc",      // PascalCase
  "corrId": "xyz",         // abbreviated
  "trace-id": "def"        // kebab-case
}
```

**Good - Consistent naming**:
```json
{
  "userId": "123",
  "sessionId": "abc",
  "correlationId": "xyz",
  "traceId": "def"
}
```

### Log Levels Semantic Guidance

Use log levels to indicate operational urgency:

**ERROR** - Action required, service degraded
- System is in degraded state requiring immediate attention
- Failed critical operations (payment processing failed, database unreachable)
- Alerts should trigger on ERROR logs
- Examples: Database connection lost, external API timeout, unhandled exception

**WARN** - Potential issue, no immediate action required
- Recoverable errors or unexpected behavior that doesn't impact users
- Performance degradation or approaching resource limits
- Deprecated API usage
- Examples: Retry succeeded after failure, slow database query (>500ms), high memory usage (>80%)

**INFO** - Business events and significant state changes
- Normal operation milestones that provide business value
- User actions, transaction completions, state transitions
- Service lifecycle events (started, stopped, configuration updated)
- Examples: User registered, payment processed, cache refreshed, service started

**DEBUG** - Troubleshooting details and verbose context
- Detailed execution flow for debugging purposes
- Variable values, intermediate computation results
- Should be disabled in production or sampled
- Examples: Function entry/exit, query parameters, HTTP request/response bodies

**Production Recommendation**: Set default log level to INFO, enable DEBUG only for specific services during troubleshooting.

---

## 2. Language-Specific Implementation

### Node.js - Pino

Pino is the fastest JSON logger for Node.js with zero-configuration JSON output and low overhead.

**Installation**:
```bash
npm install pino
```

**Configuration**:
```javascript
// logger.js - Centralized logger configuration
// Location: src/utils/logger.js
// Used by: All application modules for logging
// Dependencies: pino

const pino = require('pino');

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  formatters: {
    level: (label) => ({ level: label.toUpperCase() })
  },
  base: {
    service: process.env.SERVICE_NAME || 'default-service'
  },
  timestamp: () => `,"timestamp":"${new Date().toISOString()}"`,
  redact: {
    paths: ['password', 'creditCard', 'ssn', '*.password', '*.creditCard'],
    remove: true
  }
});

module.exports = logger;
```

**Usage with Context**:
```javascript
// Example: Express middleware for request logging
// Location: src/middleware/requestLogger.js
// Used by: app.js (applied to all routes)
// Dependencies: logger.js, @opentelemetry/api

const logger = require('../utils/logger');
const { trace } = require('@opentelemetry/api');

function requestLogger(req, res, next) {
  const start = Date.now();

  // Extract OpenTelemetry trace context
  const span = trace.getActiveSpan();
  const traceId = span?.spanContext().traceId;
  const spanId = span?.spanContext().spanId;

  // Create request-scoped logger with context
  req.logger = logger.child({
    correlationId: req.headers['x-correlation-id'] || `req_${Date.now()}`,
    traceId,
    spanId,
    userId: req.user?.id,
    sessionId: req.session?.id
  });

  res.on('finish', () => {
    const duration = Date.now() - start;
    req.logger.info({
      method: req.method,
      path: req.path,
      statusCode: res.statusCode,
      duration
    }, 'HTTP request completed');
  });

  next();
}

module.exports = requestLogger;
```

**Usage in Application Code**:
```javascript
// Example: Payment service with structured logging
async function processPayment(paymentData, logger) {
  logger.info({
    amount: paymentData.amount,
    currency: paymentData.currency,
    paymentMethod: paymentData.method
  }, 'Processing payment');

  try {
    const result = await paymentGateway.charge(paymentData);

    logger.info({
      transactionId: result.id,
      amount: paymentData.amount,
      currency: paymentData.currency,
      duration: result.duration
    }, 'Payment processed successfully');

    return result;
  } catch (error) {
    logger.error({
      error: {
        name: error.name,
        message: error.message,
        stack: error.stack
      },
      amount: paymentData.amount,
      currency: paymentData.currency
    }, 'Payment processing failed');

    throw error;
  }
}
```

### Python - Loguru

Loguru provides structured JSON logging with minimal configuration and excellent developer experience.

**Installation**:
```bash
pip install loguru
```

**Configuration**:
```python
# logger.py - Centralized logger configuration
# Location: src/utils/logger.py
# Used by: All application modules for logging
# Dependencies: loguru

import sys
import os
from loguru import logger

# Remove default handler
logger.remove()

# Add JSON handler for structured logging
logger.add(
    sys.stdout,
    format="{message}",
    serialize=True,  # JSON output
    level=os.getenv("LOG_LEVEL", "INFO")
)

# Add context fields
logger = logger.bind(service=os.getenv("SERVICE_NAME", "default-service"))

def configure_logger(correlation_id=None, trace_id=None, span_id=None, user_id=None):
    """Create request-scoped logger with context."""
    return logger.bind(
        correlationId=correlation_id,
        traceId=trace_id,
        spanId=span_id,
        userId=user_id
    )
```

**Usage with Flask**:
```python
# Example: Flask middleware for request logging
# Location: src/middleware/request_logger.py
# Used by: app.py (applied to all routes via @app.before_request)
# Dependencies: logger.py, opentelemetry

from flask import request, g
from opentelemetry import trace
from utils.logger import configure_logger
import time

@app.before_request
def before_request():
    # Extract OpenTelemetry trace context
    span = trace.get_current_span()
    trace_id = format(span.get_span_context().trace_id, '032x') if span else None
    span_id = format(span.get_span_context().span_id, '016x') if span else None

    # Create request-scoped logger
    correlation_id = request.headers.get('X-Correlation-ID', f"req_{int(time.time() * 1000)}")
    g.logger = configure_logger(
        correlation_id=correlation_id,
        trace_id=trace_id,
        span_id=span_id,
        user_id=getattr(request, 'user_id', None)
    )

    g.start_time = time.time()

@app.after_request
def after_request(response):
    duration = (time.time() - g.start_time) * 1000  # milliseconds

    g.logger.info(
        "HTTP request completed",
        method=request.method,
        path=request.path,
        statusCode=response.status_code,
        duration=duration
    )

    return response
```

**Usage in Application Code**:
```python
# Example: Payment service with structured logging
async def process_payment(payment_data, logger):
    logger.info(
        "Processing payment",
        amount=payment_data['amount'],
        currency=payment_data['currency'],
        paymentMethod=payment_data['method']
    )

    try:
        result = await payment_gateway.charge(payment_data)

        logger.info(
            "Payment processed successfully",
            transactionId=result['id'],
            amount=payment_data['amount'],
            currency=payment_data['currency'],
            duration=result['duration']
        )

        return result
    except Exception as error:
        logger.error(
            "Payment processing failed",
            error={
                "name": type(error).__name__,
                "message": str(error),
                "stack": traceback.format_exc()
            },
            amount=payment_data['amount'],
            currency=payment_data['currency']
        )

        raise
```

### Java - Logback with Logstash Encoder

Logback with Logstash JSON encoder provides structured logging for Java applications.

**Dependencies** (Maven):
```xml
<dependency>
  <groupId>ch.qos.logback</groupId>
  <artifactId>logback-classic</artifactId>
  <version>1.4.14</version>
</dependency>
<dependency>
  <groupId>net.logstash.logback</groupId>
  <artifactId>logstash-logback-encoder</artifactId>
  <version>7.4</version>
</dependency>
```

**Configuration** (logback.xml):
```xml
<!-- logback.xml - Logback configuration for JSON logging -->
<!-- Location: src/main/resources/logback.xml -->
<!-- Used by: All Java application classes via SLF4J -->
<configuration>
  <appender name="JSON" class="ch.qos.logback.core.ConsoleAppender">
    <encoder class="net.logstash.logback.encoder.LogstashEncoder">
      <customFields>{"service":"${SERVICE_NAME:-default-service}"}</customFields>
      <fieldNames>
        <timestamp>timestamp</timestamp>
        <message>message</message>
        <logger>[ignore]</logger>
        <thread>[ignore]</thread>
      </fieldNames>
    </encoder>
  </appender>

  <root level="${LOG_LEVEL:-INFO}">
    <appender-ref ref="JSON" />
  </root>
</configuration>
```

**Usage in Application Code**:
```java
// Example: Payment service with structured logging
// Location: src/main/java/com/example/service/PaymentService.java
// Used by: PaymentController for payment processing
// Dependencies: SLF4J, Logstash Logback Encoder

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import net.logstash.logback.argument.StructuredArguments;
import io.opentelemetry.api.trace.Span;

public class PaymentService {
    private static final Logger logger = LoggerFactory.getLogger(PaymentService.class);

    public Payment processPayment(PaymentData paymentData, String correlationId) {
        // Extract OpenTelemetry trace context
        Span span = Span.current();
        String traceId = span.getSpanContext().getTraceId();
        String spanId = span.getSpanContext().getSpanId();

        logger.info("Processing payment",
            StructuredArguments.keyValue("correlationId", correlationId),
            StructuredArguments.keyValue("traceId", traceId),
            StructuredArguments.keyValue("spanId", spanId),
            StructuredArguments.keyValue("amount", paymentData.getAmount()),
            StructuredArguments.keyValue("currency", paymentData.getCurrency()),
            StructuredArguments.keyValue("paymentMethod", paymentData.getMethod())
        );

        try {
            Payment result = paymentGateway.charge(paymentData);

            logger.info("Payment processed successfully",
                StructuredArguments.keyValue("correlationId", correlationId),
                StructuredArguments.keyValue("traceId", traceId),
                StructuredArguments.keyValue("spanId", spanId),
                StructuredArguments.keyValue("transactionId", result.getId()),
                StructuredArguments.keyValue("amount", paymentData.getAmount()),
                StructuredArguments.keyValue("currency", paymentData.getCurrency()),
                StructuredArguments.keyValue("duration", result.getDuration())
            );

            return result;
        } catch (Exception error) {
            logger.error("Payment processing failed",
                StructuredArguments.keyValue("correlationId", correlationId),
                StructuredArguments.keyValue("traceId", traceId),
                StructuredArguments.keyValue("spanId", spanId),
                StructuredArguments.keyValue("error", Map.of(
                    "name", error.getClass().getName(),
                    "message", error.getMessage()
                )),
                StructuredArguments.keyValue("amount", paymentData.getAmount()),
                StructuredArguments.keyValue("currency", paymentData.getCurrency())
            );

            throw error;
        }
    }
}
```

### C#/.NET - Serilog

Serilog is the leading structured logging library for .NET with first-class JSON support.

**Installation**:
```bash
dotnet add package Serilog
dotnet add package Serilog.Sinks.Console
dotnet add package Serilog.Formatting.Compact
```

**Configuration**:
```csharp
// Program.cs - Serilog configuration
// Location: src/Program.cs
// Used by: Application startup, all services via ILogger<T>
// Dependencies: Serilog, Serilog.Sinks.Console, Serilog.Formatting.Compact

using Serilog;
using Serilog.Formatting.Compact;

Log.Logger = new LoggerConfiguration()
    .Enrich.WithProperty("service", Environment.GetEnvironmentVariable("SERVICE_NAME") ?? "default-service")
    .WriteTo.Console(new CompactJsonFormatter())
    .MinimumLevel.Information()
    .CreateLogger();

var builder = WebApplication.CreateBuilder(args);
builder.Host.UseSerilog();
```

**Usage in Application Code**:
```csharp
// Example: Payment service with structured logging
// Location: src/Services/PaymentService.cs
// Used by: PaymentController for payment processing
// Dependencies: Serilog, OpenTelemetry

using Serilog;
using System.Diagnostics;

public class PaymentService
{
    private readonly ILogger<PaymentService> _logger;

    public PaymentService(ILogger<PaymentService> logger)
    {
        _logger = logger;
    }

    public async Task<Payment> ProcessPayment(PaymentData paymentData, string correlationId)
    {
        // Extract OpenTelemetry trace context
        var activity = Activity.Current;
        var traceId = activity?.TraceId.ToString();
        var spanId = activity?.SpanId.ToString();

        _logger.LogInformation(
            "Processing payment for {Amount} {Currency}",
            paymentData.Amount,
            paymentData.Currency,
            correlationId,
            traceId,
            spanId,
            paymentData.Method
        );

        try
        {
            var result = await _paymentGateway.Charge(paymentData);

            _logger.LogInformation(
                "Payment processed successfully: {TransactionId}",
                result.Id,
                correlationId,
                traceId,
                spanId,
                paymentData.Amount,
                paymentData.Currency,
                result.Duration
            );

            return result;
        }
        catch (Exception error)
        {
            _logger.LogError(
                error,
                "Payment processing failed for {Amount} {Currency}",
                paymentData.Amount,
                paymentData.Currency,
                correlationId,
                traceId,
                spanId
            );

            throw;
        }
    }
}
```

### Go - zap

zap is the fastest structured logging library for Go with zero-allocation JSON encoding.

**Installation**:
```bash
go get go.uber.org/zap
```

**Configuration**:
```go
// logger.go - Centralized logger configuration
// Location: pkg/observability/logger.go
// Used by: All application modules for logging
// Dependencies: go.uber.org/zap

package observability

import (
	"os"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

// NewLogger creates a new production logger instance
func NewLogger() (*zap.Logger, error) {
	// Configure encoder for production JSON output
	encoderConfig := zap.NewProductionEncoderConfig()
	encoderConfig.TimeKey = "timestamp"
	encoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder
	encoderConfig.LevelKey = "level"
	encoderConfig.EncodeLevel = zapcore.CapitalLevelEncoder

	// Determine log level from environment with error handling
	logLevel := zapcore.InfoLevel
	if lvl := os.Getenv("LOG_LEVEL"); lvl != "" {
		if err := logLevel.UnmarshalText([]byte(lvl)); err != nil {
			// Fall back to INFO level if invalid level specified
			logLevel = zapcore.InfoLevel
		}
	}

	core := zapcore.NewCore(
		zapcore.NewJSONEncoder(encoderConfig),
		zapcore.AddSync(os.Stdout),
		logLevel,
	)

	logger := zap.New(core).With(
		zap.String("service", getEnvOrDefault("SERVICE_NAME", "default-service")),
		zap.String("environment", getEnvOrDefault("ENVIRONMENT", "production")),
	)

	return logger, nil
}

// WithContext creates a request-scoped logger with trace context
func WithContext(logger *zap.Logger, correlationID, traceID, spanID string) *zap.Logger {
	return logger.With(
		zap.String("correlationId", correlationID),
		zap.String("traceId", traceID),
		zap.String("spanId", spanID),
	)
}

func getEnvOrDefault(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
```

**Usage with HTTP Middleware**:
```go
// middleware.go - HTTP middleware for request logging
// Location: pkg/middleware/logging.go
// Used by: HTTP router (applied to all routes)
// Dependencies: logger.go, go.opentelemetry.io/otel/trace

package middleware

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"net/http"
	"time"

	"go.opentelemetry.io/otel/trace"
	"go.uber.org/zap"

	"myapp/pkg/observability"
)

type contextKey string

const loggerKey contextKey = "logger"

// NewLoggingMiddleware creates HTTP middleware for request logging
func NewLoggingMiddleware(logger *zap.Logger) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()

			// Extract or generate correlation ID
			correlationID := r.Header.Get("X-Correlation-ID")
			if correlationID == "" {
				correlationID = generateCorrelationID()
			}

			// Extract OpenTelemetry trace context
			span := trace.SpanFromContext(r.Context())
			spanCtx := span.SpanContext()

			// Format trace IDs as hex strings (consistent with other languages)
			traceID := spanCtx.TraceID().String()
			spanID := spanCtx.SpanID().String()

			// Create request-scoped logger
			reqLogger := observability.WithContext(logger, correlationID, traceID, spanID)

			// Add logger to request context for downstream handlers
			ctx := context.WithValue(r.Context(), loggerKey, reqLogger)
			r = r.WithContext(ctx)

			// Log incoming request
			reqLogger.Info("Incoming request",
				zap.String("method", r.Method),
				zap.String("path", r.URL.Path),
				zap.String("userAgent", r.UserAgent()),
			)

			// Wrap response writer to capture status code
			wrapped := &responseWriter{ResponseWriter: w, statusCode: http.StatusOK}

			// Process request
			next.ServeHTTP(wrapped, r)

			// Log completed request
			duration := time.Since(start)
			reqLogger.Info("Request completed",
				zap.String("method", r.Method),
				zap.String("path", r.URL.Path),
				zap.Int("statusCode", wrapped.statusCode),
				zap.Duration("duration", duration),
			)
		})
	}
}

// LoggerFromContext extracts the logger from the request context
func LoggerFromContext(ctx context.Context) *zap.Logger {
	if logger, ok := ctx.Value(loggerKey).(*zap.Logger); ok {
		return logger
	}
	// Return no-op logger if not found (should never happen in practice)
	return zap.NewNop()
}

func generateCorrelationID() string {
	b := make([]byte, 8)
	rand.Read(b)
	return "req_" + hex.EncodeToString(b)
}

type responseWriter struct {
	http.ResponseWriter
	statusCode int
}

func (rw *responseWriter) WriteHeader(code int) {
	rw.statusCode = code
	rw.ResponseWriter.WriteHeader(code)
}
```

**Usage in Application Code**:
```go
// payment_service.go - Payment service with structured logging
// Location: pkg/services/payment_service.go
// Used by: HTTP handlers for payment processing
// Dependencies: logger.go, middleware.LoggerFromContext

package services

import (
	"context"
	"errors"
	"fmt"
	"runtime/debug"

	"go.uber.org/zap"

	"myapp/pkg/middleware"
)

type PaymentService struct {
	paymentGateway PaymentGateway
}

func NewPaymentService(gateway PaymentGateway) *PaymentService {
	return &PaymentService{paymentGateway: gateway}
}

type PaymentData struct {
	Amount   float64
	Currency string
	Method   string
}

type PaymentResult struct {
	ID       string
	Amount   float64
	Currency string
	Duration int64
}

// ProcessPayment processes a payment with structured logging
func (s *PaymentService) ProcessPayment(ctx context.Context, data PaymentData) (*PaymentResult, error) {
	// Extract logger from context (added by middleware)
	logger := middleware.LoggerFromContext(ctx)

	logger.Info("Processing payment",
		zap.Float64("amount", data.Amount),
		zap.String("currency", data.Currency),
		zap.String("paymentMethod", data.Method),
	)

	result, err := s.paymentGateway.Charge(ctx, data)
	if err != nil {
		// Log error with structured fields matching other language examples
		logger.Error("Payment processing failed",
			zap.Error(err),
			zap.String("errorType", getErrorType(err)),
			zap.String("errorMessage", err.Error()),
			zap.String("stack", string(debug.Stack())),
			zap.Float64("amount", data.Amount),
			zap.String("currency", data.Currency),
		)
		return nil, fmt.Errorf("payment processing failed: %w", err)
	}

	logger.Info("Payment processed successfully",
		zap.String("transactionId", result.ID),
		zap.Float64("amount", data.Amount),
		zap.String("currency", data.Currency),
		zap.Int64("duration", result.Duration),
	)

	return result, nil
}

// getErrorType extracts error type for categorization
func getErrorType(err error) string {
	// Check for common error types
	var gatewayErr *GatewayError
	if errors.As(err, &gatewayErr) {
		return "GatewayError"
	}

	var validationErr *ValidationError
	if errors.As(err, &validationErr) {
		return "ValidationError"
	}

	// Fall back to generic error type
	return "UnknownError"
}

// Example error types
type GatewayError struct {
	Message string
}

func (e *GatewayError) Error() string {
	return e.Message
}

type ValidationError struct {
	Field   string
	Message string
}

func (e *ValidationError) Error() string {
	return fmt.Sprintf("%s: %s", e.Field, e.Message)
}

// PaymentGateway interface for payment processing
type PaymentGateway interface {
	Charge(ctx context.Context, data PaymentData) (*PaymentResult, error)
}
```

### Language Comparison Summary

| Language | Library | JSON Output | Performance | Learning Curve | Ecosystem |
|----------|---------|-------------|-------------|----------------|-----------|
| Node.js | Pino | Native | Fastest | Low | Excellent |
| Python | Loguru | Via serialize | Fast | Low | Good |
| Java | Logback + Logstash | Native | Good | Medium | Excellent |
| C#/.NET | Serilog | Via formatter | Good | Low | Excellent |
| Go | zap | Native | Fastest | Medium | Good |
| Ruby | Semantic Logger | Native | Good | Low | Good |

---

## 3. Correlation and Context Propagation

### Correlation ID Generation Strategies

Correlation IDs enable tracing requests across distributed services.

**UUID v4** - Random, globally unique
```javascript
const { v4: uuidv4 } = require('uuid');
const correlationId = uuidv4(); // e.g., "7f8a9b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c"
```
- **Pros**: Globally unique, no coordination needed
- **Cons**: Long (36 characters), not sortable, not human-readable

**Prefixed Short UUID** - Human-readable, shorter
```javascript
const correlationId = `req_${uuidv4().substring(0, 12)}`; // e.g., "req_7f8a9b2c3d4e"
```
- **Pros**: Shorter (16 chars), human-readable prefix, identifiable as request ID
- **Cons**: Not guaranteed globally unique (collision risk with 12-char substring)

**Snowflake IDs** - Ordered, distributed
```javascript
// Using snowflake-id library
const { Snowflake } = require('nodejs-snowflake');
const snowflake = new Snowflake({ machineId: 1 });
const correlationId = snowflake.getUniqueID().toString(); // e.g., "123456789012345678"
```
- **Pros**: Sortable (timestamp-based), distributed generation, 64-bit integer
- **Cons**: Requires machine ID coordination, more complex setup

**Recommendation**: Use prefixed short UUID (`req_<12-char-uuid>`) for simplicity and human readability in most cases.

### Propagating Correlation IDs Across Services

**HTTP Header Standard**: Use `X-Correlation-ID` header (de facto standard)

**API Gateway Pattern** - Generate if missing
```javascript
// API Gateway: Generate correlation ID for incoming requests
// Location: src/middleware/correlationId.js
// Used by: API Gateway service (entry point)
// Dependencies: uuid

const { v4: uuidv4 } = require('uuid');

function correlationMiddleware(req, res, next) {
  // Use existing correlation ID or generate new one
  const correlationId = req.headers['x-correlation-id'] || `req_${uuidv4().substring(0, 12)}`;

  req.correlationId = correlationId;

  // Propagate to downstream services
  res.setHeader('X-Correlation-ID', correlationId);

  next();
}

module.exports = correlationMiddleware;
```

**Downstream Service Pattern** - Propagate in outgoing requests
```javascript
// Downstream Service: Propagate correlation ID to external services
// Location: src/services/userService.js
// Used by: PaymentService when calling User Service
// Dependencies: axios

const axios = require('axios');

async function getUserById(userId, correlationId) {
  const response = await axios.get(`https://user-service/users/${userId}`, {
    headers: {
      'X-Correlation-ID': correlationId
    }
  });

  return response.data;
}
```

**gRPC Metadata Propagation**
```javascript
// gRPC: Propagate correlation ID via metadata
const grpc = require('@grpc/grpc-js');

function callGrpcService(correlationId) {
  const metadata = new grpc.Metadata();
  metadata.add('x-correlation-id', correlationId);

  client.someMethod(request, metadata, (err, response) => {
    // Handle response
  });
}
```

### Integrating OpenTelemetry Trace/Span IDs in Logs

OpenTelemetry provides trace IDs and span IDs that should be included in every log entry for correlation with distributed traces.

**Extract Trace Context** (Node.js):
```javascript
// Location: src/middleware/requestLogger.js
// Extracts OpenTelemetry trace context and adds to logger

const { trace } = require('@opentelemetry/api');

function addTraceContext(req, res, next) {
  const span = trace.getActiveSpan();

  if (span) {
    const spanContext = span.spanContext();
    req.traceId = spanContext.traceId;
    req.spanId = spanContext.spanId;
  }

  // Create logger with trace context
  req.logger = logger.child({
    correlationId: req.correlationId,
    traceId: req.traceId,
    spanId: req.spanId
  });

  next();
}
```

**Extract Trace Context** (Python):
```python
# Location: src/middleware/trace_context.py
# Extracts OpenTelemetry trace context and adds to logger

from opentelemetry import trace

def add_trace_context(request, logger):
    try:
        span = trace.get_current_span()

        if span and span.is_recording():
            span_context = span.get_span_context()
            if span_context.is_valid:
                trace_id = format(span_context.trace_id, '032x')
                span_id = format(span_context.span_id, '016x')

                return logger.bind(
                    traceId=trace_id,
                    spanId=span_id
                )
    except Exception as e:
        # Tracing not initialized or error accessing span context
        # Log error but continue without trace context
        logger.warning(f"Failed to extract trace context: {e}")

    return logger
```

**Extract Trace Context** (Java):
```java
// Location: src/main/java/com/example/util/TraceContextExtractor.java
// Extracts OpenTelemetry trace context for structured logging

import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.SpanContext;

public class TraceContextExtractor {
    public static String getTraceId() {
        SpanContext spanContext = Span.current().getSpanContext();
        return spanContext.isValid() ? spanContext.getTraceId() : null;
    }

    public static String getSpanId() {
        SpanContext spanContext = Span.current().getSpanContext();
        return spanContext.isValid() ? spanContext.getSpanId() : null;
    }
}
```

**Result**: Logs can be correlated with distributed traces in APM platforms (DataDog, New Relic, Grafana) by matching trace IDs.

---

## 4. Log Aggregation Systems

### ELK Stack (Elasticsearch + Logstash + Kibana)

**Use Case**: On-premises deployment, full-text search priority, established ELK expertise

**Architecture**:
```
Application Logs → Filebeat → Logstash → Elasticsearch → Kibana (Visualization)
```

**Strengths**:
- **Powerful search**: Elasticsearch full-text search across all log fields
- **Flexible dashboards**: Kibana visualization and query builder
- **Rich ecosystem**: Beats (Filebeat, Metricbeat, etc.), plugins, community support
- **On-premises**: Full control for compliance/security requirements

**Weaknesses**:
- **Resource-intensive**: High memory/CPU usage (Elasticsearch requires 2-4 GB RAM minimum)
- **Operational complexity**: Cluster management, index lifecycle, shard optimization
- **Cost**: Elastic Cloud pricing comparable to DataDog (~$95/month per GB indexed)

**Configuration Example** (Filebeat → Elasticsearch):
```yaml
# filebeat.yml - Filebeat configuration for shipping logs to Elasticsearch
# Location: /etc/filebeat/filebeat.yml
# Purpose: Collect application logs and forward to Elasticsearch

filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/payment-service/*.log
    json.keys_under_root: true
    json.add_error_key: true
    fields:
      service: payment-service
      environment: production

output.elasticsearch:
  hosts: ["https://elasticsearch:9200"]
  index: "logs-payment-service-%{+yyyy.MM.dd}"
  username: "elastic"
  password: "${ELASTIC_PASSWORD}"

setup.ilm.enabled: true
setup.ilm.rollover_alias: "logs-payment-service"
setup.ilm.pattern: "{now/d}-000001"
```

**When to Choose**:
- On-premises requirement (compliance, data sovereignty)
- Need full-text search across all log content
- Established ELK expertise on team
- Willing to invest in operational overhead

### Grafana Loki

**Use Case**: Kubernetes/containers, cost-conscious, already using Prometheus/Grafana

**Architecture**:
```
Application Logs → Promtail → Loki → Grafana (Visualization)
```

**Strengths**:
- **Cost-effective**: Indexes only labels (not full text), stores logs in object storage (S3, GCS)
- **10x cheaper storage**: Compared to Elasticsearch (~$0.02/GB in S3 vs $0.20+/GB in Elasticsearch)
- **Kubernetes-native**: Native Kubernetes service discovery and label extraction
- **LogQL**: Query language similar to PromQL (low learning curve for Prometheus users)

**Weaknesses**:
- **Limited full-text search**: Can only search by labels, then grep log content
- **Slower queries**: Full-text grep on log content (not indexed) is slower than Elasticsearch
- **Grafana dependency**: Best experience requires Grafana ecosystem

**Configuration Example** (Promtail → Loki):
```yaml
# promtail-config.yaml - Promtail configuration for shipping logs to Loki
# Location: /etc/promtail/config.yaml
# Purpose: Collect application logs and forward to Loki with labels

server:
  http_listen_port: 9080
  grpc_listen_port: 0

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
          environment: production
          __path__: /var/log/payment-service/*.log

    pipeline_stages:
      - json:
          expressions:
            level: level
            traceId: traceId
            correlationId: correlationId
      - labels:
          level:
          traceId:
          correlationId:
```

**LogQL Query Examples**:
```logql
# Find all ERROR logs for payment-service
{job="payment-service"} | json | level="ERROR"

# Find logs for specific trace ID
{job="payment-service"} | json | traceId="4bf92f3577b34da6a3ce929d0e0e4736"

# Find logs containing "payment failed" (grep full text)
{job="payment-service"} |= "payment failed"

# Count error logs per minute
sum(rate({job="payment-service"} | json | level="ERROR" [1m]))
```

**When to Choose**:
- Kubernetes/container-heavy architecture
- Budget-constrained with high log volume
- Already using Prometheus and Grafana
- Label-based filtering sufficient (don't need full-text search across all fields)

### DataDog Logs

**Use Case**: Already using DataDog APM, want unified observability platform

**Architecture**:
```
Application Logs → DataDog Agent → DataDog Logs → DataDog Dashboard
```

**Strengths**:
- **Unified platform**: Integrated with metrics, traces, APM in single interface
- **Automatic correlation**: Logs automatically correlated with traces and metrics by trace ID
- **Automatic parsing**: DataDog automatically parses common log formats (JSON, Apache, NGINX)
- **Ease of use**: Minimal configuration, managed service
- **AI insights**: Anomaly detection, log pattern analysis

**Pricing**:
- **Ingestion**: $0.10/GB ingested
- **Indexing**: $1.70/million log events indexed
- **15-day retention** included, $1.27/million events/month for extended retention

**Cost Example**: 100 GB logs/day = $3,000/month ingestion + ~$5,000/month indexing = $8,000/month

**Configuration Example** (DataDog Agent):
```yaml
# datadog.yaml - DataDog Agent configuration for log collection
# Location: /etc/datadog-agent/conf.d/payment-service.yaml
# Purpose: Collect application logs and forward to DataDog

logs:
  - type: file
    path: /var/log/payment-service/*.log
    service: payment-service
    source: nodejs
    sourcecategory: application
    tags:
      - env:production
      - team:payments
```

**Application Configuration** (Node.js with DD Trace):
```javascript
// Automatic log correlation with traces
const tracer = require('dd-trace').init({
  service: 'payment-service',
  env: 'production',
  logInjection: true  // Automatically inject trace IDs into logs
});

const logger = require('pino')();
// Logs will automatically include dd.trace_id and dd.span_id
```

**When to Choose**:
- Already using DataDog for APM or infrastructure monitoring
- Want unified observability (logs + metrics + traces in one platform)
- Need automatic correlation between logs and traces
- Budget for premium managed service

### Decision Matrix

| Feature | ELK Stack | Grafana Loki | DataDog Logs |
|---------|-----------|--------------|--------------|
| **Full-text search** | ⭐⭐⭐⭐⭐ Elasticsearch | ⭐⭐ Label-based only | ⭐⭐⭐⭐⭐ Full indexing |
| **Cost (high volume)** | ⭐⭐ Expensive at scale | ⭐⭐⭐⭐⭐ 10x cheaper | ⭐⭐ $8k/month for 100GB/day |
| **Kubernetes-native** | ⭐⭐⭐ Via Beats | ⭐⭐⭐⭐⭐ Native support | ⭐⭐⭐⭐ Agent-based |
| **Operational complexity** | ⭐⭐ High maintenance | ⭐⭐⭐⭐ Low maintenance | ⭐⭐⭐⭐⭐ Fully managed |
| **Unified observability** | ⭐⭐ Separate tools | ⭐⭐⭐⭐ With Grafana | ⭐⭐⭐⭐⭐ Native platform |
| **Query speed** | ⭐⭐⭐⭐⭐ Indexed | ⭐⭐⭐ Grep-based | ⭐⭐⭐⭐⭐ Indexed |
| **Setup complexity** | ⭐⭐ Complex cluster | ⭐⭐⭐⭐ Simple config | ⭐⭐⭐⭐⭐ Agent install |

**Decision Tree**:
```
START: Choose log aggregation system

├─ On-premises requirement (compliance, data sovereignty)?
│  └─ YES → ELK Stack (full control, on-premises deployment)

├─ Already using DataDog for APM/metrics?
│  └─ YES → DataDog Logs (unified platform, automatic correlation)

├─ Kubernetes/container-heavy + cost-conscious?
│  └─ YES → Grafana Loki (10x cheaper, Kubernetes-native)

├─ Need full-text search across all log fields?
│  └─ YES → ELK Stack or DataDog Logs (full indexing)

├─ High log volume (>500 GB/day) + budget constraints?
│  └─ YES → Grafana Loki (object storage, low cost)

└─ Default → Start with Grafana Loki (cost-effective), migrate to ELK/DataDog if search needs grow
```

---

## 5. Security and Performance

### PII Redaction and Masking Patterns

**Never log sensitive data**: Passwords, API keys, credit cards, SSNs, health data (HIPAA), financial data

**Automatic Redaction** (Pino):
```javascript
const logger = pino({
  redact: {
    paths: [
      'password',
      'creditCard',
      'ssn',
      'apiKey',
      'token',
      '*.password',      // Nested fields
      '*.creditCard',
      'headers.authorization'
    ],
    remove: true  // Remove fields entirely (vs masking with [Redacted])
  }
});

logger.info({
  userId: '123',
  password: 'secret123',  // Will be removed
  creditCard: '4111-1111-1111-1111'  // Will be removed
}, 'User action');
```

**Field-Level Masking**:
```javascript
// Mask credit card: Show last 4 digits
function maskCreditCard(cardNumber) {
  return `****-****-****-${cardNumber.slice(-4)}`;
}

// Mask email: Show domain only
function maskEmail(email) {
  const [, domain] = email.split('@');
  return `***@${domain}`;
}

logger.info({
  userId: '123',
  creditCard: maskCreditCard('4111111111111111'),  // ****-****-****-1111
  email: maskEmail('user@example.com')              // ***@example.com
}, 'Payment processed');
```

**Loguru PII Redaction** (Python):
```python
import re

def redact_pii(record):
    """Remove PII from log records."""
    sensitive_fields = ['password', 'creditCard', 'ssn', 'apiKey', 'token']

    for field in sensitive_fields:
        if field in record['extra']:
            record['extra'][field] = '[REDACTED]'

    return True

logger.add(sys.stdout, format="{message}", serialize=True, filter=redact_pii)
```

### Async Logging for Performance

Synchronous logging blocks the application thread while writing to disk/network. Async logging writes to a buffer and flushes periodically.

**Pino Async Transport** (Node.js):
```javascript
// Use pino-pretty in separate worker thread (async)
const pino = require('pino');
const logger = pino(pino.destination({
  dest: './logs/app.log',
  sync: false,  // Async writes
  minLength: 4096  // Buffer 4KB before flushing
}));
```

**Trade-off**: Risk of log loss on crash (logs in buffer not yet flushed to disk). Acceptable for most applications, but use synchronous logging for critical audit logs.

### Log Sampling for High-Volume Services

For services generating millions of DEBUG logs, sampling reduces log volume while preserving ERROR/WARN logs.

**Sample DEBUG Logs** (Keep 1% of DEBUG logs):
```javascript
function shouldLogDebug() {
  return Math.random() < 0.01;  // 1% sampling rate
}

function logDebug(logger, message, context) {
  if (shouldLogDebug()) {
    logger.debug(context, message);
  }
}

// Usage
logDebug(logger, 'Processing request', { userId: '123', requestId: 'abc' });
```

**Always Keep ERROR/WARN Logs** (No sampling):
```javascript
logger.error(context, 'Payment failed');  // Always logged
logger.warn(context, 'Slow query detected');  // Always logged
logger.info(context, 'User registered');  // Always logged
logDebug(logger, 'Function entry', context);  // 1% sampled
```

**Dynamic Sampling** (Increase sampling during errors):
```javascript
let debugSamplingRate = 0.01;  // 1% baseline

function adjustSamplingRate(errorRate) {
  if (errorRate > 0.05) {
    debugSamplingRate = 0.10;  // 10% during high error rate
  } else {
    debugSamplingRate = 0.01;  // 1% normal
  }
}
```

### Storage and Retention Policies

**Hot Storage** (7-30 days):
- Queryable, indexed logs for recent debugging
- Higher cost (Elasticsearch: $0.20+/GB, Loki: $0.02/GB)
- Fast query performance

**Cold Storage** (90-365 days):
- Archived logs for compliance, audit trails
- Lower cost (S3 Glacier: $0.004/GB)
- Slower retrieval (minutes to hours)

**Deletion** (After retention period):
- GDPR compliance: Delete logs containing user data after retention period
- Cost optimization: Avoid paying for long-term storage of unnecessary logs

**Retention Policy Example** (Elasticsearch ILM):
```json
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_size": "50GB",
            "max_age": "7d"
          }
        }
      },
      "warm": {
        "min_age": "7d",
        "actions": {
          "shrink": { "number_of_shards": 1 },
          "forcemerge": { "max_num_segments": 1 }
        }
      },
      "cold": {
        "min_age": "30d",
        "actions": {
          "freeze": {}
        }
      },
      "delete": {
        "min_age": "90d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
```

**Loki Retention** (Object Storage):
```yaml
# loki-config.yaml
limits_config:
  retention_period: 90d  # Keep logs for 90 days

chunk_store_config:
  max_look_back_period: 90d

table_manager:
  retention_deletes_enabled: true
  retention_period: 90d
```

---

This reference file provides production-ready logging patterns for implementing structured logging, correlation, log aggregation, and security best practices across Node.js, Python, Java, and C#/.NET applications.
