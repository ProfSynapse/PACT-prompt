## Phase Handoffs

**On completing any phase, state**:
1. What you produced (with file paths)
2. Key decisions made
3. What the next agent needs to know

Keep it brief. No templates required.

---

## Test Engagement

| Test Type | Owner |
|-----------|-------|
| Smoke tests | Coders (minimal verification) |
| Unit tests | Test Engineer |
| Integration tests | Test Engineer |
| E2E tests | Test Engineer |

**Coders**: Your work isn't done until smoke tests pass. Smoke tests verify: "Does it compile? Does it run? Does the happy path not crash?" No comprehensive testing—that's TEST phase work.

**Test Engineer**: Engage after Code phase. You own ALL substantive testing: unit tests, integration, E2E, edge cases, adversarial testing. Target 80%+ meaningful coverage of critical paths.

### CODE → TEST Handoff

Coders provide handoff summaries to the orchestrator, who passes them to the test engineer.

**Handoff Format**:
```
HANDOFF:
1. Produced: {files created or modified, with paths}
2. Key context: {decisions made, patterns used, assumptions}
3. Areas of uncertainty: {where bugs might hide, tricky parts}
4. Open questions: {anything unresolved that needs attention}
```

Note: All four items are required, even if some are "None." This confirms you considered each aspect rather than forgot or omitted it.

**Example**:
```
HANDOFF:
1. Produced: Created `src/auth/token-manager.ts`, modified `src/middleware/auth.ts`
2. Key context: Used singleton pattern for token manager; assumed token refresh window of 30s before expiry; modified auth middleware to use new manager
3. Areas of uncertainty: Token refresh race condition with concurrent requests may yield stale tokens; clock skew handling assumed <5s drift
4. Open questions: Should refresh tokens be stored in httpOnly cookies?
```

**Test Engineer Response**:
- HIGH uncertainty areas require explicit test cases (mandatory)
- If skipping a flagged area, document the rationale
- Report findings using the Signal Output System (GREEN/YELLOW/RED)

**This is context, not prescription.** The test engineer decides *how* to test, but flagged HIGH uncertainty areas must be addressed.

---

## Cross-Cutting Concerns

Before completing any phase, consider:
- **Security**: Input validation, auth, data protection
- **Performance**: Query efficiency, caching
- **Accessibility**: WCAG, keyboard nav (frontend)
- **Observability**: Logging, error tracking

Not a checklist—just awareness.

---

## Architecture Review (Optional)

For complex features, before Code phase:
- Coders quickly validate architect's design is implementable
- Flag blockers early, not during implementation

Skip for simple features or when "just build it."

---

