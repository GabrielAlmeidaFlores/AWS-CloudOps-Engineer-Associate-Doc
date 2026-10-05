# IAM security

> [!IMPORTANT]
> Permissions boundaries and SCPs never *grant* access — they only narrow it. Each is an intersection: the effective permission is what the identity policy allows *and* the boundary or SCP does not exclude. So if a scenario asks how to give a user more access, a boundary or SCP is the wrong answer; adding one can only remove access that was already allowed. Candidates repeatedly pick "add a permissions boundary" to fix an over-permissioned user, when the boundary restricts rather than expands.

## Root user protection

The root user — the email address and password that created the account — has unrestricted access, including billing and account closure, and cannot be limited by IAM policies or SCPs. Protect it before anything else:

- Enable MFA on the root user immediately.
- Delete any root access keys; the root user should have none.
- Reserve it for the few tasks that require it, such as changing the account name or closing the account.
- Do all day-to-day work with IAM identities or federation.

## Least privilege

Grant only the actions and resources a principal needs.

- Role over a long-lived user for any workload or cross-account access — a role yields temporary credentials, so a leaked credential expires on its own.
- Resource-based policies where the resource should be the point of control (S3 buckets, KMS keys, SQS queues), because access then travels with the resource rather than the caller.
- Condition keys to narrow a broad action instead of adding a `Deny` (`aws:RequestedRegion`, `aws:SourceVpce`, `aws:PrincipalOrgID`).
- Start from no permissions and add what is required, rather than starting from `*` and pruning. IAM Access Analyzer generates a policy from CloudTrail-observed access, which is a defensible starting point.

## MFA and password policy

- **MFA** on the root user and on every human user. Virtual MFA (TOTP) or hardware (U2F) device. MFA protects console sign-in; it does not protect programmatic access keys, which is why human users should normally assume a role instead of holding keys.
- **Password policy** is account-wide: minimum length, complexity, rotation, and reuse prevention. There is exactly one password policy per account, so it applies to every IAM user and cannot be set per user.

## Credential report

The IAM credential report is a downloadable CSV that lists every user and the state of their password, MFA, and access keys. It is the first artifact to pull during an access review because it surfaces users without MFA, unused passwords, and access keys that have never been rotated.

## Permissions boundaries

A boundary is an identity-based policy attached to a user or role that sets a ceiling. The effective permissions are the intersection of the identity's policies and the boundary. Boundaries let a trusted administrator delegate *role creation* without granting the ability to escalate past the boundary — a common control in large accounts where developers may create roles but must not exceed a fixed maximum.

## SCPs and RCPs

In AWS Organizations:

- **SCP (service control policy)** caps permissions for member-account principals. It never *grants*; it only limits. The root user in a member account is also subject to SCPs, which is why an SCP can block an action even for an account administrator.
- **RCP (resource control policy)** caps permissions on resources across accounts.

Both are intersections, not unions — an action must pass the identity policy, the boundary, and the SCP/RCP.

## Identity vs resource policy (quick reference)

| Attribute | Identity-based | Resource-based |
|-----------|----------------|----------------|
| Attached to | user, group, role | a resource |
| Principal field | not required | required (who is granted) |
| Controls | what the identity can do | who can touch this resource |
| Cross-account | via role assumption | directly, per-resource |

## Rotation and credentials

- Rotate access keys on a schedule; never commit them to a repository.
- Give EC2, Lambda, and ECS workloads roles, not keys — via an instance profile or execution role.
- Use `aws sts get-caller-identity` to confirm which principal is acting in a session before debugging a permission error.

## Sources

- AWS — *IAM security best practices*. https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- AWS — *Permissions boundaries for IAM entities*. https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html
- AWS — *Service control policies*. https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html
