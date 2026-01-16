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

CODE phase produces decision log(s) at `docs/decision-logs/{feature}-{domain}.md`:
- `{feature}` = kebab-case feature name (match branch slug when available)
- `{domain}` = `backend`, `frontend`, or `database`
- Example: `user-authentication-backend.md`

**Decision log contents:**
```markdown
# Decision Log: {Feature Name}

## Summary
Brief description of what was implemented.

## Key Decisions
- Decision: rationale

## Assumptions
- Assumption made and why

## Known Limitations
- What wasn't handled and why

## Areas of Uncertainty
- Where bugs might hide, tricky parts

## Integration Context
- Depends on: [services, modules]
- Consumed by: [downstream code]

## Smoke Tests
- What was verified (compile, run, happy path)
```

**This is context, not prescription.** The test engineer decides what and how to test. The decision log helps inform that judgment.

**If decision log is missing**: For `/PACT:orchestrate`, request it from the orchestrator. For `/PACT:comPACT` (light ceremony), proceed with test design based on code analysis—decision logs are optional.

### TEST Decision Log

TEST phase produces its own decision log at `docs/decision-logs/{feature}-test.md`:

```markdown
# Test Decision Log: {Feature Name}

## Testing Approach
What strategy was chosen and why.

## Areas Prioritized
Referenced CODE logs: [list files read, e.g., `user-auth-backend.md`]
Focus areas based on their "areas of uncertainty".

## Edge Cases Identified
What boundary conditions and error scenarios were tested.

## Coverage Notes
What coverage was achieved, any significant gaps.

## What Was NOT Tested
Explicit scope boundaries and rationale (complexity, time, low risk).

## Known Issues
Flaky tests, environment dependencies, or unresolved concerns.
```

Focus on the **"why"** not the "what" — test code shows what was tested, the decision log explains the reasoning.

For `/PACT:comPACT` (light ceremony), this is optional.

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

