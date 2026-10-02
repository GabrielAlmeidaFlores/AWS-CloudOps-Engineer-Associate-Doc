# IAM quick review

> [!NOTE]
> This is the last thing you read before the exam — a one-page gate. If any line below isn't instantly obvious, go back to the source document rather than skimming: evaluation logic lives in `01-concepts.md`, the traps in `05-exam-traps.md`, and the numbers in `06-limits-defaults.md`. The goal is that every item here is recall, not re-reading.

## Non-negotiables

- **Explicit deny wins.** A `Deny` overrides every `Allow`.
- **Implicit deny** is the default: no allow means no access.
- **Union:** identity-based + resource-based policies. **Intersection:** permissions boundary, SCP, RCP.
- **Role ≠ user.** Roles are assumed, return temporary STS credentials, and are the right choice for workloads and cross-account.
- **IAM is global.**

## Policy types

- Identity-based → attaches to user/group/role.
- Resource-based → attaches to a resource; needs a `Principal`.
- Permissions boundary → caps a user/role.
- SCP → caps an account (Organizations).

## Role anatomy

- **Trust policy** = who can assume it.
- **Permissions policy** = what it can do.

## Key numbers

- Role session: default 1 hour, max 12 hours.
- Roles per account: 1,000 default.
- Customer managed policies per account: 1,500 default.
- Managed policy size: 6,144 chars.

## Troubleshooting levers

Policy simulator → CloudTrail → Access Analyzer → `DecodeAuthorizationMessage`.

## The one-liner

An action is allowed only if some policy allows it **and** nothing denies it **and** no boundary/SCP caps it.

## Sources

- Full references live in the per-topic documents: `01-concepts.md`, `03-troubleshooting.md`, and `06-limits-defaults.md`.
