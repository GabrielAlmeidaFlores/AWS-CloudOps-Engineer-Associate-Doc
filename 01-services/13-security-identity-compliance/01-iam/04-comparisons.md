# IAM comparisons

> [!IMPORTANT]
> The exam's default answer for "a service or workload needs access" is a **role**, not a user with static keys. A role is assumed and yields short-lived STS credentials; a user with access keys is long-lived and those keys must be stored somewhere, which is the classic leak. Whenever a question offers both "IAM user with access keys" and "IAM role" for a workload — EC2, Lambda, ECS, a cross-account application — the role is the intended answer. This one distinction decides more scenario questions than any other IAM fact.

## IAM user vs IAM role

The core difference is credential lifetime. A user has permanent credentials (a password and/or access keys) that live until deleted or rotated. A role has none of its own — it is assumed, and the caller receives temporary STS credentials that expire. That lifetime difference is why a role is the safe choice for anything automated.

| | IAM user | IAM role |
|--|----------|----------|
| Credentials | long-lived (password / access keys) | temporary (STS tokens) |
| Sign-in | yes (console) | no — you assume it |
| Attached to a resource | no | yes (EC2, Lambda, ECS, cross-account) |
| Use for | humans, legacy service accounts | workloads, federation, delegation |

The exam's default answer for "a service or workload needs access" is **role**, not a user with static keys.

## Identity-based vs resource-based policy

The two policy types answer different questions. An identity-based policy says what a principal may do; a resource-based policy says who may touch the resource. For same-account access they combine as a union — either one can grant the action.

- **Identity-based** — attaches to a principal; no `Principal` element needed.
- **Resource-based** — attaches to a resource; a `Principal` element is required.
- Same account: the two **combine** (union). An action allowed by either is allowed.

For cross-account access the distinction matters: a resource-based policy can grant another account access directly, whereas identity-based access requires the other account to assume a role.

## Managed vs inline policy

Managed policies are standalone documents you attach to many identities and version independently. Inline policies are embedded in a single identity and are deleted with it. Managed policies are the right default for anything shared; inline policies suit a one-off, tightly scoped grant that should not be reused.

| | Managed | Inline |
|--|---------|--------|
| Reusable | yes | no (embedded in one identity) |
| Versioning / tracking | yes | limited |
| Who edits | independent of the identity | deleted with the identity |
| Size limit | 6,144 chars | user 2,048 / role 10,240 / group 5,120 |

Prefer managed policies for anything reusable or shared.

## IAM user vs IAM Identity Center

IAM was built for one account. For an organization with many accounts and human users, IAM Identity Center provides a single sign-on portal backed by a directory or external IdP, and assigns access through permission sets mapped to accounts. This replaces the old pattern of creating a separate IAM user in every account.

| | IAM | IAM Identity Center (SSO) |
|--|-----|---------------------------|
| Scope | one account | multi-account |
| Identities | users/roles you create | directory or external IdP |
| Access model | long-lived users, roles | permission sets mapped to accounts |
| Console sign-in | per-account | single portal |

For an organization with many accounts and human users, Identity Center (with permission sets and role-based sessions) replaces per-account IAM users.

## Permissions boundary vs SCP

Both cap permissions, but at different scopes and under different administration.

- **Boundary** — attached to one user/role, inside an account; administered by whoever manages that identity.
- **SCP** — applied to an account or OU from Organizations; caps every principal in that account, including the root user.

Both are **intersections**: they reduce, never expand, effective permissions.

## Sources

- AWS — *Managed policies and inline policies*. https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_managed-vs-inline.html
- AWS — *IAM Identity Center*. https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html
- AWS — *Permissions boundaries for IAM entities*. https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html
