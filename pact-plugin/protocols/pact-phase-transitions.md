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

Coders provide handoff summaries to the orchestrator, who passes them to the test engineer. Handoff includes:
- What was implemented
- Key decisions and assumptions
- Areas of uncertainty (where bugs might hide—test engineer should prioritize these)

**This is context, not prescription.** The test engineer decides what and how to test.

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

