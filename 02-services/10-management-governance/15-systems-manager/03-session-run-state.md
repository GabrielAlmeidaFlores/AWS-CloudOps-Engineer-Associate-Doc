# Session Manager, Run Command, and State Manager

Three tools cover the day-to-day act of operating a node: getting a shell on it, running a command on it once, and keeping it in a defined state over time. They share one mechanism, the SSM Agent's outbound channel, which is why none of them needs an inbound port, a bastion host, or an SSH key. This document treats each in turn, then the comparison that decides which one an exam scenario is asking for.

## Session Manager

Session Manager gives you an interactive shell or a one-shot command channel to a managed node, through either a browser-based shell or the AWS CLI, with no need to open inbound ports, maintain bastion hosts, or manage SSH keys.

- **Access control through IAM.** Access to nodes is granted and revoked with IAM policies, not SSH keys, so a single place governs who can reach which node.
- **Session types.** Interactive shell sessions; port forwarding (redirect a port inside the node to a local client port); SSH sessions; and non-interactive command sessions.
- **Cross-platform.** Windows, Linux, and macOS from the same tool, so you do not need an SSH client for Linux or an RDP client for Windows.
- **Logging.** Session activity can be recorded to CloudTrail (API calls), Amazon S3, and CloudWatch Logs, and start/stop events can drive EventBridge rules and SNS notifications.
- **Logging gap.** Session logging is **not** available for sessions that connect through port forwarding or SSH, because the session data is encrypted inside the TLS tunnel and cannot be captured by the shell logger.

The security argument is the point: replacing inbound SSH (port 22) and RDP (port 3389) with IAM-authorized sessions removes the exposed attack surface, and every session is attributable to an IAM principal.

Starting a session is a three-step workflow. Step 1 picks the target and records why the session is being opened, which is what makes the audit trail meaningful.

![Session Manager start-session step 1, Specify target, with the reason field and node list](../../../assets/images/screenshots/ssm/09-ssm-session-manager-start-session.png)

*The Session Manager **Start a session** workflow. The step indicator (1) shows the three steps: Specify target, Specify session document (optional), and Review and launch. The **Reason for session** field (2) is optional but is written into the CloudTrail event when the session starts, so it is how you record intent. The target table (3) lists the managed nodes; selecting one and choosing Next opens the shell with no inbound port and no SSH key.*

## Run Command

Run Command runs commands on managed nodes remotely, at scale, for one-time changes. It is the "run this now" tool.

- **What it runs.** SSM documents, either AWS-provided or yours, issued to one or many nodes.
- **Where from.** The console, AWS CLI, AWS Tools for Windows PowerShell, or the AWS SDKs.
- **Typical uses.** Install or bootstrap applications, run a deployment step, capture logs when a node leaves an Auto Scaling group, or join instances to a Windows domain.
- **Cost.** No additional charge.
- **Consistency.** The Run Command API is eventually consistent, so a command that follows immediately after another may not yet see its effect.
- **Events.** Supported as both an event type and a target type in EventBridge rules.

The first thing Run Command asks for is the **document**, the definition of what to run. The picker shows the document name, owner, and the platforms each one supports, so you filter to something that matches your nodes before you get to parameters.

![Run Command document picker showing AWS-managed command documents and platform types](../../../assets/images/screenshots/ssm/10-ssm-run-command-document.png)

*The Run Command document picker. The table (1) lists documents by name, owner (`Amazon`), and Platform types; `AWS-RunShellScript` supports Linux and macOS, `AWS-ConfigureAWSPackage` supports Windows, Linux, and macOS, and a Windows-only document such as `AWS-ConfigureCloudWatch` cannot run on a Linux node. The **Document version** control (2) lets you pin a specific version instead of the default, which matters when a document has been edited and you need the behavior you tested.*

Once the command runs, the execution page is where you watch it land. Each node reports its own status, so one failing node does not hide the ones that succeeded.

![Run Command execution page showing command status and per-node Success results](../../../assets/images/screenshots/ssm/11-ssm-run-command-output.png)

*The Run Command execution page. **Command status** (1) summarizes the whole invocation (overall status, detailed status, and counts for targets, completed, errors, and delivery timeouts). The **Targets and outputs** table (2) shows the result per node: here two nodes report **Success** and one is still **In Progress**, which is the eventual-consistency behavior described above. **View output** (3) opens the stdout for a single node; without it, the console truncates the output at 24,000 characters.*

## State Manager

State Manager automates the process of keeping managed nodes and other AWS resources in a state you define. Where Run Command acts once, State Manager acts on a schedule until the state holds.

A **State Manager association** is a configuration assigned to targets. It names the document that enforces the state, the targets, and the schedule.

- **Examples of state.** Antivirus installed and running; specific ports closed; a configuration file present. If the state is not met, the association acts to reach it.
- **Scheduling.** Cron and rate expressions, including the `#` (nth weekday of the month) and `L` (last day) modifiers, plus an *offset* in days (useful for running after a patch cycle). By default an association runs immediately on creation and then on schedule; set `ApplyOnlyAtCronInterval` to skip the immediate run. Months are not supported in cron expressions.
- **Targeting.** Tags, AWS Resource Groups, individual node IDs, or all managed nodes in the current account and Region. When you target by tag in the console you can specify a maximum of five tag keys, and all of them must match a node for it to be included; see [17-tagging.md](17-tagging.md) for the tag rules that apply across Run Command, State Manager, and Maintenance Windows.
- **Output.** Command output can be stored in S3.
- **Automation.** To act on resources beyond nodes, State Manager schedules Automation runbooks: for example, attaching an SSM role to instances, enforcing security-group rules, creating DynamoDB backups or EBS snapshots, or starting and stopping instances and RDS databases.
- **Events.** Supported as both an event type and a target type in EventBridge rules.

Creating an association is where the three components come together: a document, the targets, and the schedule. The form states that contract explicitly and names the service-linked role State Manager uses to act on AWS resources.

![Create Association form showing the document, name, and the AWSServiceRoleForAmazonSSM note](../../../assets/images/screenshots/ssm/12-ssm-state-manager-create-association.png)

*The Create Association form. The overview (1) states that an association is a document, targets, and a schedule. The Name field (2) is optional but is what you search on later; an unnamed association appears only by its generated ID. The note about `AWSServiceRoleForAmazonSSM` (3) is the service-linked role State Manager assumes to manage AWS resources on your behalf, which is why some associations need no explicit role in the instance profile.*

## The shared access model

All three tools reach the node the same way, which is why the network diagram looks the same for each: the operator is authorized by IAM, the Systems Manager service sends work, and the agent on the node carries it out over its existing outbound connection. No connection is ever initiated from the service into the node.

```mermaid
flowchart LR
    OP(("Operator"))
    subgraph CLOUD["AWS Cloud"]
      direction TB
      subgraph MGMT["Systems Manager"]
        SM["Session Manager"]:::mgmt
        RC["Run Command"]:::mgmt
        ST["State Manager"]:::mgmt
      end
      subgraph VPC["VPC 10.0.0.0/16"]
        subgraph PRIV["Private subnet, no inbound ports"]
          EC2["EC2 instance<br/>SSM Agent"]:::compute
        end
      end
    end
    OP -->|"IAM-authorized"| SM
    OP -->|"IAM-authorized"| RC
    SM -->|"over the agent channel"| EC2
    RC -->|"over the agent channel"| EC2
    ST -->|"on schedule, over the agent channel"| EC2
    classDef mgmt fill:#E7157B,stroke:#E7157B,color:#ffffff
    classDef compute fill:#ED7100,stroke:#ED7100,color:#ffffff
    classDef actor fill:#232F3E,stroke:#232F3E,color:#ffffff
    class SM,RC,ST mgmt
    class EC2 compute
    class OP actor
    style CLOUD fill:#ffffff,stroke:#232F3E,stroke-width:2px,stroke-dasharray:5 5,color:#232F3E
    style MGMT fill:#ffffff,stroke:#00A4A6,stroke-width:2px,color:#147EBA
    style VPC fill:#ffffff,stroke:#8C4FFF,stroke-width:2px,color:#8C4FFF
    style PRIV fill:#ffffff,stroke:#00A4A6,color:#147EBA
```

Read the arrows from right to left: the instance is the one that holds the connection open, and the service can only send work because the agent keeps that channel alive. The three tool boxes differ only in what they send and when. This is why a node with a stopped agent is unreachable to all three at once, and it is the first thing to check when sessions or commands fail.

## Choosing between them

| Question the scenario asks | Tool |
|----------------------------|------|
| "Open a shell, or tunnel a port, without SSH or a bastion" | Session Manager |
| "Run a command on many nodes once" | Run Command |
| "Keep a configuration applied on an ongoing schedule" | State Manager |
| "Run a high-priority task inside a defined change window" | Maintenance Windows (covered in [06-change-management.md](06-change-management.md)) |

## Examples

Start an interactive session, run a command once, and create an association that runs daily:

```bash
# Interactive shell on a managed node (no SSH, no open inbound port)
aws ssm start-session --target i-0123456789abcdef0

# Run a command once on nodes tagged by environment
aws ssm send-command \
  --document-name "AWS-RunShellScript" \
  --targets "Key=tag:Environment,Values=dev" \
  --parameters 'commands=["sudo yum -y update"]'

# Keep a state applied every day at 03:00 UTC
aws ssm create-association \
  --name "AWS-ConfigureAWSPackage" \
  --targets "Key=tag:OS,Values=linux" \
  --schedule-expression "cron(0 3 * * ? *)"
```

## Sources

- AWS: *AWS Systems Manager Session Manager*. https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html
- AWS: *AWS Systems Manager Run Command*. https://docs.aws.amazon.com/systems-manager/latest/userguide/run-command.html
- AWS: *AWS Systems Manager State Manager*. https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-state.html
- AWS: *Choosing between State Manager and Maintenance Windows*. https://docs.aws.amazon.com/systems-manager/latest/userguide/state-manager-vs-maintenance-windows.html
