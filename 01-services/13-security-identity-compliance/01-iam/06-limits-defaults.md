# IAM limits and defaults

Values verified against the IAM quotas documentation. Split by what you must remember for the exam versus operational detail.

> [!IMPORTANT]
> The "must remember" table below is the exam-critical subset. The quota table is "good to know" — the exam rarely asks for an exact quota ceiling, and when it does the value is usually in the question stem. What it does test are the behavioral defaults: **role session duration (1 hour by default, up to 12 hours maximum)** and that **IAM is global** (a role is visible and usable from every Region, unlike most resources). Commit those two rather than the quota table.

## Must remember

| Item | Value |
|------|-------|
| Policy evaluation default | implicit deny — no allow, no access |
| Explicit deny vs allow | deny wins |
| Role default session duration | 1 hour |
| Role maximum session duration | 12 hours |
| IAM scope | global (account-wide, not regional) |
| Permissions boundary / SCP effect | intersection (caps, never grants) |

## Quotas (defaults, adjustable)

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

| Item | Limit |
|------|-------|
| Customer managed policy size | 6,144 chars |
| Inline policy — user | 2,048 chars |
| Inline policy — role | 10,240 chars |
| Inline policy — group | 5,120 chars |
| User / role name | 64 chars |
| Group name | 128 chars |
| Path | 512 chars |

## STS request quota

600 requests/second per account per Region for `AssumeRole`, `GetCallerIdentity`, `GetSessionToken`, `GetFederationToken`, `DecodeAuthorizationMessage`, and `GetAccessKeyInfo`. Service-principal role assumptions (EC2, Lambda) do not consume this quota.

## Good to know

- White space does not count against policy size limits.
- User, group, and role names are case-insensitive and must be unique within the account.
- Account alias: 3–63 characters, lowercase, DNS naming.

## Sources

- AWS — *IAM and AWS STS quotas*. https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_iam-quotas.html
