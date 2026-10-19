# Systems Manager quick review

This page is the final recall gate for the topic, not a second explanation. It compresses the managed-node requirements, the tool roles, and the key numbers into the facts you should be able to state without derivation.

> [!NOTE]
> This is the last thing you read before the exam. If any line below is not instantly obvious, go back to the document that owns it: fundamentals in `01-fundamentals.md`, node tools in `02-node-tools.md` and `03-session-run-state.md`, patching in `04-patch-manager.md`, automation in `06-change-management.md`, and configuration in `07-parameter-store.md`.

## Non-negotiables

These are the facts you should be able to state from memory. Each one decides a common scenario, and the explanation is in the document that owns it, not in this summary.

- **A managed node needs three things.** SSM Agent installed and running, an IAM role that allows `ssm:UpdateInstanceInformation` (an instance profile, or the DHMC role), and a network path to the SSM endpoints. If a node is not managed, it is one of those, plus IMDSv2 and agent 3.2.582.0+ for Default Host Management.
- **The agent connects out.** HTTPS 443 outbound to `ssm`, `ssmmessages`, and `ec2messages`. No inbound port, no bastion, no SSH key.
- **Session Manager replaces bastion hosts and SSH.** Access is granted with IAM, and sessions are logged to CloudTrail, CloudWatch Logs, and S3 (not for port-forwarding or SSH sessions).
- **Run Command runs once; State Manager maintains state; Maintenance Windows run in a window.** That one sentence decides most "which tool" questions.
- **Patch baselines decide what installs; patch groups map nodes to a baseline by tag.** A node is in one patch group, and a group registers with one baseline. Patch policies ignore patch groups.
- **Parameter Store Standard vs Advanced.** 10,000 vs 100,000 parameters, 4 KB vs 8 KB, no policies vs policies, free vs billed, and Advanced is **not** downgradeable.
- **Secrets that rotate belong in Secrets Manager, not Parameter Store.**
- **Automation runs runbooks.** They can be triggered manually, by EventBridge, by Maintenance Windows, or by AWS Config remediation.

## The tools in one line each

The tools overlap in the console, so the list gives each one its single job; use it to map a scenario to the right tool before you recall the details.

- **Fleet Manager:** console/GUI remote management of nodes.
- **Compliance:** patch and association compliance across the fleet.
- **Inventory:** installed software, OS, and configuration metadata, queryable across accounts and Regions.
- **Hybrid Activations:** register non-EC2 machines as `mi-` nodes.
- **Session Manager:** IAM-authorized shell without inbound ports.
- **Run Command:** run a document once, at scale.
- **State Manager:** associations that keep a defined state on a schedule.
- **Patch Manager:** OS and application patching against a baseline.
- **Distributor:** package and deploy versioned software.
- **Automation:** multi-step runbooks across AWS services.
- **Change Calendar:** OPEN/CLOSED gate that blocks or permits changes.
- **Maintenance Windows:** run disruptive tasks in a bounded window.
- **Documents:** the JSON or YAML actions every tool runs.
- **Quick Setup:** configure patching and host management at organization scale.
- **Parameter Store:** hierarchical configuration and encrypted values.
- **AppConfig:** feature flags and runtime config with validation and rollback.
- **Resource Groups:** tag- or stack-based targets for the tools.
- **Explorer:** aggregated operations dashboard.
- **OpsCenter:** the queue of OpsItems with runbooks to resolve them.

## Key numbers

These are the numbers a scenario can turn on, and each row pairs the default with what it controls and what happens when it is exceeded.

| Setting | Default | What it controls and why it matters |
|---------|---------|-------------------------------------|
| Managed nodes | 2,400 per account per Region | The registration ceiling. A fleet above it needs a quota increase before new nodes appear, which is the usual cause of "the instance launched but never shows up". |
| Automation execution | 12 hours in a user context; `executeScript` step 10 minutes | The hard timeout on a runbook step. A long script fails at the step timeout unless the work is split or the timeout is raised. |
| Parameter Store | 10,000 Standard and 100,000 Advanced parameters per account per Region; 4 KB Standard and 8 KB Advanced values; 100 versions retained | The count and value-size ceilings. A large config blob or a high parameter count forces the Advanced tier, which changes the cost model. |
| Inventory | 30 minutes minimum collection interval; 30 days console retention | How fresh and how far back the inventory data goes. Longer retention requires a resource data sync to S3. |
| State Manager | 2,000 associations per account per Region; 20 per node | The scale limits for ongoing enforcement. A node that already has 20 associations cannot take another, which appears as a failed association. |
| Session Manager | 20-minute default idle timeout | When an idle session closes. A long interactive task needs activity or a configured timeout. |
| SSM documents | 64 KB per document; 500 documents per account per Region | The size and count limits for the documents that define commands and runbooks. A large script must be fetched from S3 instead of embedded. |

## The one-liner

Install the agent, grant the role, reach the endpoints: after that, Systems Manager is a set of tools that all reach the node over the agent's outbound channel, each chosen by whether the job is a one-time command, an ongoing state, a scheduled window, or a multi-step workflow.

## Sources

This page keeps the bibliography short: the detailed sources live in the topic documents, and the links below point to the files that carry them.

- Full references live in the per-tool documents. Start with `01-fundamentals.md` and `04-patch-manager.md`.
