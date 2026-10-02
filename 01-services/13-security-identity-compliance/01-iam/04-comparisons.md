# IAM comparisons

> [!IMPORTANT]
> The exam's default answer for "a service or workload needs access" is a **role**, not a user with static keys. A role is assumed and yields short-lived STS credentials; a user with access keys is long-lived and those keys must be stored somewhere, which is the classic leak. Whenever a question offers both "IAM user with access keys" and "IAM role" for a workload — EC2, Lambda, ECS, a cross-account application — the role is the intended answer. This one distinction decides more scenario questions than any other IAM fact.

## IAM user vs IAM role

| | IAM user | IAM role |
|--|----------|----------|
| Credentials | long-lived (password / access keys) | temporary (STS tokens) |
| Sign-in | yes (console) | no — you assume it |
| Attached to a resource | no | yes (EC2, Lambda, ECS, cross-account) |
| Use for | humans, legacy service accounts | workloads, federation, delegation |

The exam's default answer for "a service or workload needs access" is **role**, not a user with static keys.

## Identity-based vs resource-based policy

- **Identity-based** attaches to a principal; no `Principal` element needed.
- **Resource-based** attaches to a resource; a `Principal` element is required.
- Same account: the two **combine** (union). An action allowed by either is allowed.

## Managed vs inline policy

| | Managed | Inline |
|--|---------|--------|
| Reusable | yes | no (embedded in one identity) |
| Versioning / tracking | yes | limited |
| Who edits | independent of the identity | deleted with the identity |
| Size limit | 6,144 chars | user 2,048 / role 10,240 / group 5,120 |

Prefer managed policies for anything reusable or shared.

## IAM vs IAM Identity Center

| | IAM | IAM Identity Center (SSO) |
|--|-----|---------------------------|
| Scope | one account | multi-account |
| Identities | users/roles you create | directory or external IdP |
| Access model | long-lived users, roles | permission sets mapped to accounts |
| Console sign-in | per-account | single portal |

For an organization with many accounts and human users, Identity Center (with permission sets and role-based sessions) replaces per-account IAM users.

## Permissions boundary vs SCP

Both cap permissions, at different scopes:

- **Boundary** — attached to one user/role, within an account.
- **SCP** — applied to an account (or OU) from Organizations, caps every principal in that account.

Both are **intersections**: they reduce, never expand, effective permissions.

## Sources

- AWS — *Managed policies and inline policies*. https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_managed-vs-inline.html
- AWS — *IAM Identity Center*. https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html
- AWS — *Permissions boundaries for IAM entities*. https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html
