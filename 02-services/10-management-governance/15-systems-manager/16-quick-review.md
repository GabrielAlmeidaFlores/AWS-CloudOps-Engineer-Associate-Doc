# Systems Manager quick review

> [!NOTE]
> This is the last thing you read before the exam. If any line below is not instantly obvious, go back to the document that owns it: fundamentals in `01-fundamentals.md`, node tools in `02-node-tools.md` and `03-session-run-state.md`, patching in `04-patch-manager.md`, automation in `06-change-management.md`, and configuration in `07-parameter-store.md`.

## Non-negotiables

- **A managed node needs three things.** SSM Agent installed and running, an IAM role that allows `ssm:UpdateInstanceInformation`, and a network path to the SSM endpoints. If a node is not managed, it is one of those, plus IMDS for Default Host Management.
- **The agent connects out.** HTTPS 443 outbound to `ssm`, `ssmmessages`, and `ec2messages`. No inbound port, no bastion, no SSH key.
- **Session Manager replaces bastion hosts and SSH.** Access is granted with IAM, and sessions are logged to CloudTrail, CloudWatch Logs, and S3 (not for port-forwarding or SSH sessions).
- **Run Command runs once; State Manager maintains state; Maintenance Windows run in a window.** That one sentence decides most "which tool" questions.
- **Patch baselines decide what installs; patch groups map nodes to a baseline by tag.** A node is in one patch group, and a group registers with one baseline. Patch policies ignore patch groups.
- **Parameter Store Standard vs Advanced.** 10,000 vs 100,000 parameters, 4 KB vs 8 KB, no policies vs policies, free vs billed, and Advanced is **not** downgradeable.
- **Secrets that rotate belong in Secrets Manager, not Parameter Store.**
- **Automation runs runbooks.** They can be triggered manually, by EventBridge, by Maintenance Windows, or by AWS Config remediation.

## The tools in one line each

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

- Managed nodes: **2,400** per account per Region by default.
- Automation: **12 hours** max in a user context; `executeScript` **10 minutes**.
- Parameter Store: **10,000** Standard / **100,000** Advanced; **4 KB** / **8 KB**; **100** versions retained.
- Inventory: **30 minutes** minimum interval; **30 days** retention.
- State Manager: **2,000** associations; **20** per node.
- Session Manager idle timeout: **20 minutes** default.
- Document size: **64 KB**; **500** documents.

## The one-liner

Install the agent, grant the role, reach the endpoints: after that, Systems Manager is a set of tools that all reach the node over the agent's outbound channel, each chosen by whether the job is a one-time command, an ongoing state, a scheduled window, or a multi-step workflow.

## Sources

- Full references live in the per-tool documents. Start with `01-fundamentals.md` and `04-patch-manager.md`.
