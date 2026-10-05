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

A permissions boundary is an IAM policy that sets the **maximum** permissions an identity can have. It attaches to a user or role, and the identity's effective permissions are the intersection of its identity-based policies and the boundary — the boundary can only take permissions away, never add them.

Boundaries exist so a trusted administrator can safely delegate identity *creation*. In a large account, a developer may be allowed to create roles, but a boundary on those roles caps what the roles can ever do, so the developer cannot escalate to full administrator by creating an over-permissioned role.

A boundary that caps a role to read-only S3 and CloudWatch access, even if the role's own policy is broader:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:Get*", "s3:List*", "cloudwatch:Get*", "cloudwatch:List*"],
    "Resource": "*"
  }]
}
```

The boundary is written as an `Allow` policy, which is what confuses people: it grants nothing on its own. It defines the ceiling that the identity's real policies are matched against, so any action outside it is denied even when an identity policy allows it.

## SCPs and RCPs

AWS Organizations has two kinds of authorization policy that set guardrails across your accounts. Both are **intersections** in policy evaluation — they can only remove access, never grant it, and an action must pass them as well as the identity and resource policies. They differ in what they govern: an SCP governs what your principals may do; an RCP governs who may reach your resources.

### Service control policy (SCP)

An SCP caps the maximum permissions for **IAM users and roles in a member account**. It is the tool for confining what identities inside your organization are allowed to do.

- Applies only to member accounts, never the management account.
- Applies to every principal in the account, **including the account's root user**, which is why an SCP can block an action even for an account administrator holding `AdministratorAccess`.
- Does not affect resource-based policies, principals outside the organization, or service-linked roles.
- Attached to the organization root, an OU, or an individual account. A principal has only the permissions allowed by **every** level above it, so a deny high in the tree cannot be undone lower down.
- Requires all features enabled. The default `FullAWSAccess` policy is attached everywhere; removing it without replacing it blocks all actions in that scope.

You work with SCPs in the AWS Organizations console under **Policies → Service control policies**, attached to the root, an OU, or an account, or with `aws organizations create-policy --type SERVICE_CONTROL_POLICY`. Control Tower and CloudFormation can deploy them at scale.

An SCP that blocks every action outside two approved Regions — everything inside them stays allowed because `FullAWSAccess` still applies:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyOutsideApprovedRegions",
    "Effect": "Deny",
    "Action": "*",
    "Resource": "*",
    "Condition": { "StringNotEquals": { "aws:RequestedRegion": ["us-east-1", "us-west-2"] } }
  }]
}
```

### Resource control policy (RCP)

An RCP caps the maximum permissions for **resources in a member account**. It is the tool for controlling who can reach your resources — including principals from accounts outside your organization, which SCPs cannot touch.

- Applies to a subset of services (for example Amazon S3, DynamoDB, SQS, KMS, and CloudWatch Logs), not all of them.
- Is evaluated based on the **resource owner's** account, so it restricts external callers, not just your own principals.
- Never grants. The resource owner must still attach a resource-based policy (or the caller an identity policy) to actually allow access.
- Like an SCP, it attaches to the root, an OU, or an account, and it does not affect the management account, service-linked roles, or AWS-managed KMS keys.

You work with RCPs in the AWS Organizations console under **Policies → Resource control policies**, or with `aws organizations create-policy --type RESOURCE_CONTROL_POLICY`.

An RCP that denies access to an S3 bucket unless the caller belongs to your organization — the external-account protection SCPs cannot provide:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyOutsideOrganization",
    "Effect": "Deny",
    "Principal": "*",
    "Action": "s3:*",
    "Resource": "*",
    "Condition": { "StringNotEquals": { "aws:PrincipalOrgID": "o-exampleorg" } }
  }]
}
```

### The difference

An SCP limits what *your* principals can do; an RCP limits who can do things to *your* resources. Use an SCP to confine identities inside member accounts; use an RCP to lock down access to resources in those accounts, above all from principals outside the organization.

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
- AWS — *Resource control policies*. https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_rcps.html
