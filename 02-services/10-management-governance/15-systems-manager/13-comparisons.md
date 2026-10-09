# Systems Manager comparisons

These are the distinctions that decide exam answers. Each one pits two Systems Manager capabilities or one Systems Manager capability against an adjacent service, and the difference changes which is correct.

## Run Command vs State Manager vs Maintenance Windows

| | Run Command | State Manager | Maintenance Windows |
|--|-------------|---------------|---------------------|
| Nature | Run a command once | Maintain a state on a schedule | Run a task inside a bounded window |
| Trigger | You invoke it | Cron or rate schedule | The window's schedule |
| Best for | One-time change, bootstrap, capture logs | Ongoing configuration, prevent drift | High-priority, time-sensitive disruptive work |
| Task types | Documents of type Command | Documents plus Automation runbooks | Run Command, Automation, Lambda, Step Functions |

The exam phrasing test: "run this now on many nodes" is Run Command; "keep this applied" is State Manager; "do this inside a change window" is Maintenance Windows.

## State Manager vs Maintenance Windows

The documentation states the distinction directly: choose State Manager to **automate system compliance**, and Maintenance Windows to perform **high-priority, time-sensitive tasks during periods you specify**. Keeping antivirus installed is State Manager; patching the fleet during the Sunday maintenance window is Maintenance Windows.

## Patch groups vs patch policies

| | Patch groups | Patch policies (Quick Setup) |
|--|--------------|------------------------------|
| Mechanism | Tag (`Patch Group` or `PatchGroup`) mapped to a baseline | Policy configured in Quick Setup |
| Recommended | Legacy mechanism | Yes, the recommended patching method |
| Organizations | Per account and Region | One policy spanning the organization |
| Used together | Not used by patch policies | Does not use patch groups |

A common trap: a scenario that sets a `Patch Group` tag *and* configures a patch policy is mixing two mechanisms. Patch policies do not read patch groups.

## Parameter Store vs Secrets Manager vs AppConfig

| | Parameter Store | Secrets Manager | AppConfig |
|--|-----------------|-----------------|-----------|
| Best for | Static configuration, lightweight encrypted values | Credentials and secrets | Feature flags and runtime config with safe rollout |
| Encryption | Optional (`SecureString` with KMS) | Always, with KMS | Via KMS |
| Rotation | None | Automatic, with database integrations | Not the same concept |
| Rollout safety | None (next read takes effect) | None | Validators, gradual deployment, automatic rollback |

The default rule for the exam: configuration goes in **Parameter Store**, rotating secrets go in **Secrets Manager**, and changes that need validation and rollback go in **AppConfig**.

## Default Host Management Configuration vs instance profile

| | Default Host Management Configuration | Instance profile |
|--|---------------------------------------|------------------|
| IAM setup | Automatic default role | You create and attach a role |
| Scope | Per account and per Region | Per instance |
| Requires | IMDSv2 and SSM Agent 3.2.582.0+ | Agent and a role with `UpdateInstanceInformation` |
| Precedence | Used only when no profile grants registration | Used first if present and permitting |

A node with an instance profile that allows `ssm:UpdateInstanceInformation` will not fall back to the Default Host Management role. That precedence is a deliberate exam distinction.

## Session Manager vs bastion host or SSH

| | Session Manager | Bastion host + SSH |
|--|-----------------|--------------------|
| Inbound ports | None | SSH or RDP must be open |
| Credentials | IAM-authorized sessions | SSH keys or RDP credentials |
| Audit | CloudTrail, CloudWatch Logs, S3 session logging | Depends on the host |
| Bastion required | No | Yes |

Session Manager replaces bastion hosts, SSH keys, and open inbound ports with IAM-authorized sessions and logging.

## Explorer vs OpsCenter (and Application Manager)

| | Explorer | OpsCenter | Application Manager |
|--|----------|-----------|---------------------|
| Role | Aggregated operations dashboard | Queue of OpsItems to investigate and fix | Application-centric operations view |
| Primary object | Widgets and OpsData | OpsItems | Applications and clusters |
| Action | Visualize and link | Remediate with runbooks | Investigate and remediate in context |

Explorer is the *view*; OpsCenter is the *work*. "Reduce mean time to resolution by viewing, investigating, and remediating in one place" points to OpsCenter. Application Manager is the application-context variant and is closed to new customers.

## Automation vs Run Command

| | Run Command | Automation |
|--|-------------|------------|
| Unit of work | One command on nodes | A multi-step runbook |
| Targets | Managed nodes | Managed nodes and other AWS resources (EC2, RDS, S3, and more) |
| Logic | Script plus parameters | Steps, conditions, approvals, scripts, and cross-service actions |
| Scale control | Rate controls | Rate controls and adaptive concurrency |

Use Run Command for a command; use Automation when the work is a workflow across services or needs approvals and branching.

## Sources

- AWS: *Choosing between State Manager and Maintenance Windows*. https://docs.aws.amazon.com/systems-manager/latest/userguide/state-manager-vs-maintenance-windows.html
- AWS: *AWS Systems Manager Patch Manager* and *patch groups*. https://docs.aws.amazon.com/systems-manager/latest/userguide/patch-manager.html
- AWS: *AWS Systems Manager Parameter Store*. https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html
- AWS: *Managing EC2 instances automatically with Default Host Management Configuration*. https://docs.aws.amazon.com/systems-manager/latest/userguide/fleet-manager-default-host-management-configuration.html
