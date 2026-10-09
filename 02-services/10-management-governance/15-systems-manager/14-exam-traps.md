# Systems Manager exam traps

Recurring mistakes candidates make, and what AWS actually does.

> [!CAUTION]
> The two most expensive Systems Manager traps are: (1) assuming a node is managed just because it launches, when the real gate is the **instance IAM role** allowing `ssm:UpdateInstanceInformation`; and (2) treating **patch groups** and **patch policies** as interchangeable. Both show up as "the feature silently does nothing" scenarios.

### "Any EC2 instance is managed by default"

**Mistake:** Assuming Systems Manager can control any instance that exists.

**Actual behavior:** A node is managed only when SSM Agent is installed and running, the instance role allows registration, and the agent reaches the endpoints. The agent is preinstalled on AWS AMIs (Amazon Linux, Ubuntu Server, Windows Server) but not on all images.

**Why it matters:** A scenario that says "an instance cannot be controlled by Systems Manager" is almost always the agent, the role, or the network path, in that order.

### "The agent is enough, no IAM role needed"

**Mistake:** Installing the agent and expecting the node to register.

**Actual behavior:** The instance needs a role granting `ssm:UpdateInstanceInformation`, normally through `AmazonSSMManagedInstanceCore`. Without it the agent runs but the node never appears.

**Why it matters:** This is the single most common cause of a node that is "not managed" despite a running agent.

### "Patch groups work with patch policies"

**Mistake:** Tagging nodes with `Patch Group` and also configuring a patch policy, expecting the tag to route.

**Actual behavior:** Patch policies do not use patch groups. Patch groups are a legacy mechanism that maps a tag value to a baseline; patch policies are the recommended organization-wide method and ignore the tag.

**Why it matters:** Scenarios that combine the two produce an unpatched fleet, and the correct fix is to pick one mechanism.

### "A node can be in several patch groups"

**Mistake:** Applying multiple patch-group tags to one instance.

**Actual behavior:** A node resolves to a single patch group, and a patch group registers with a single patch baseline.

**Why it matters:** Multi-baseline expectations fail; the node uses one baseline.

### "Advanced parameters can be downgraded"

**Mistake:** Creating an advanced parameter and later moving it to standard to stop the charge.

**Actual behavior:** Standard can be upgraded to advanced, but advanced **cannot** be downgraded. Downgrading would truncate an 8 KB value to 4 KB, drop its policies, and change the encryption form. To stop paying, delete it and recreate it as standard.

**Why it matters:** A cost question that says "reduce Parameter Store cost" expects deleting and recreating, not a tier change.

### "Parameter Store is where secrets belong"

**Mistake:** Storing database credentials or API keys as `SecureString` parameters.

**Actual behavior:** Parameter Store can encrypt with `SecureString`, but AWS recommends **Secrets Manager** for secrets because it adds automatic rotation and cross-Region replication.

**Why it matters:** A scenario that needs **rotation** expects Secrets Manager; Parameter Store does not rotate.

### "Systems Manager Automation is free"

**Mistake:** Assuming Automation has no charge.

**Actual behavior:** The free tier changed. Customers new to Automation as of August 14, 2025 do not receive it, and the free tier for existing customers ended December 31, 2025. Hybrid managed nodes also moved to pay-as-you-go for Session Manager and Run Command from September 30, 2026.

**Why it matters:** Cost scenarios now treat Automation and hybrid sessions as billable.

### "Maintenance Windows and State Manager are the same"

**Mistake:** Using one for the other's purpose.

**Actual behavior:** State Manager maintains a state on a schedule; Maintenance Windows run high-priority tasks inside a time window.

**Why it matters:** "Patch during a scheduled change window" is Maintenance Windows; "keep a config applied" is State Manager.

### "Session Manager needs an open inbound port"

**Mistake:** Opening port 22 or 3389 before using Session Manager.

**Actual behavior:** Session Manager uses the agent's outbound channel; no inbound port, bastion host, or SSH key is required.

**Why it matters:** The security-correct answer closes the inbound port, and any answer that opens one is wrong.

### "IMDSv2 is optional for Default Host Management"

**Mistake:** Enabling Default Host Management Configuration on instances still on IMDSv1.

**Actual behavior:** Default Host Management requires IMDSv2 and SSM Agent 3.2.582.0 or later, and it is enabled **per account and per Region**.

**Why it matters:** A scenario about instances in a new Region staying unmanaged is testing the per-Region scope.

### "Patch Manager upgrades the OS"

**Mistake:** Expecting Patch Manager to move Windows Server 2016 to 2019 or RHEL 7 to RHEL 8.

**Actual behavior:** Patch Manager patches and installs minor updates and service packs; it does not upgrade major versions. It also does not test patches before AWS lists them.

**Why it matters:** Major-version upgrade questions are answered by migrating, not patching.

## Sources

- AWS: *AWS Systems Manager User Guide* (per-tool pages cited in the sibling documents). https://docs.aws.amazon.com/systems-manager/latest/userguide/what-is-systems-manager.html
- AWS: *AWS Systems Manager endpoints and quotas*. https://docs.aws.amazon.com/general/latest/gr/ssm.html
- AWS: *AWS Systems Manager pricing*. https://aws.amazon.com/systems-manager/pricing/
