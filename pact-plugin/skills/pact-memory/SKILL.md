---
name: pact-memory
description: |
  Persistent memory for PACT agents. Save context, goals, lessons learned,
  decisions, and entities. Semantic search across sessions.
  Use when: saving session context, recalling past decisions, searching lessons.
  Triggers: memory, save memory, search memory, lessons learned, remember, recall
---

# PACT Memory Skill

Persistent memory system for PACT framework agents. Store and retrieve context,
goals, lessons learned, decisions, and entities across sessions with semantic search.

## Overview

The PACT Memory skill provides:
- **Rich Memory Objects**: Store context, goals, tasks, lessons, decisions, and entities
- **Semantic Search**: Find relevant memories using natural language queries
- **Graph-Enhanced Retrieval**: Memories linked to files are boosted when working on related files
- **Session Tracking**: Automatic file tracking and session context
- **Cross-Session Learning**: Memories persist across sessions for cumulative knowledge

## Quick Start

```python
from pact_memory.scripts import PACTMemory

# Initialize
memory = PACTMemory()

# Save a memory
memory_id = memory.save({
    "context": "Implementing user authentication",
    "goal": "Add JWT refresh token support",
    "lessons_learned": [
        "Redis INCR is atomic - perfect for rate limiting",
        "Always validate refresh token rotation"
    ],
    "decisions": [
        {
            "decision": "Use Redis for token blacklist",
            "rationale": "Fast TTL support, distributed access"
        }
    ],
    "entities": [
        {"name": "AuthService", "type": "component"},
        {"name": "TokenManager", "type": "class"}
    ]
})

# Search memories
results = memory.search("rate limiting tokens")
for mem in results:
    print(f"Context: {mem.context}")
    print(f"Lessons: {mem.lessons_learned}")

# List recent memories
recent = memory.list(limit=10)
```

## Memory Structure

Each memory can contain:

| Field | Type | Description |
|-------|------|-------------|
| `context` | string | Current working context description |
| `goal` | string | What you're trying to achieve |
| `active_tasks` | list | Tasks with status and priority |
| `lessons_learned` | list | What worked or didn't work |
| `decisions` | list | Decisions with rationale and alternatives |
| `entities` | list | Referenced components, services, modules |
| `files` | list | Associated file paths (auto-linked) |
| `project_id` | string | Auto-detected from environment |
| `session_id` | string | Auto-detected from environment |

### Task Format
```python
{"task": "Implement token refresh", "status": "in_progress", "priority": "high"}
```

### Decision Format
```python
{
    "decision": "Use Redis for caching",
    "rationale": "Fast, supports TTL natively",
    "alternatives": ["Memcached", "In-memory LRU"]
}
```

### Entity Format
```python
{"name": "AuthService", "type": "component", "notes": "Handles all auth flows"}
```

## API Reference

### PACTMemory Class

```python
class PACTMemory:
    def save(self, memory: dict, files: list = None) -> str
    def search(self, query: str, current_file: str = None, limit: int = 5) -> list[MemoryObject]
    def get(self, memory_id: str) -> MemoryObject | None
    def update(self, memory_id: str, updates: dict) -> bool
    def delete(self, memory_id: str) -> bool
    def list(self, limit: int = 20, session_only: bool = False) -> list[MemoryObject]
    def get_status(self) -> dict
```

### Convenience Functions

```python
from pact_memory.scripts import save_memory, search_memory, list_memories_simple

# Quick save
memory_id = save_memory({
    "context": "Bug fix",
    "lessons_learned": ["Check null values first"]
})

# Quick search
results = search_memory("authentication")

# Quick list
recent = list_memories_simple(10)
```

## Search Capabilities

### Semantic Search
Uses embeddings to find semantically similar memories. Requires either:
- sqlite-lembed with GGUF model (preferred)
- sentence-transformers (fallback)

### Graph-Enhanced Search
When searching while working on a file, memories linked to:
- The current file
- Files imported by/importing the current file
- Files modified in the same session

...are boosted in ranking.

### Keyword Fallback
If embeddings are unavailable, falls back to substring matching across
context, goal, lessons_learned, and decisions fields.

## Setup

### Dependencies

```bash
# Required for database
pip install sqlite-vec

# For local embeddings (recommended)
pip install sqlite-lembed

# Alternative embedding backend
pip install sentence-transformers
```

### Model Download

The skill uses a 24MB GGUF model for embeddings. Download automatically:

```python
from pact_memory.scripts.setup_memory import ensure_initialized
ensure_initialized(download_model_if_missing=True)
```

Or manually:
```bash
python -m pact_memory.scripts.setup_memory model
```

### Check Status

```python
from pact_memory.scripts.setup_memory import get_setup_status
status = get_setup_status()
print(f"Semantic search: {'Available' if status['can_use_semantic_search'] else 'Unavailable'}")
```

## Storage

Memories are stored in `~/.claude/memory/memory.db` using SQLite with:
- WAL mode for crash safety
- Vector extensions for semantic search
- Graph tables for file relationships

## Best Practices

1. **Save at Phase Completion**: Save memories after completing PACT phases
2. **Include Lessons**: Always capture what worked and what didn't
3. **Document Decisions**: Record rationale and alternatives considered
4. **Link Entities**: Reference components for better graph connectivity
5. **Search Before Acting**: Check for relevant past context before starting work

## Integration with PACT

The memory skill integrates with PACT phases:

- **Prepare**: Search for relevant past context before starting
- **Architect**: Record design decisions with rationale
- **Code**: Save lessons learned during implementation
- **Test**: Document test strategies and findings

See `references/memory-patterns.md` for detailed usage patterns.
