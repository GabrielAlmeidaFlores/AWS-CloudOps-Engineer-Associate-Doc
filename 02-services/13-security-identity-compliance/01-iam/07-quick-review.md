# IAM quick review

> [!NOTE]
> This is the last thing you read before the exam, a one-page gate. If any line below isn't instantly obvious, go back to the source document rather than skimming: evaluation logic lives in `01-concepts.md`, the traps in `05-exam-traps.md`, and the numbers in `06-limits-defaults.md`. The goal is that every item here is recall, not re-reading.

## Non-negotiables

- **Explicit deny wins.** A `Deny` in any applicable policy overrides every `Allow` in every other policy, identity, resource, boundary, or SCP. This single rule decides most "why is access denied" questions.
- **Implicit deny is the default.** If no policy explicitly allows an action; it is denied. IAM has no implicit allow.
- **Union vs intersection.** Identity-based and resource-based policies combine as a **union** (either can allow. Permissions boundaries and SCPs are **intersections**) they can only remove access, never add it.
- **A role is not a user.** A role is assumed and returns short-lived STS credentials; it has no password and no long-lived keys. It is the correct choice for workloads and cross-account access.
- **IAM is global, not regional.** A user, role, or policy exists account-wide and is usable from every Region, unlike most AWS resources.

## Policy types

- **Identity-based policy**, attaches to a user, group, or role and defines what that identity can do.
- **Resource-based policy**, attaches to a resource (S3 bucket, KMS key, SQS queue) and includes a `Principal` element naming who is granted access.
- **Permissions boundary**, attaches to a user or role and caps its maximum possible permissions.
- **SCP**, attaches to an account or OU in Organizations and caps every principal in that account, including the root user.

## Role anatomy

Every role carries two policies that answer two different questions:

- **Trust policy**, *who may assume the role* (the principal). An EC2 role's trust policy names `ec2.amazonaws.com`.
- **Permissions policy**, *what the assumed session may do*.

Mixing them up is the classic cross-account failure: an access-denied on `sts:AssumeRole` is a trust-policy problem; a later API call failing is a permissions-policy problem.

## Key numbers

- **Role session duration:** 1 hour by default, configurable up to 12 hours.
- **Roles per account:** 1,000 default (10,000 max).
- **Customer managed policies per account:** 1,500 default (10,000 max).
- **Customer managed policy size:** 6,144 characters.

## Troubleshooting levers

Start with the **IAM policy simulator** (evaluates a policy without a live call), then **CloudTrail** (what actually happened), then **IAM Access Analyzer** (external exposure), and decode an authorization failure message with `DecodeAuthorizationMessage`.

## The one-liner

An action is allowed only if some policy allows it **and** nothing denies it **and** no boundary or SCP caps it.

## Sources

- Full references live in the per-topic documents: `01-concepts.md`, `03-troubleshooting.md`, and `06-limits-defaults.md`.
