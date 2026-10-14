# Systems Manager exam practice questions

Twelve original, scenario-based questions covering the Systems Manager docs in this folder. They map mainly to **Domain 1 (Monitoring, Logging, and Remediation)**, **Domain 3 (Deployment, Provisioning, and Automation)**, and **Domain 4 (Security and Compliance)**. These are written in the SOA-C03 style, not copied from any exam.

The set covers: managed-node onboarding, Default Host Management Configuration, Session Manager logging, Run Command versus State Manager, patch groups, Parameter Store tiers and policies, Automation rate control, Maintenance Windows, Inventory aggregation, OpsCenter, and tagging.

---

## Q1

A company runs 200 EC2 instances in private subnets with no NAT gateway and no inbound security-group rules. The instances must be managed by Systems Manager. Which two changes let the nodes register? (Choose two.)

- A. Attach an IAM role with `AmazonSSMManagedInstanceCore` to the instances.
- B. Open inbound TCP 22 from the VPC CIDR to the instances.
- C. Create interface VPC endpoints for `ssm`, `ssmmessages`, and `ec2messages`.
- D. Install the CloudWatch agent on each instance.

<details><summary>Answer</summary>

**A and C.** The agent needs the role for `ssm:UpdateInstanceInformation`, and a private subnet with no NAT needs interface endpoints to reach the service.
- **B.** SSM Agent opens an outbound connection; it needs no inbound port.
- **D.** The CloudWatch agent sends metrics and logs; it does not register the node.

Reference: [01-fundamentals.md](01-fundamentals.md), [02-node-tools.md](02-node-tools.md).
</details>

---

## Q2

Default Host Management Configuration was enabled in `us-east-1`. A week later, a team launches instances in `us-west-2` and finds they never appear in Fleet Manager, even though the AMIs ship with SSM Agent and use IMDSv2. What is the cause?

- A. The agent needs to be reinstalled on the AMIs in `us-west-2`.
- B. Default Host Management Configuration is scoped per Region, so it is not active in `us-west-2`.
- C. The instances need an inbound rule on port 443.
- D. IMDSv2 blocks the agent from reading the instance identity.

<details><summary>Answer</summary>

**B.** Default Host Management Configuration is enabled per account **and per Region**; enabling it in one Region does nothing in another.
- **A.** The agent is preinstalled and running on these AMIs.
- **C.** Systems Manager uses no inbound port.
- **D.** IMDSv2 is required for DHMC, not blocked by it.

Reference: [01-fundamentals.md](01-fundamentals.md).
</details>

---

## Q3

Default Host Management Configuration is enabled in a Region, but some instances still show as unmanaged. Each has an instance profile whose policy grants `s3:GetObject` only. What should you do?

- A. Reboot the instances so the agent re-reads the configuration.
- B. Add `ssm:UpdateInstanceInformation` to the instance profile policy, or detach the profile.
- C. Delete the Default Host Management role and recreate it.
- D. Move the instances to a public subnet.

<details><summary>Answer</summary>

**B.** When an instance profile is attached, the agent uses it first; a profile that does not allow `UpdateInstanceInformation` leaves the node unmanaged, so add the permission or remove the profile so the DHMC role applies.
- **A.** A reboot does not change IAM.
- **C.** The DHMC role is fine.
- **D.** Subnet placement is not the issue when an endpoint or NAT path exists.

Reference: [01-fundamentals.md](01-fundamentals.md).
</details>

---

## Q4

A patch baseline is registered for patch group `PROD`. Some nodes that should be in that group keep falling back to the default baseline. The nodes are tagged `PatchGroup = Prod`. What is the problem?

- A. The nodes need to be rebooted after tagging.
- B. Patch Manager ignores Linux nodes.
- C. Key and value matching is case-sensitive, so `Prod` does not match `PROD`.
- D. The baseline must be the account default.

<details><summary>Answer</summary>

**C.** The patch group key and value are matched case-sensitively; `PatchGroup = Prod` is not the group `PROD`, so retag the nodes to `PROD` or register the baseline for `Prod`.
- **A.** Tagging is resolved at patch time; a reboot changes nothing.
- **B.** Patch Manager supports Linux.
- **D.** A registered group overrides the default; the default is only the fallback.

Reference: [04-patch-manager.md](04-patch-manager.md), [17-tagging.md](17-tagging.md).
</details>

---

## Q5

An auditor wants a full transcript of every Systems Manager session, including the commands run. Operators use a mix of interactive shell sessions and port-forwarding sessions to reach internal services. Which statement is correct?

- A. All session types are logged to CloudWatch Logs and S3.
- B. Only interactive shell sessions are logged; port-forwarding and SSH sessions are not.
- C. Session logging requires an inbound port on the node.
- D. Logging is available only with the AWS CLI, not the console.

<details><summary>Answer</summary>

**B.** Port-forwarding and SSH session data is encrypted inside the TLS tunnel and cannot be captured by the shell logger, so only interactive shell sessions produce session logs.
- **A.** Not all session types are logged.
- **C.** Sessions use the outbound agent channel; no inbound port is opened.
- **D.** Logging is independent of the client.

Reference: [03-session-run-state.md](03-session-run-state.md).
</details>

---

## Q6

An application reads a `SecureString` parameter and gets `AccessDenied` when it requests decryption, even though its role allows `ssm:GetParameter` on the parameter. What is missing?

- A. The parameter must be `String`, not `SecureString`.
- B. The role also needs `kms:Decrypt` on the KMS key.
- C. The parameter must be in the same VPC as the application.
- D. The role needs `ssm:DescribeParameters`.

<details><summary>Answer</summary>

**B.** A `SecureString` read needs `ssm:GetParameter` and `kms:Decrypt`; the missing decrypt permission is the usual cause of this failure.
- **A.** The type is intentional and supported.
- **C.** Parameter Store is a regional API, not VPC-bound.
- **D.** `DescribeParameters` is for listing, not reading values.

Reference: [07-parameter-store.md](07-parameter-store.md).
</details>

---

## Q7

A team needs a configuration value that is automatically deleted 30 days after creation and that emits an EventBridge notification before it expires. Which choice is required?

- A. A Standard parameter with a tag named `Expiration`.
- B. An Advanced parameter with a parameter policy.
- C. A `StringList` parameter.
- D. A parameter stored in Secrets Manager.

<details><summary>Answer</summary>

**B.** Expiration and expiration-notification are parameter policies, available only on **Advanced** parameters.
- **A.** Tags do not enforce expiration.
- **C.** The type does not add policies.
- **D.** Secrets Manager is a valid store, but the requirement is met by a Parameter Store advanced parameter.

Reference: [07-parameter-store.md](07-parameter-store.md).
</details>

---

## Q8

A State Manager association that applies a configuration file runs the moment it is created, which causes an unexpected change during business hours. The team wants it to run only at the scheduled time. What should they do?

- A. Set `ApplyOnlyAtCronInterval` on the association.
- B. Change the schedule from rate to cron.
- C. Add a maintenance window.
- D. Remove the `#` modifier from the cron expression.

<details><summary>Answer</summary>

**A.** By default an association runs immediately on creation and then on schedule; `ApplyOnlyAtCronInterval` skips the immediate run so it waits for the cron interval.
- **B.** The schedule type does not change the immediate run.
- **C.** A maintenance window is a different tool.
- **D.** The `#` modifier is unrelated to the immediate run.

Reference: [03-session-run-state.md](03-session-run-state.md).
</details>

---

## Q9

A runbook must patch 500 instances. The team wants the rollout to stop starting new invocations after 5 failures. Which Automation feature do they configure?

- A. A maintenance window cutoff.
- B. Automation rate control (`max-concurrency` and `max-errors`).
- C. A CloudWatch alarm.
- D. State Manager.

<details><summary>Answer</summary>

**B.** Rate control sets how many targets run concurrently and how many errors stop the run; `max-errors` of 5 stops starting new invocations after five failures.
- **A.** A cutoff bounds time, not errors.
- **C.** An alarm can pause invocations but is not the primary mechanism.
- **D.** State Manager is for ongoing state, not a one-time fan-out.

Reference: [06-change-management.md](06-change-management.md).
</details>

---

## Q10

A company patches its fleet on the second Sunday of every month inside a fixed 3-hour period, and the work must run only in that period. Which tool fits?

- A. State Manager association.
- B. A Maintenance Window with a cron schedule, duration, and cutoff.
- C. Run Command executed manually.
- D. Parameter Store.

<details><summary>Answer</summary>

**B.** A Maintenance Window schedules disruptive work in a bounded period with a duration and cutoff; the nth-weekday cron modifier selects the second Sunday.
- **A.** State Manager is for ongoing state, not a bounded window.
- **C.** Manual execution is ad hoc.
- **D.** Parameter Store stores values.

Reference: [06-change-management.md](06-change-management.md), [03-session-run-state.md](03-session-run-state.md).
</details>

---

## Q11

A security team must query software inventory across 12 accounts and 3 Regions from one place. Which combination delivers this?

- A. Inventory alone, from the console.
- B. A resource data sync writing inventory to a central S3 bucket, queried with Athena.
- C. Patch Manager baselines.
- D. Fleet Manager filtered by tag.

<details><summary>Answer</summary>

**B.** Inventory is per-Region in the console; a resource data sync centralizes metadata into one S3 bucket, which Athena then queries across accounts and Regions.
- **A.** The console view is not cross-account and cross-Region on its own.
- **C.** Patch baselines are for patching, not inventory.
- **D.** Fleet Manager shows nodes, not a queryable cross-account inventory.

Reference: [02-node-tools.md](02-node-tools.md).
</details>

---

## Q12

A CloudWatch alarm enters the `ALARM` state on a production database. The team wants an investigation item created automatically with the alarm context attached, before anyone is paged. Which service does this?

- A. AWS Config.
- B. Systems Manager OpsCenter (an OpsItem).
- C. AWS Trusted Advisor.
- D. Systems Manager Inventory.

<details><summary>Answer</summary>

**B.** OpsCenter creates an OpsItem when a CloudWatch alarm enters `ALARM` or from an EventBridge event, and attaches the resource and alarm context for investigation.
- **A.** Config records compliance, not a work item.
- **C.** Trusted Advisor reports best practices.
- **D.** Inventory collects node metadata.

Reference: [10-operations-tools.md](10-operations-tools.md), [11-monitoring.md](11-monitoring.md).
</details>
