# PACT Memory Usage Patterns

This document provides patterns and examples for effective use of the PACT Memory
skill across different scenarios.

## Pattern 1: Phase Completion Memory

Save context after completing each PACT phase to preserve learnings.

### After Prepare Phase

```python
memory.save({
    "context": "Researching authentication approaches for API gateway",
    "goal": "Evaluate OAuth2 vs JWT for microservices auth",
    "lessons_learned": [
        "OAuth2 adds complexity but better for third-party integrations",
        "JWT works well for internal service-to-service auth",
        "Need to consider token revocation strategy early"
    ],
    "decisions": [
        {
            "decision": "Use JWT for internal services, OAuth2 for external",
            "rationale": "Balances simplicity with flexibility",
            "alternatives": ["OAuth2 everywhere", "Custom token system"]
        }
    ],
    "entities": [
        {"name": "APIGateway", "type": "component"},
        {"name": "AuthService", "type": "service"}
    ]
})
```

### After Architect Phase

```python
memory.save({
    "context": "Designing authentication microservice architecture",
    "goal": "Create scalable auth service with token management",
    "active_tasks": [
        {"task": "Define API contracts", "status": "completed"},
        {"task": "Design database schema", "status": "completed"},
        {"task": "Plan caching strategy", "status": "in_progress"}
    ],
    "decisions": [
        {
            "decision": "Use Redis for token blacklist",
            "rationale": "Fast TTL, distributed, already in stack",
            "alternatives": ["PostgreSQL with TTL", "In-memory cache"]
        },
        {
            "decision": "Separate refresh token table",
            "rationale": "Different lifecycle, rotation tracking",
            "alternatives": ["Single token table with type field"]
        }
    ],
    "entities": [
        {"name": "TokenBlacklist", "type": "component", "notes": "Redis-backed"},
        {"name": "RefreshTokenStore", "type": "table"}
    ]
})
```

### After Code Phase

```python
memory.save({
    "context": "Implemented JWT authentication with refresh tokens",
    "goal": "Complete auth service implementation",
    "lessons_learned": [
        "PyJWT requires explicit algorithm specification",
        "Redis SCAN is safer than KEYS for production",
        "Refresh token rotation prevents replay attacks"
    ],
    "decisions": [
        {
            "decision": "Use sliding window for rate limiting",
            "rationale": "Smoother experience than fixed window",
            "alternatives": ["Fixed window", "Token bucket"]
        }
    ],
    "entities": [
        {"name": "JWTHandler", "type": "class"},
        {"name": "RateLimiter", "type": "middleware"}
    ]
})
```

### After Test Phase

```python
memory.save({
    "context": "Completed authentication service testing",
    "goal": "Ensure auth service reliability and security",
    "lessons_learned": [
        "Mock Redis for unit tests, real Redis for integration",
        "Time-based tests need freezegun or similar",
        "Security tests should cover token tampering scenarios"
    ],
    "decisions": [
        {
            "decision": "Add chaos testing for Redis failures",
            "rationale": "Auth must gracefully degrade",
            "alternatives": ["Skip chaos testing for MVP"]
        }
    ]
})
```

## Pattern 2: Blocker Documentation

When hitting a blocker, save context for future reference.

```python
memory.save({
    "context": "Blocked on sqlite-lembed installation on M1 Mac",
    "goal": "Enable local embeddings for memory skill",
    "lessons_learned": [
        "sqlite-lembed requires Rosetta 2 on M1",
        "Alternative: use sentence-transformers as fallback",
        "Binary distribution needs architecture-specific builds"
    ],
    "decisions": [
        {
            "decision": "Implement fallback chain for embeddings",
            "rationale": "Graceful degradation over hard failure"
        }
    ],
    "active_tasks": [
        {"task": "Add sentence-transformers fallback", "status": "pending", "priority": "high"},
        {"task": "Test cross-platform compatibility", "status": "pending"}
    ]
})
```

## Pattern 3: Search Before Starting

Query for relevant context before beginning work.

```python
# Starting work on authentication
results = memory.search("authentication security tokens")

for mem in results:
    print(f"\n=== Past Context ===")
    print(f"Context: {mem.context}")
    print(f"Goal: {mem.goal}")

    if mem.lessons_learned:
        print(f"\nLessons:")
        for lesson in mem.lessons_learned:
            print(f"  - {lesson}")

    if mem.decisions:
        print(f"\nDecisions:")
        for dec in mem.decisions:
            print(f"  - {dec.decision}")
            if dec.rationale:
                print(f"    Rationale: {dec.rationale}")
```

## Pattern 4: File-Based Context

Search for memories related to files you're working on.

```python
# Get context for the file you're editing
current_file = "src/auth/token_manager.py"
related = memory.search_by_file(current_file)

for mem in related:
    print(f"Previous work on related files:")
    print(f"  Context: {mem.context}")
    print(f"  Files: {', '.join(mem.files)}")
```

## Pattern 5: Decision Tracking

Use memories as a decision log across the project.

```python
# Search for past decisions on a topic
decisions = memory.search("caching strategy decisions")

# Compile decision history
for mem in decisions:
    if mem.decisions:
        print(f"\n{mem.created_at}: {mem.context}")
        for dec in mem.decisions:
            print(f"  Decision: {dec.decision}")
            print(f"  Rationale: {dec.rationale}")
            if dec.alternatives:
                print(f"  Alternatives: {', '.join(dec.alternatives)}")
```

## Pattern 6: Entity Reference

Build up knowledge about system components.

```python
# Search for memories mentioning a component
auth_memories = memory.search("AuthService")

# Compile entity knowledge
entity_notes = {}
for mem in auth_memories:
    for entity in mem.entities:
        if entity.name not in entity_notes:
            entity_notes[entity.name] = {
                "type": entity.type,
                "notes": []
            }
        if entity.notes:
            entity_notes[entity.name]["notes"].append(entity.notes)

# Display accumulated knowledge
for name, info in entity_notes.items():
    print(f"{name} ({info['type']})")
    for note in info["notes"]:
        print(f"  - {note}")
```

## Pattern 7: Session Wrap-Up

Save comprehensive session summary before ending.

```python
# Get files modified in this session
tracked_files = memory.get_tracked_files()

memory.save({
    "context": "Session wrap-up: Authentication feature implementation",
    "goal": "Complete JWT auth with refresh tokens",
    "active_tasks": [
        {"task": "Add unit tests for TokenManager", "status": "completed"},
        {"task": "Implement rate limiting middleware", "status": "completed"},
        {"task": "Add chaos tests", "status": "pending", "priority": "medium"}
    ],
    "lessons_learned": [
        "Token rotation requires careful state management",
        "Redis connection pooling essential for performance",
        "Always log auth failures with correlation IDs"
    ],
    "decisions": [
        {
            "decision": "Defer chaos testing to next sprint",
            "rationale": "Core functionality complete, need stakeholder review"
        }
    ],
    "entities": [
        {"name": "TokenManager", "type": "class", "notes": "Core JWT handling"},
        {"name": "RateLimiter", "type": "middleware", "notes": "Uses sliding window"},
        {"name": "AuthService", "type": "service", "notes": "Main entry point"}
    ]
},
files=tracked_files,
include_tracked=False  # We're explicitly providing files
)
```

## Pattern 8: Incremental Learning

Update memories as understanding evolves.

```python
# Get existing memory
mem = memory.get("abc123")

# Add new lessons learned
existing_lessons = mem.lessons_learned if mem.lessons_learned else []
new_lessons = existing_lessons + [
    "Redis cluster mode requires different connection handling",
    "Sentinel provides better HA than standalone Redis"
]

memory.update("abc123", {
    "lessons_learned": new_lessons,
    "entities": mem.entities + [
        {"name": "RedisSentinel", "type": "component", "notes": "HA setup"}
    ]
})
```

## Anti-Patterns to Avoid

### Too Vague

```python
# BAD - no actionable information
memory.save({
    "context": "Working on auth",
    "lessons_learned": ["Things were hard"]
})
```

### Too Granular

```python
# BAD - noise in the memory system
memory.save({
    "context": "Fixed typo in variable name",
    "lessons_learned": ["Check spelling"]
})
```

### Missing Rationale

```python
# BAD - decision without context
memory.save({
    "decisions": [
        {"decision": "Use Redis"}  # Why? What alternatives?
    ]
})
```

### No Entity Links

```python
# BAD - hard to connect to related work
memory.save({
    "context": "Refactored the authentication service",
    # Missing: which components? what files?
})
```

## Best Practices Summary

1. **Be Specific**: Include concrete details that will be useful later
2. **Capture Rationale**: Document why, not just what
3. **Link Entities**: Reference components for graph connectivity
4. **Include Alternatives**: Record options that were considered
5. **Save at Transitions**: Phase completions, blockers, decisions
6. **Search First**: Check for relevant context before starting
7. **Update Incrementally**: Add to existing memories as you learn
