# IAM exam practice questions

Eleven original, scenario-based questions covering the IAM docs in this folder. They map mainly to **Domain 4 (Security and Compliance)**, and touch **Domain 1 (auditing with CloudTrail)** and **Domain 3 (roles as code)**. Written in the SOA-C03 style, not copied from any exam.

The set covers: the policy evaluation order, SCPs versus permissions boundaries, roles versus users, cross-account access, resource-based policies, MFA conditions, policy types and limits, Access Analyzer, STS, and least privilege.

---

## Q1

A user has an identity policy that allows `s3:GetObject` on a bucket, a permissions boundary that does not include `s3:GetObject`, and an SCP that allows all S3 actions. The user's `GetObject` call returns `AccessDenied`. Why?

- A. The SCP denied the action.
- B. The permissions boundary excludes `s3:GetObject`, and a boundary can only cap, never grant.
- C. The bucket needs a resource policy.
- D. IAM policies are eventually consistent.

<details><summary>Answer</summary>

**B.** A permissions boundary limits the maximum permissions an identity can have; an action outside the boundary is denied even when an identity policy allows it.
- **A.** The SCP allows all S3 actions, so it is not the cause.
- **C.** A resource policy is not required for same-account access.
- **D.** This is an authorization decision, not consistency lag.

Reference: [01-concepts.md](01-concepts.md), [02-security.md](02-security.md).
</details>

---

## Q2

An organization applies an SCP that allows only `ec2` and `s3` actions. A developer's identity policy allows `iam:CreateUser`. The developer cannot create users. Which statement explains this?

- A. An SCP that allows a service denies everything else by omission in the affected accounts.
- B. IAM users cannot create other IAM users.
- C. The SCP granted `iam:CreateUser` but the identity policy denied it.
- D. SCPs do not apply to IAM users.

<details><summary>Answer</summary>

**A.** An SCP sets the maximum permissions for accounts in the organization; anything not allowed by the SCP is denied, even if an identity policy allows it.
- **B.** IAM users can create users when a policy allows it.
- **C.** SCPs never grant permissions.
- **D.** SCPs apply to principals in the affected accounts.

Reference: [02-security.md](02-security.md), [04-comparisons.md](04-comparisons.md).
</details>

---

## Q3

An application on an EC2 instance must read objects from an S3 bucket. What is the correct, most secure approach?

- A. Create an IAM user and put its access key in the application configuration.
- B. Attach a role to the instance through an instance profile and grant the role `s3:GetObject`.
- C. Store an access key in the AMI and rotate it every 90 days.
- D. Make the bucket public and rely on a bucket policy.

<details><summary>Answer</summary>

**B.** An instance role delivers short-lived credentials through instance metadata; nothing long-lived is stored on the host.
- **A.** A stored access key is long-lived and can leak.
- **C.** A key baked into the AMI is long-lived and hard to rotate safely.
- **D.** A public bucket exposes the objects.

Reference: [04-comparisons.md](04-comparisons.md), [02-security.md](02-security.md).
</details>

---

## Q4

Account A must let a principal in account B read a specific S3 bucket. The team wants the least operational overhead and no temporary role switching. What is the simplest correct approach?

- A. An identity policy in account B that allows `s3:GetObject` on the bucket.
- B. A resource-based bucket policy in account A that grants the account B principal `s3:GetObject`.
- C. A shared access key stored in both accounts.
- D. An SCP in account B.

<details><summary>Answer</summary>

**B.** A resource-based policy on the bucket can grant a principal in another account access directly, with no role assumption.
- **A.** A cross-account identity policy alone is not sufficient without a resource grant.
- **C.** Shared long-lived keys are poor practice.
- **D.** An SCP restricts; it never grants.

Reference: [01-concepts.md](01-concepts.md), [04-comparisons.md](04-comparisons.md).
</details>

---

## Q5

A company requires that console users sign in with MFA before they can stop EC2 instances. Which policy element enforces this?

- A. `Condition` with `Bool: {"aws:MultiFactorAuthPresent": "true"}` on the `ec2:StopInstances` statement.
- B. A password policy that requires MFA.
- C. An SCP that denies all EC2 actions.
- D. A resource-based policy on the instances.

<details><summary>Answer</summary>

**A.** A condition key such as `aws:MultiFactorAuthPresent` gates the action on an MFA-authenticated session.
- **B.** A password policy enforces password strength, not MFA.
- **C.** An SCP that denies EC2 blocks the action entirely.
- **D.** A resource policy does not apply to the caller's MFA state.

Reference: [02-security.md](02-security.md).
</details>

---

## Q6

A team attaches more than ten managed policies to one role and the console rejects the change. What is the limit?

- A. Two managed policies per role.
- B. Ten managed policies per role by default.
- C. Twenty inline policies per role.
- D. There is no limit.

<details><summary>Answer</summary>

**B.** A role can have **10** managed policies attached by default (an adjustable quota); consolidate or use inline policies within their size limits to exceed it.
- **A.** The default is not two.
- **C.** The statement misstates inline policy counts.
- **D.** There is a default quota.

Reference: [06-limits-defaults.md](06-limits-defaults.md).
</details>

---

## Q7

An auditor wants to find resource-based policies that grant public or cross-account access across the account's S3 buckets, KMS keys, and IAM roles. Which tool is built for this?

- A. AWS Trusted Advisor.
- B. IAM Access Analyzer.
- C. AWS Config.
- D. GuardDuty.

<details><summary>Answer</summary>

**B.** IAM Access Analyzer analyzes resource-based policies and reports resources shared with external entities.
- **A.** Trusted Advisor offers best-practice checks.
- **C.** AWS Config records compliance state.
- **D.** GuardDuty detects threats from activity and logs.

Reference: [README.md](README.md), [01-concepts.md](01-concepts.md).
</details>

---

## Q8

A security team must answer "which principal deleted this S3 bucket, when, and from which IP" after an incident. Where is that recorded?

- A. Amazon CloudWatch metrics.
- B. AWS CloudTrail management events.
- C. AWS Config.
- D. VPC Flow Logs.

<details><summary>Answer</summary>

**B.** CloudTrail records the API call, the calling principal, the time, and the source IP for management events such as `DeleteBucket`.
- **A.** CloudWatch metrics are numeric, not an API audit trail.
- **C.** Config records configuration state and history, not the caller identity for every call.
- **D.** VPC Flow Logs record network flows, not API authorship.

Reference: [03-troubleshooting.md](03-troubleshooting.md), [README.md](README.md).
</details>

---

## Q9

An application assumes a role to run a batch job. Which statement about the credentials it receives is correct?

- A. They are permanent until the role is deleted.
- B. They are temporary credentials issued by STS and they expire.
- C. They are the same as the role's access key.
- D. They cannot be revoked before expiry.

<details><summary>Answer</summary>

**B.** `sts:AssumeRole` returns temporary credentials with an expiration; a principal re-assumes the role to refresh them.
- **A.** They expire.
- **C.** A role has no long-lived access key.
- **D.** A role's session can be revoked before expiry.

Reference: [01-concepts.md](01-concepts.md), [04-comparisons.md](04-comparisons.md).
</details>

---

## Q10

A policy grants `s3:*` on `*`. A reviewer asks the team to tighten it to only what the application uses. Which practice fits?

- A. Leave it and add an SCP.
- B. Replace the wildcard with the specific actions and the specific bucket ARN the application needs.
- C. Add an MFA condition.
- D. Move the policy to a resource-based policy.

<details><summary>Answer</summary>

**B.** Least privilege means granting only the actions and resources required; scoping the action list and the resource ARN does that directly.
- **A.** An SCP adds a ceiling without narrowing the grant.
- **C.** An MFA condition does not reduce the scope of the actions granted.
- **D.** Moving it does not narrow what it allows.

Reference: [02-security.md](02-security.md).
</details>

---

## Q11

A developer reports `AccessDenied` on an action that a policy appears to allow. Which two steps best diagnose it? (Choose two.)

- A. Check for an explicit `Deny` in identity, resource, boundary, or SCP policies.
- B. Reboot the developer's workstation.
- C. Confirm the policy's `Action`, `Resource`, and any `Condition` actually match the request.
- D. Recreate the developer's access keys.

<details><summary>Answer</summary>

**A and C.** An explicit `Deny` anywhere in the chain wins, and an apparent `Allow` often mismatches the action name, resource ARN, or condition for the request.
- **B.** A reboot does not change authorization.
- **D.** Recreating access keys does not resolve a policy mismatch.

Reference: [03-troubleshooting.md](03-troubleshooting.md), [01-concepts.md](01-concepts.md).
</details>
