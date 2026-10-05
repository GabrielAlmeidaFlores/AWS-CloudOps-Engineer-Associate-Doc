# IAM limits and defaults

Values verified against the IAM quotas documentation. The behavioral defaults matter most; quota ceilings rarely appear on the exam.

> [!IMPORTANT]
> The "must remember" table below is the exam-critical subset. The quota table is "good to know", the exam rarely asks for an exact quota ceiling, and when it does the value is usually in the question stem. What it does test are the behavioral defaults: **role session duration (1 hour by default, up to 12 hours maximum)** and that **IAM is global** (a role is visible and usable from every Region, unlike most resources). Commit those two rather than the quota table.

## Must remember

| Item | Value | Why it matters |
|------|-------|----------------|
| Policy evaluation default | Implicit deny | No allow means no access, IAM has no implicit allow |
| Explicit deny vs allow | Deny wins | A single `Deny` overrides every `Allow` |
| Role default session duration | 1 hour | What an assumption gets if you do not request more |
| Role maximum session duration | 12 hours | The cap, set per role; requests above it fail |
| IAM scope | Global, account-wide | A role is usable from every Region, not just where it was made |
| Permissions boundary / SCP effect | Intersection | They cap, never grant |

## Quotas (defaults, adjustable)

Defaults are per account and most can be raised through Service Quotas.

| Resource | Default | Max |
|----------|---------|-----|
| Roles per account | 1,000 | 10,000 |
| Customer managed policies per account | 1,500 | 10,000 |
| Groups per account | 300 | 500 |
| Instance profiles per account | 1,000 | 10,000 |
| Managed policies attached per role | 20 | 25 |
| Managed policies attached per user | 10 | 20 |
| Role trust policy length | 2,048 chars | 8,192 chars |

## Size limits (not adjustable)

These caps are fixed. The inline-policy limits differ by entity type, which is a detail candidates overlook.

| Item | Limit |
|------|-------|
| Customer managed policy size | 6,144 chars |
| Inline policy: user | 2,048 chars |
| Inline policy: role | 10,240 chars |
| Inline policy: group | 5,120 chars |
| User / role name | 64 chars |
| Group name | 128 chars |
| Path | 512 chars |

## STS request quota

AWS STS allows 600 requests per second per account per Region across `AssumeRole`, `GetCallerIdentity`, `GetSessionToken`, `GetFederationToken`, `DecodeAuthorizationMessage`, and `GetAccessKeyInfo`. Role assumptions by AWS service principals (EC2, Lambda) do not consume this quota, which is why a service-heavy account rarely hits it.

## Good to know

- White space does not count against policy size limits, so a policy can be reformatted for readability without changing its size.
- User, group, and role names are case-insensitive and must be unique within the account.
- An account alias is 3–63 characters, lowercase, and must follow DNS naming rules.

## Sources

- AWS: *IAM and AWS STS quotas*. https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_iam-quotas.html
