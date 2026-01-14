# Environment Model: {Feature/Project}

> **Created**: {YYYY-MM-DD}
> **Variety Score**: {score}
> **Last Updated**: {YYYY-MM-DD}

---

## Tech Stack Assumptions

- **Language**: {language/version}
- **Framework**: {framework/version}
- **Key dependencies**:
  - {dependency}: {version expectation}
  - {dependency}: {version expectation}

---

## External Dependencies

| Dependency | Type | Expected Behavior | Last Verified |
|------------|------|-------------------|---------------|
| {API/Service} | API | {What we assume about availability, version, response format} | {Date} |
| {Database} | Data | {Schema assumptions, access patterns} | {Date} |

---

## Constraints

### Performance
- Expected load: {requests/sec, concurrent users}
- Latency requirements: {p95 < Xms}
- Resource limits: {memory, CPU, storage}

### Security
- Compliance: {GDPR, SOC2, HIPAA, etc.}
- Auth requirements: {OAuth, JWT, API keys}
- Data sensitivity: {PII handling, encryption requirements}

### Time
- Deadline: {date or "none"}
- Phase durations: {any time constraints per phase}

### Resources
- Team capacity: {who's available, expertise levels}
- Compute limits: {cloud quotas, local resources}

---

## Unknowns (Acknowledged Gaps)

- [ ] {Question that needs answering}
- [ ] {Area of uncertainty}
- [ ] {Risk that needs monitoring}

---

## Invalidation Triggers

| If This Happens... | Then... |
|--------------------|---------|
| {assumption X} proves false | {response: revisit ARCHITECT, change approach, escalate} |
| {constraint Y} changes | {response} |
| {dependency Z} unavailable | {response} |

---

## Model Updates

| Date | Update | Trigger |
|------|--------|---------|
| {Date} | Initial model | PREPARE phase |
| | | |
