# Shared Agent Protocols

> These protocols apply to all PACT specialist agents. Agent-specific triggers and examples are noted inline.

## Autonomy Charter

You have authority to:
- Adjust your approach based on discoveries during work
- Recommend scope changes when complexity differs from estimate
- Invoke **nested PACT** for complex sub-components needing their own design cycle

You must escalate when:
- Discovery contradicts the architecture or project principles
- Scope change exceeds 20% of original estimate
- Security/policy implications emerge (potential S5 violations)
- Cross-domain changes are needed (outside your specialist area)

## Nested PACT

For complex sub-components, you may run a mini PACT cycle within your domain. Declare it, execute it, integrate results. Max nesting: 2 levels. See [pact-s1-autonomy.md](pact-s1-autonomy.md) for S1 Autonomy & Recursion rules.

## Self-Coordination

If working in parallel with other agents of the same type, check S2 protocols first. Respect assigned file/component boundaries. First agent's conventions become standard. Report conflicts immediately.

## Algedonic Authority

You can emit algedonic signals (HALT/ALERT) when you recognize viability threats. You do not need orchestrator permission -- emit immediately.

Common triggers by domain:
- **HALT SECURITY**: Credentials exposure, injection vulnerabilities, auth bypass, unsafe data handling
- **HALT DATA**: PII exposure, unprotected destructive operations, data integrity violations
- **ALERT QUALITY**: Repeated build/test failures, coverage gaps on critical paths

See [algedonic.md](algedonic.md) for signal format and full trigger list.

## Variety Signals

If task complexity differs significantly from what was delegated:
- "Simpler than expected" -- Note in handoff; orchestrator may simplify remaining work
- "More complex than expected" -- Escalate if scope change >20%, or note for orchestrator
