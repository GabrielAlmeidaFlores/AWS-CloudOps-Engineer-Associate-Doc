# IAM security

> [!IMPORTANT]
> Permissions boundaries and SCPs never *grant* access — they only narrow it. Each is an intersection: the effective permission is what the identity policy allows *and* the boundary or SCP does not exclude. So if a scenario asks how to give a user more access, a boundary or SCP is the wrong answer; adding one can only remove access that was already allowed. Candidates repeatedly pick "add a permissions boundary" to fix an over-permissioned user, when the boundary restricts rather than expands.

## Least privilege

Grant only the actions and resources a principal needs. Prefer:

- Role over a long-lived user for any workload or cross-account access.
- Resource-based policies where the resource should be the point of control (S3 buckets, KMS keys, SQS queues).
- Condition keys to narrow a broad action instead of adding a `Deny` (e.g. `aws:RequestedRegion`, `aws:SourceVpce`).

The IAM Access Analyzer generates policies from logged access, and can flag externally shared resources — two tools for tightening privilege without guessing.

## MFA and password policy

- **MFA** on the root user and on every human user. Virtual MFA (TOTP) or hardware (U2F) device. MFA protects the console; it does not protect programmatic access keys.
- **Password policy** is account-wide: minimum length, complexity, rotation, and password reuse prevention. There is one password policy per account, applied to all IAM users.

## Permissions boundaries

A boundary is an identity-based policy attached to a user or role that sets a ceiling. The identity's effective permissions are the intersection of its policies and the boundary. Boundaries let a trusted admin delegate role *creation* without granting the ability to escalate past the boundary — a common control in large accounts.

## SCPs and RCPs

In AWS Organizations:

- **SCP (service control policy)** caps permissions for member-account principals. It never *grants*; it only limits. The root user in a member account is also subject to SCPs.
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

- Rotate access keys on a schedule; never commit them.
- Give EC2/Lambda/ECS workloads roles, not keys.
- Use `aws sts get-caller-identity` to confirm which principal is acting in a session.

## Sources

- AWS — *IAM security best practices*. https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- AWS — *Permissions boundaries for IAM entities*. https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html
- AWS — *Service control policies*. https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html
