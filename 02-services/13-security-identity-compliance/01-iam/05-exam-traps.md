# IAM exam traps

Recurring mistakes candidates make, and what AWS actually does.

> [!CAUTION]
> These are the traps that cost points. The two most expensive are: (1) forgetting that **an explicit deny beats every allow**, so a scenario with a working allow plus a hidden deny in a boundary, SCP, or inline policy is actually denied; and (2) mixing up the role's **trust policy** (who may assume the role) with its **permissions policy** (what the assumed role may do). Fixing the wrong one of the two is the classic "cross-account access still failing" question.

### "Roles are people too"

**Mistake:** Treating a role like a user — signing in with it, giving it a password.

**Actual behavior:** A role has no password and no long-lived keys. It is assumed, and it returns temporary credentials through STS.

**Why it matters:** A scenario asking for EC2-to-S3 access expects an instance profile + role, not a user with keys baked into the instance.

### "An Allow and a Deny cancel out"

**Mistake:** Believing conflicting statements resolve to the more specific one, or to neither.

**Actual behavior:** Explicit **deny always wins**, regardless of how many allows exist.

**Why it matters:** The exam frequently presents a working allow plus a hidden deny (SCP, boundary, inline deny) and asks why access fails.

### "If two policies allow different things, both apply"

**Mistake:** Expecting identity and resource policies to intersect.

**Actual behavior:** Identity-based + resource-based policies are a **union** — either can allow. Boundaries and SCPs are the intersections.

**Why it matters:** Cross-account and same-account S3 scenarios hinge on knowing which combination is union and which is intersection.

### "A service can use a user's static keys"

**Mistake:** Giving an application a long-lived IAM user access key.

**Actual behavior:** The correct pattern is a role assumed by the service (EC2 instance profile, Lambda execution role).

**Why it matters:** Security-focused questions reward the role pattern; static keys are a red flag in the answer options.

### "IAM is regional"

**Mistake:** Looking for a role in the Region you created it in.

**Actual behavior:** IAM is global. Users, roles, and policies are account-scoped, not regional.

### "Deny-by-default means an empty policy denies"

**Mistake:** Confusing "no allow" with an explicit deny.

**Actual behavior:** Absence of an allow is **implicit deny** — distinct from an explicit `Deny` statement, which overrides allows. Implicit deny does not override an allow.

### "A permissions boundary grants permissions"

**Mistake:** Assuming a boundary adds access.

**Actual behavior:** A boundary only limits. It never grants anything by itself.

### "Trust policy controls what the role can do"

**Mistake:** Confusing the role's two policies.

**Actual behavior:** The **trust policy** says who can assume the role; the **permissions policy** says what the role can do. A common trap is fixing the wrong one.

## Sources

- AWS — *SOA-C03 exam guide, Content Domain 4*. https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/sysops-administrator-associate-03-domain4.html
- AWS — *Policy evaluation logic*. https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html
- Community — candidate reports on SOA-C03 IAM misconceptions (re:Post, Reddit r/AWSCertifications).
