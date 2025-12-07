# Async Processing Patterns Reference

## Overview

Asynchronous processing is essential for building scalable, resilient backend systems. This reference covers job queues, background workers, retry strategies, dead letter queues, and event-driven patterns that enable reliable async processing.

## When to Use Async Processing

**Use async processing when**:
- Operations take longer than acceptable request timeout (>5 seconds)
- Tasks can be processed later without blocking user response
- High reliability is required for critical operations
- You need to handle traffic spikes gracefully
- External services have unreliable response times

**Common use cases**:
- Email/SMS/push notification sending
- Report generation and data exports
- Image/video processing and transformations
- Webhook delivery and external API calls
- Data imports and batch processing
- Scheduled/recurring tasks
- Event propagation across microservices

## Job Queue Patterns

### Message Queue Architecture

```
Producer (API/Service)
    │
    ├─> Queue (Redis/RabbitMQ/SQS)
    │       │
    │       ├─> Worker 1 (Consumer)
    │       ├─> Worker 2 (Consumer)
    │       └─> Worker N (Consumer)
    │
    └─> Results/Events
```

### Redis-Based Queues (BullMQ)

BullMQ is a modern, TypeScript-native job queue library backed by Redis with excellent performance and reliability.

**Core concepts**:
- **Queue**: Stores jobs to be processed
- **Worker**: Processes jobs from the queue
- **Job**: Unit of work with data and options
- **Flow**: Parent-child job dependencies

#### Basic Queue Implementation (TypeScript)

```typescript
import { Queue, Worker, Job } from 'bullmq';

// Define job data type
interface EmailJobData {
  to: string;
  subject: string;
  body: string;
  userId: string;
}

// Create queue
const emailQueue = new Queue<EmailJobData>('email-notifications', {
  connection: {
    host: 'localhost',
    port: 6379
  },
  defaultJobOptions: {
    attempts: 3,
    backoff: {
      type: 'exponential',
      delay: 2000
    },
    removeOnComplete: {
      age: 86400, // Keep completed jobs for 24 hours
      count: 1000 // Keep max 1000 completed jobs
    },
    removeOnFail: {
      age: 604800 // Keep failed jobs for 7 days
    }
  }
});

// Add job to queue (producer)
async function sendEmailAsync(emailData: EmailJobData) {
  const job = await emailQueue.add('send-email', emailData, {
    priority: emailData.userId === 'admin' ? 1 : 5,
    delay: 0 // Send immediately (or use ms for delay)
  });

  return { jobId: job.id };
}

// Process jobs (worker)
const emailWorker = new Worker<EmailJobData>(
  'email-notifications',
  async (job: Job<EmailJobData>) => {
    const { to, subject, body, userId } = job.data;

    console.log(`Processing email job ${job.id} for user ${userId}`);

    // Simulate email sending
    await emailService.send({
      to,
      subject,
      body
    });

    // Return result (stored in job)
    return {
      messageId: 'msg-123',
      sentAt: new Date().toISOString()
    };
  },
  {
    connection: {
      host: 'localhost',
      port: 6379
    },
    concurrency: 5, // Process up to 5 jobs concurrently
    limiter: {
      max: 10, // Max 10 jobs
      duration: 1000 // Per second (rate limiting)
    }
  }
);

// Event listeners
emailWorker.on('completed', (job: Job) => {
  console.log(`Job ${job.id} completed`, job.returnvalue);
});

emailWorker.on('failed', (job: Job | undefined, error: Error) => {
  console.error(`Job ${job?.id} failed`, error);
});

emailWorker.on('error', (error: Error) => {
  console.error('Worker error', error);
});
```

#### Python Queue Implementation (RQ)

```python
from redis import Redis
from rq import Queue, Worker
from typing import Dict, Any
import smtplib

# Connect to Redis
redis_conn = Redis(host='localhost', port=6379, db=0)

# Create queue
email_queue = Queue('email-notifications', connection=redis_conn)

# Job function
def send_email(to: str, subject: str, body: str, user_id: str) -> Dict[str, Any]:
    """Send email via SMTP"""
    print(f"Sending email to {to} for user {user_id}")

    # Simulate email sending
    # In production, use a proper email service
    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login('user', 'password')
        server.sendmail('from@example.com', to, f"Subject: {subject}\n\n{body}")

    return {
        'message_id': 'msg-123',
        'sent_at': datetime.utcnow().isoformat()
    }

# Enqueue job (producer)
def send_email_async(to: str, subject: str, body: str, user_id: str):
    job = email_queue.enqueue(
        send_email,
        to, subject, body, user_id,
        retry=Retry(max=3, interval=[10, 30, 60]),
        job_timeout='5m',
        result_ttl=86400  # Keep result for 24 hours
    )
    return {'job_id': job.id}

# Worker (run separately: rq worker email-notifications)
if __name__ == '__main__':
    worker = Worker([email_queue], connection=redis_conn)
    worker.work()
```

### RabbitMQ Pattern

RabbitMQ provides advanced routing, persistence, and reliability guarantees.

```typescript
import amqp, { Channel, Connection, ConsumeMessage } from 'amqplib';

class RabbitMQService {
  private connection: Connection | null = null;
  private channel: Channel | null = null;

  async connect() {
    this.connection = await amqp.connect('amqp://localhost');
    this.channel = await this.connection.createChannel();

    // Declare queue with durability
    await this.channel.assertQueue('email-queue', {
      durable: true, // Queue survives broker restart
      deadLetterExchange: 'dlx',
      deadLetterRoutingKey: 'email-failed'
    });

    // Declare dead letter queue
    await this.channel.assertQueue('email-failed', {
      durable: true
    });
  }

  async publishJob(queueName: string, data: any) {
    if (!this.channel) throw new Error('Channel not initialized');

    return this.channel.sendToQueue(
      queueName,
      Buffer.from(JSON.stringify(data)),
      {
        persistent: true, // Message survives broker restart
        priority: data.priority || 5,
        expiration: '3600000' // TTL: 1 hour
      }
    );
  }

  async consumeJobs(queueName: string, handler: (data: any) => Promise<void>) {
    if (!this.channel) throw new Error('Channel not initialized');

    // Set prefetch to control concurrency
    await this.channel.prefetch(5);

    await this.channel.consume(
      queueName,
      async (msg: ConsumeMessage | null) => {
        if (!msg) return;

        try {
          const data = JSON.parse(msg.content.toString());
          await handler(data);

          // Acknowledge success
          this.channel!.ack(msg);
        } catch (error) {
          console.error('Job processing failed', error);

          // Reject and requeue (or send to DLQ)
          this.channel!.nack(msg, false, false); // Don't requeue
        }
      },
      {
        noAck: false // Manual acknowledgment
      }
    );
  }
}
```

### AWS SQS Pattern

```typescript
import { SQSClient, SendMessageCommand, ReceiveMessageCommand, DeleteMessageCommand } from '@aws-sdk/client-sqs';

class SQSService {
  private client: SQSClient;
  private queueUrl: string;

  constructor(queueUrl: string) {
    this.client = new SQSClient({ region: 'us-east-1' });
    this.queueUrl = queueUrl;
  }

  async sendMessage(messageBody: any, delaySeconds: number = 0) {
    const command = new SendMessageCommand({
      QueueUrl: this.queueUrl,
      MessageBody: JSON.stringify(messageBody),
      DelaySeconds: delaySeconds,
      MessageAttributes: {
        Priority: {
          DataType: 'Number',
          StringValue: messageBody.priority?.toString() || '5'
        }
      }
    });

    return await this.client.send(command);
  }

  async processMessages(handler: (message: any) => Promise<void>) {
    while (true) {
      const command = new ReceiveMessageCommand({
        QueueUrl: this.queueUrl,
        MaxNumberOfMessages: 10,
        WaitTimeSeconds: 20, // Long polling
        VisibilityTimeout: 30
      });

      const response = await this.client.send(command);

      if (!response.Messages || response.Messages.length === 0) {
        continue;
      }

      for (const message of response.Messages) {
        try {
          const body = JSON.parse(message.Body!);
          await handler(body);

          // Delete message on success
          await this.client.send(new DeleteMessageCommand({
            QueueUrl: this.queueUrl,
            ReceiptHandle: message.ReceiptHandle!
          }));
        } catch (error) {
          console.error('Message processing failed', error);
          // Message will be retried after visibility timeout
        }
      }
    }
  }
}
```

## Background Workers

### Worker Pool Pattern

```typescript
import { Worker } from 'bullmq';
import os from 'os';

class WorkerPool {
  private workers: Worker[] = [];
  private queueName: string;

  constructor(queueName: string, concurrency?: number) {
    this.queueName = queueName;
    const workerCount = concurrency || os.cpus().length;

    // Create multiple worker processes
    for (let i = 0; i < workerCount; i++) {
      const worker = new Worker(
        queueName,
        async (job) => this.processJob(job),
        {
          connection: { host: 'localhost', port: 6379 },
          concurrency: 5,
          limiter: {
            max: 100,
            duration: 1000
          }
        }
      );

      worker.on('failed', (job, error) => {
        console.error(`Worker ${i} - Job ${job?.id} failed:`, error);
      });

      this.workers.push(worker);
    }
  }

  private async processJob(job: any) {
    // Implement job processing logic
    console.log(`Processing job ${job.id}`, job.data);
    return { success: true };
  }

  async shutdown() {
    await Promise.all(this.workers.map(w => w.close()));
  }
}
```

### Graceful Shutdown

```typescript
class GracefulWorker {
  private worker: Worker;
  private isShuttingDown = false;

  constructor(queueName: string) {
    this.worker = new Worker(queueName, async (job) => {
      if (this.isShuttingDown) {
        throw new Error('Worker is shutting down');
      }

      return await this.processJob(job);
    });

    this.setupShutdownHandlers();
  }

  private setupShutdownHandlers() {
    const shutdown = async (signal: string) => {
      console.log(`Received ${signal}, starting graceful shutdown`);
      this.isShuttingDown = true;

      // Stop accepting new jobs
      await this.worker.close();

      console.log('Worker shut down successfully');
      process.exit(0);
    };

    process.on('SIGTERM', () => shutdown('SIGTERM'));
    process.on('SIGINT', () => shutdown('SIGINT'));
  }

  private async processJob(job: any) {
    // Job processing logic
    return { success: true };
  }
}
```

### Python Worker with Concurrency Control

```python
import signal
from concurrent.futures import ThreadPoolExecutor
from rq import Worker, Queue
from redis import Redis

class ConcurrentWorker:
    def __init__(self, queue_name: str, max_workers: int = 5):
        self.redis_conn = Redis(host='localhost', port=6379)
        self.queue = Queue(queue_name, connection=self.redis_conn)
        self.max_workers = max_workers
        self.shutdown_requested = False

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        signal.signal(signal.SIGINT, self.handle_shutdown)

    def handle_shutdown(self, signum, frame):
        print(f"Received signal {signum}, shutting down gracefully...")
        self.shutdown_requested = True

    def start(self):
        worker = Worker(
            [self.queue],
            connection=self.redis_conn
        )

        # Process jobs until shutdown
        worker.work(with_scheduler=True)
```

## Retry Strategies

### Exponential Backoff with Jitter

Exponential backoff increases delay between retries exponentially. Jitter adds randomness to prevent thundering herd problems.

```typescript
interface RetryOptions {
  maxAttempts: number;
  baseDelay: number; // milliseconds
  maxDelay: number;
  jitterType: 'full' | 'equal' | 'decorrelated';
}

async function retryWithBackoff<T>(
  operation: () => Promise<T>,
  options: RetryOptions
): Promise<T> {
  const { maxAttempts, baseDelay, maxDelay, jitterType } = options;
  let lastError: Error;

  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error as Error;

      // Don't retry on certain errors
      if (error instanceof ValidationError || error instanceof UnauthorizedError) {
        throw error;
      }

      if (attempt < maxAttempts - 1) {
        const delay = calculateDelay(attempt, baseDelay, maxDelay, jitterType);

        console.log(`Attempt ${attempt + 1} failed, retrying in ${delay}ms`, {
          error: lastError.message
        });

        await sleep(delay);
      }
    }
  }

  throw new MaxRetriesExceededError(
    `Failed after ${maxAttempts} attempts: ${lastError.message}`
  );
}

function calculateDelay(
  attempt: number,
  baseDelay: number,
  maxDelay: number,
  jitterType: 'full' | 'equal' | 'decorrelated'
): number {
  const exponentialDelay = Math.min(
    baseDelay * Math.pow(2, attempt),
    maxDelay
  );

  switch (jitterType) {
    case 'full':
      // Full jitter: random between 0 and exponential delay
      return Math.random() * exponentialDelay;

    case 'equal':
      // Equal jitter: half deterministic, half random
      return exponentialDelay / 2 + Math.random() * (exponentialDelay / 2);

    case 'decorrelated':
      // Decorrelated jitter: more aggressive randomization
      return Math.random() * Math.min(maxDelay, baseDelay * 3);

    default:
      return exponentialDelay;
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Usage
const result = await retryWithBackoff(
  () => externalAPI.call(),
  {
    maxAttempts: 5,
    baseDelay: 1000,
    maxDelay: 30000,
    jitterType: 'full'
  }
);
```

### Python Retry with Backoff

```python
import random
import time
from typing import Callable, TypeVar, Any
from functools import wraps

T = TypeVar('T')

def retry_with_backoff(
    max_attempts: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True
):
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except (ValidationError, UnauthorizedError):
                    # Don't retry client errors
                    raise
                except Exception as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        # Calculate exponential backoff
                        delay = min(base_delay * (2 ** attempt), max_delay)

                        # Add jitter
                        if jitter:
                            delay = delay * random.random()

                        print(f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s")
                        time.sleep(delay)

            raise MaxRetriesExceededError(
                f"Failed after {max_attempts} attempts: {last_exception}"
            )

        return wrapper
    return decorator

# Usage
@retry_with_backoff(max_attempts=5, base_delay=1.0, jitter=True)
def call_external_api():
    response = requests.get('https://api.example.com/data')
    response.raise_for_status()
    return response.json()
```

### Circuit Breaker Pattern

Prevents cascading failures by stopping requests to failing services.

```typescript
enum CircuitState {
  CLOSED = 'CLOSED',
  OPEN = 'OPEN',
  HALF_OPEN = 'HALF_OPEN'
}

interface CircuitBreakerOptions {
  failureThreshold: number;
  successThreshold: number;
  timeout: number;
}

class CircuitBreaker {
  private state: CircuitState = CircuitState.CLOSED;
  private failureCount = 0;
  private successCount = 0;
  private lastFailureTime?: number;

  constructor(private options: CircuitBreakerOptions) {}

  async execute<T>(operation: () => Promise<T>): Promise<T> {
    if (this.state === CircuitState.OPEN) {
      if (this.shouldAttemptReset()) {
        this.state = CircuitState.HALF_OPEN;
        console.log('Circuit breaker transitioning to HALF_OPEN');
      } else {
        throw new CircuitOpenError('Circuit breaker is OPEN');
      }
    }

    try {
      const result = await operation();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  private onSuccess() {
    this.failureCount = 0;

    if (this.state === CircuitState.HALF_OPEN) {
      this.successCount++;

      if (this.successCount >= this.options.successThreshold) {
        this.state = CircuitState.CLOSED;
        this.successCount = 0;
        console.log('Circuit breaker CLOSED');
      }
    }
  }

  private onFailure() {
    this.failureCount++;
    this.lastFailureTime = Date.now();

    if (this.state === CircuitState.HALF_OPEN) {
      this.state = CircuitState.OPEN;
      console.log('Circuit breaker reopened from HALF_OPEN');
      return;
    }

    if (this.failureCount >= this.options.failureThreshold) {
      this.state = CircuitState.OPEN;
      console.log('Circuit breaker opened', {
        failureCount: this.failureCount,
        threshold: this.options.failureThreshold
      });
    }
  }

  private shouldAttemptReset(): boolean {
    return (
      this.lastFailureTime !== undefined &&
      Date.now() - this.lastFailureTime >= this.options.timeout
    );
  }

  getState(): CircuitState {
    return this.state;
  }
}

// Usage
const paymentServiceBreaker = new CircuitBreaker({
  failureThreshold: 5,
  successThreshold: 2,
  timeout: 60000 // 1 minute
});

async function processPayment(orderId: string) {
  return await paymentServiceBreaker.execute(async () => {
    return await paymentService.charge(orderId);
  });
}
```

## Dead Letter Queues

Dead Letter Queues (DLQs) store messages that cannot be processed successfully after multiple retry attempts.

### BullMQ Dead Letter Queue

```typescript
import { Queue, Worker } from 'bullmq';

// Main queue
const orderQueue = new Queue('orders', {
  connection: { host: 'localhost', port: 6379 },
  defaultJobOptions: {
    attempts: 3,
    backoff: {
      type: 'exponential',
      delay: 2000
    }
  }
});

// Dead letter queue
const dlqQueue = new Queue('orders-dlq', {
  connection: { host: 'localhost', port: 6379 }
});

// Worker with DLQ handling
const orderWorker = new Worker(
  'orders',
  async (job) => {
    // Process order
    await processOrder(job.data);
  },
  {
    connection: { host: 'localhost', port: 6379 }
  }
);

// Move failed jobs to DLQ
orderWorker.on('failed', async (job, error) => {
  if (!job) return;

  if (job.attemptsMade >= job.opts.attempts!) {
    console.log(`Moving job ${job.id} to DLQ after ${job.attemptsMade} attempts`);

    await dlqQueue.add('failed-order', {
      originalJobId: job.id,
      originalJobData: job.data,
      failureReason: error.message,
      failedAt: new Date().toISOString(),
      attempts: job.attemptsMade
    });
  }
});

// DLQ monitoring and reprocessing
const dlqWorker = new Worker(
  'orders-dlq',
  async (job) => {
    console.log('Processing DLQ job', job.data);

    // Manual inspection/reprocessing logic
    const { originalJobData, failureReason } = job.data;

    // Option 1: Alert operations team
    await alertOps({
      jobData: originalJobData,
      error: failureReason
    });

    // Option 2: Attempt manual fix and reprocess
    // const fixed = await attemptFix(originalJobData);
    // if (fixed) {
    //   await orderQueue.add('order', originalJobData);
    // }
  },
  {
    connection: { host: 'localhost', port: 6379 }
  }
);
```

### RabbitMQ Dead Letter Exchange

```typescript
async setupQueuesWithDLX() {
  // Declare dead letter exchange
  await this.channel.assertExchange('dlx', 'direct', { durable: true });

  // Declare DLQ
  await this.channel.assertQueue('orders-dlq', { durable: true });
  await this.channel.bindQueue('orders-dlq', 'dlx', 'orders-failed');

  // Declare main queue with DLX configuration
  await this.channel.assertQueue('orders', {
    durable: true,
    deadLetterExchange: 'dlx',
    deadLetterRoutingKey: 'orders-failed',
    messageTtl: 3600000 // 1 hour TTL
  });
}
```

### Poison Message Detection

```typescript
interface JobMetadata {
  attemptCount: number;
  firstAttempt: Date;
  lastError?: string;
  errorPattern?: string;
}

class PoisonMessageDetector {
  private errorPatterns = new Map<string, number>();

  async processJob(job: Job) {
    try {
      await this.executeJob(job);
      this.errorPatterns.delete(job.id!);
    } catch (error) {
      const errorSignature = this.getErrorSignature(error);

      // Track repeated error patterns
      const count = (this.errorPatterns.get(errorSignature) || 0) + 1;
      this.errorPatterns.set(errorSignature, count);

      if (this.isPoisonMessage(error, count)) {
        console.error('Poison message detected', {
          jobId: job.id,
          errorSignature,
          occurrences: count
        });

        // Immediately move to DLQ
        await this.moveToDLQ(job, error, 'poison_message');
        return;
      }

      throw error;
    }
  }

  private getErrorSignature(error: Error): string {
    // Create signature from error type and message
    return `${error.constructor.name}:${error.message.slice(0, 50)}`;
  }

  private isPoisonMessage(error: Error, occurrences: number): boolean {
    // Deterministic errors are likely poison messages
    const deterministicErrors = [
      'ValidationError',
      'TypeError',
      'SyntaxError'
    ];

    if (deterministicErrors.includes(error.constructor.name)) {
      return occurrences >= 2; // Fast detection
    }

    return occurrences >= 5; // Slower detection for other errors
  }

  private async moveToDLQ(job: Job, error: Error, reason: string) {
    // Implementation depends on queue system
  }
}
```

## Event-Driven Architecture

### Event Bus Pattern

```typescript
type EventHandler<T = any> = (data: T) => Promise<void>;

class EventBus {
  private handlers = new Map<string, EventHandler[]>();

  subscribe(eventType: string, handler: EventHandler) {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, []);
    }

    this.handlers.get(eventType)!.push(handler);
  }

  async publish(eventType: string, data: any) {
    const handlers = this.handlers.get(eventType) || [];

    // Parallel execution
    await Promise.all(
      handlers.map(handler =>
        handler(data).catch(error => {
          console.error(`Handler failed for ${eventType}`, error);
        })
      )
    );
  }

  async publishSequential(eventType: string, data: any) {
    const handlers = this.handlers.get(eventType) || [];

    // Sequential execution
    for (const handler of handlers) {
      try {
        await handler(data);
      } catch (error) {
        console.error(`Handler failed for ${eventType}`, error);
      }
    }
  }
}

// Usage
const eventBus = new EventBus();

// Subscribe to events
eventBus.subscribe('user.created', async (data) => {
  await emailService.sendWelcomeEmail(data.email);
});

eventBus.subscribe('user.created', async (data) => {
  await analyticsService.trackUserSignup(data);
});

// Publish events
class UserService {
  async createUser(userData: CreateUserData): Promise<User> {
    const user = await this.userRepository.create(userData);

    // Emit event
    await eventBus.publish('user.created', {
      userId: user.id,
      email: user.email,
      createdAt: user.createdAt
    });

    return user;
  }
}
```

### Event Sourcing Basics

Event Sourcing stores state changes as a sequence of events rather than current state.

```typescript
// Event types
interface DomainEvent {
  eventType: string;
  aggregateId: string;
  timestamp: Date;
  version: number;
}

interface AccountCreatedEvent extends DomainEvent {
  eventType: 'AccountCreated';
  accountId: string;
  initialBalance: number;
}

interface FundsDepositedEvent extends DomainEvent {
  eventType: 'FundsDeposited';
  accountId: string;
  amount: number;
}

interface FundsWithdrawnEvent extends DomainEvent {
  eventType: 'FundsWithdrawn';
  accountId: string;
  amount: number;
}

// Aggregate
class BankAccount {
  private id: string;
  private balance: number = 0;
  private version: number = 0;
  private uncommittedEvents: DomainEvent[] = [];

  constructor(id: string) {
    this.id = id;
  }

  // Command: Create account
  create(initialBalance: number) {
    const event: AccountCreatedEvent = {
      eventType: 'AccountCreated',
      aggregateId: this.id,
      accountId: this.id,
      initialBalance,
      timestamp: new Date(),
      version: this.version + 1
    };

    this.applyEvent(event);
    this.uncommittedEvents.push(event);
  }

  // Command: Deposit funds
  deposit(amount: number) {
    if (amount <= 0) {
      throw new ValidationError('Amount must be positive');
    }

    const event: FundsDepositedEvent = {
      eventType: 'FundsDeposited',
      aggregateId: this.id,
      accountId: this.id,
      amount,
      timestamp: new Date(),
      version: this.version + 1
    };

    this.applyEvent(event);
    this.uncommittedEvents.push(event);
  }

  // Command: Withdraw funds
  withdraw(amount: number) {
    if (amount <= 0) {
      throw new ValidationError('Amount must be positive');
    }

    if (amount > this.balance) {
      throw new ValidationError('Insufficient funds');
    }

    const event: FundsWithdrawnEvent = {
      eventType: 'FundsWithdrawn',
      aggregateId: this.id,
      accountId: this.id,
      amount,
      timestamp: new Date(),
      version: this.version + 1
    };

    this.applyEvent(event);
    this.uncommittedEvents.push(event);
  }

  // Apply event to update state
  private applyEvent(event: DomainEvent) {
    switch (event.eventType) {
      case 'AccountCreated':
        this.balance = (event as AccountCreatedEvent).initialBalance;
        break;
      case 'FundsDeposited':
        this.balance += (event as FundsDepositedEvent).amount;
        break;
      case 'FundsWithdrawn':
        this.balance -= (event as FundsWithdrawnEvent).amount;
        break;
    }
    this.version = event.version;
  }

  // Rebuild state from events
  static fromEvents(id: string, events: DomainEvent[]): BankAccount {
    const account = new BankAccount(id);
    events.forEach(event => account.applyEvent(event));
    return account;
  }

  getUncommittedEvents(): DomainEvent[] {
    return this.uncommittedEvents;
  }

  markEventsAsCommitted() {
    this.uncommittedEvents = [];
  }

  getBalance(): number {
    return this.balance;
  }
}

// Event Store
class EventStore {
  private events: Map<string, DomainEvent[]> = new Map();

  async saveEvents(aggregateId: string, events: DomainEvent[]) {
    const existingEvents = this.events.get(aggregateId) || [];
    this.events.set(aggregateId, [...existingEvents, ...events]);
  }

  async getEvents(aggregateId: string): Promise<DomainEvent[]> {
    return this.events.get(aggregateId) || [];
  }
}

// Usage
const eventStore = new EventStore();

// Create and use account
const account = new BankAccount('acc-123');
account.create(1000);
account.deposit(500);
account.withdraw(200);

// Save events
await eventStore.saveEvents('acc-123', account.getUncommittedEvents());
account.markEventsAsCommitted();

// Rebuild from events
const events = await eventStore.getEvents('acc-123');
const rebuiltAccount = BankAccount.fromEvents('acc-123', events);
console.log(rebuiltAccount.getBalance()); // 1300
```

### CQRS Pattern

Command Query Responsibility Segregation separates read and write operations.

```typescript
// Write Model (Commands)
interface CreateOrderCommand {
  userId: string;
  items: Array<{ productId: string; quantity: number }>;
}

class OrderCommandHandler {
  constructor(
    private orderRepository: OrderRepository,
    private eventBus: EventBus
  ) {}

  async handle(command: CreateOrderCommand): Promise<string> {
    // Validate
    if (command.items.length === 0) {
      throw new ValidationError('Order must have items');
    }

    // Create order
    const order = await this.orderRepository.create({
      userId: command.userId,
      items: command.items,
      status: 'pending'
    });

    // Publish event
    await this.eventBus.publish('order.created', {
      orderId: order.id,
      userId: order.userId,
      items: order.items
    });

    return order.id;
  }
}

// Read Model (Queries)
interface OrderSummary {
  orderId: string;
  userId: string;
  totalAmount: number;
  itemCount: number;
  status: string;
}

class OrderQueryHandler {
  constructor(private readDatabase: ReadDatabase) {}

  async getUserOrders(userId: string): Promise<OrderSummary[]> {
    // Query optimized read model
    return await this.readDatabase.query(
      'SELECT * FROM order_summaries WHERE user_id = ?',
      [userId]
    );
  }

  async getOrderDetails(orderId: string): Promise<OrderSummary> {
    return await this.readDatabase.queryOne(
      'SELECT * FROM order_summaries WHERE order_id = ?',
      [orderId]
    );
  }
}

// Read Model Projector
class OrderSummaryProjector {
  constructor(
    private readDatabase: ReadDatabase,
    private eventBus: EventBus
  ) {
    this.subscribeToEvents();
  }

  private subscribeToEvents() {
    this.eventBus.subscribe('order.created', async (event) => {
      await this.readDatabase.insert('order_summaries', {
        order_id: event.orderId,
        user_id: event.userId,
        total_amount: this.calculateTotal(event.items),
        item_count: event.items.length,
        status: 'pending'
      });
    });

    this.eventBus.subscribe('order.completed', async (event) => {
      await this.readDatabase.update(
        'order_summaries',
        { status: 'completed' },
        { order_id: event.orderId }
      );
    });
  }

  private calculateTotal(items: any[]): number {
    return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  }
}
```

## Best Practices Summary

### Job Queue Design
- ✅ Use durable queues for critical operations
- ✅ Set appropriate TTL on messages
- ✅ Configure dead letter queues
- ✅ Implement idempotent job handlers
- ✅ Use job priorities strategically
- ✅ Monitor queue depth and processing rates
- ✅ Set rate limits to protect downstream services

### Worker Configuration
- ✅ Match concurrency to available resources
- ✅ Implement graceful shutdown
- ✅ Use health checks and monitoring
- ✅ Set appropriate timeouts
- ✅ Log all job failures with context
- ✅ Use worker pools for CPU-intensive tasks

### Retry Strategy
- ✅ Use exponential backoff with jitter
- ✅ Set maximum retry limits
- ✅ Don't retry client errors (4xx)
- ✅ Implement circuit breakers for external dependencies
- ✅ Distinguish transient from permanent failures
- ✅ Log retry attempts with context

### Dead Letter Queue
- ✅ Monitor DLQ size and age
- ✅ Alert on DLQ message arrival
- ✅ Implement DLQ reprocessing workflow
- ✅ Detect poison messages early
- ✅ Store failure metadata
- ✅ Set retention policies

### Event-Driven Design
- ✅ Use consistent event naming conventions
- ✅ Include correlation IDs
- ✅ Make events immutable
- ✅ Version event schemas
- ✅ Handle duplicate events (idempotency)
- ✅ Monitor event processing lag

## Quick Reference

### Queue Comparison

| Feature | BullMQ (Redis) | RabbitMQ | AWS SQS |
|---------|---------------|----------|---------|
| Language | TypeScript/JS | Any | Any |
| Persistence | Redis AOF/RDB | Durable queues | Fully managed |
| Priority | Yes | Yes | Limited |
| Delay | Yes | Yes (plugins) | Yes |
| DLQ | Manual | Native | Native |
| Scalability | Horizontal | Horizontal | Unlimited |
| Cost | Redis hosting | Self-hosted/managed | Pay per request |

### Retry Decision Matrix

| Error Type | Retry? | Strategy |
|------------|--------|----------|
| Network timeout | Yes | Exponential backoff |
| 500 Server Error | Yes | Exponential backoff |
| 503 Service Unavailable | Yes | Exponential backoff + circuit breaker |
| 429 Rate Limit | Yes | Respect Retry-After header |
| 400 Bad Request | No | Fix and resubmit |
| 401 Unauthorized | No | Refresh credentials |
| 404 Not Found | No | Verify resource exists |
| Validation Error | No | Fix input data |

### Common Pitfalls

- ❌ Missing job idempotency (duplicate processing)
- ❌ No maximum retry limit (infinite retries)
- ❌ Retrying non-transient errors (wasted resources)
- ❌ Missing graceful shutdown (lost jobs)
- ❌ No DLQ monitoring (silent failures)
- ❌ Blocking event handlers (slow processing)
- ❌ Missing correlation IDs (difficult debugging)
- ❌ No circuit breakers (cascading failures)

## Summary

Async processing patterns enable scalable, resilient backend systems. Key principles:

1. **Job Queues**: Use durable message queues (BullMQ, RabbitMQ, SQS) for reliable async processing
2. **Background Workers**: Configure worker pools with appropriate concurrency and graceful shutdown
3. **Retry Strategies**: Implement exponential backoff with jitter and circuit breakers
4. **Dead Letter Queues**: Monitor and process failed messages systematically
5. **Event-Driven Architecture**: Decouple services through events, consider Event Sourcing and CQRS for complex domains
