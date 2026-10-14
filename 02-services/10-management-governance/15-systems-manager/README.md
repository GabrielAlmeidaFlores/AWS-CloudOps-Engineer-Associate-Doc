# AWS Systems Manager (SSM)

AWS Systems Manager (SSM) is the operations hub for your compute. It gives you one place to view and act on *managed nodes* (EC2 instances, edge devices, on-premises servers, and VMs) across accounts and Regions: run commands, open shell sessions without SSH, patch operating systems, keep software in a known state, store configuration and secrets, and automate remediation. The unifying idea is simple: install the SSM Agent on a node, give it an IAM role, and the node registers with Systems Manager; from then on you operate it remotely through AWS instead of logging in.

## What Systems Manager is

Systems Manager manages two concerns in one service:

- **Node operations.** A fleet view, inventory, patching, remote command and session access, and state enforcement for the machines you run.
- **Operational automation.** Runbooks, maintenance windows, parameter storage, and event-driven remediation that act across AWS resources, not only nodes.

The unified console groups those tools in its left navigation, which is the map this documentation follows. The screenshot below is the Systems Manager home page in the sandbox account.

![Systems Manager home page with the tool groups in the left navigation](../../../assets/images/screenshots/ssm/01-ssm-home-tool-groups.png)

*The Systems Manager home page. The left navigation groups the tools into Node Tools (Compliance, Distributor, Fleet Manager, Hybrid Activations, Inventory, Patch Manager, Run Command, Session Manager, State Manager), Change Management Tools (Automation, Change Calendar, Documents, Maintenance Windows, Quick Setup), and Application Tools. The numbered documents in this folder follow that grouping.*

Systems Manager is **regional**. A managed node registers with the Systems Manager service in its own Region; it is not managed from another Region's service. Feature coverage is broad but not identical in every Region.

It is effectively a **free service**: AWS does not charge for using Systems Manager itself. You pay for the resources it acts on and for a few optional features that carry their own pricing, such as Parameter Store *advanced* parameters and Automation steps beyond the free tier.

## SOA-C03 relevance

Systems Manager is in scope under **Management and Governance**, and it appears across three domains:

- **Domain 1, Task 1.2**: Skill 1.2.1 (analyze metrics and automate remediation with services such as Systems Manager) and Skill 1.2.3 (create or run custom and predefined Systems Manager Automation runbooks) make SSM a first-class remediation tool.
- **Domain 3, Task 3.2**: Skill 3.2.1 (use AWS services such as Systems Manager to automate operational processes) and Skill 3.2.2 (event-driven automation).
- **Domain 4**: patch and compliance management (Patch Manager, Compliance) and Skill 4.2.4 (securely store secrets, which Parameter Store serves alongside Secrets Manager).

The canonical Systems Manager documentation lives here; domain and cross-service pages link back rather than repeat it.

## Topic mind map

Systems Manager at a glance: it operates your fleet, so it reads and writes through the surrounding AWS services. The map shows the ones that feed it, watch it, and the nodes it acts on.

```mermaid
flowchart TD
    SSM(("Systems Manager"))
    EC2["EC2 instance"]
    IAM["IAM"]
    CW["CloudWatch"]
    CT["CloudTrail"]
    CFG["AWS Config"]
    EB["EventBridge"]
    S3[("S3")]
    KMS["KMS"]
    SSM -->|"runs work on"| N1["agent dials out on 443, no inbound port"]:::note --> EC2
    IAM -->|"authorizes"| N2["role needs ssm:UpdateInstanceInformation"]:::note --> EC2
    SSM -->|"emits"| N3["metrics and session logs"]:::note --> CW
    SSM -->|"logs to"| CT
    CFG -->|"remediates via"| N4["Config rule runs an Automation runbook"]:::note --> SSM
    EB -->|"starts"| N5["event or schedule runs a runbook"]:::note --> SSM
    SSM -->|"writes"| S3
    SSM -->|"reads"| N6["SecureString needs GetParameter and Decrypt"]:::note --> KMS
    classDef mgmt fill:#E7157B,stroke:#E7157B,color:#ffffff
    classDef compute fill:#ED7100,stroke:#ED7100,color:#ffffff
    classDef storage fill:#7AA116,stroke:#7AA116,color:#ffffff
    classDef security fill:#DD344C,stroke:#DD344C,color:#ffffff
    classDef actor fill:#232F3E,stroke:#232F3E,color:#ffffff
    classDef note fill:#FFF4E5,stroke:#FF9900,color:#232F3E
    class SSM,CFG,EB,CW,CT mgmt
    class EC2 compute
    class S3 storage
    class IAM,KMS security
```

Read the map outward from Systems Manager: it runs commands and patches on EC2 managed nodes that carry its agent, and an IAM instance role authorizes them to register. It emits metrics and session logs to CloudWatch and its API calls to CloudTrail, while AWS Config and EventBridge feed back in as remediation and triggers. The note blocks on the links mark the detail that decides an exam answer, such as the outbound-only agent channel, the registration permission a node must have, and the two permissions a `SecureString` read needs. The `## Document index` below carries the links to this topic's documents.

## Document index (read in this order)

1. [01-fundamentals.md](01-fundamentals.md): the SSM Agent, managed nodes, the instance IAM role, and Default Host Management Configuration.
2. [02-node-tools.md](02-node-tools.md): Fleet Manager, Compliance, Inventory, and Hybrid Activations.
3. [03-session-run-state.md](03-session-run-state.md): Session Manager, Run Command, and State Manager.
4. [04-patch-manager.md](04-patch-manager.md): Patch Manager, patch baselines, and patch groups.
5. [05-distributor.md](05-distributor.md): Distributor packages.
6. [06-change-management.md](06-change-management.md): Automation, Change Calendar, Maintenance Windows, Documents, and Quick Setup.
7. [07-parameter-store.md](07-parameter-store.md): Parameter Store, its tiers, and parameter policies.
8. [08-application-tools.md](08-application-tools.md): Application Manager and AppConfig.
9. [09-resource-groups.md](09-resource-groups.md): Resource Groups.
10. [10-operations-tools.md](10-operations-tools.md): Explorer and OpsCenter.
11. [11-monitoring.md](11-monitoring.md): CloudWatch, CloudTrail, and Config integration.
12. [12-troubleshooting.md](12-troubleshooting.md): diagnosing nodes that will not register or run.
13. [13-comparisons.md](13-comparisons.md): the distinctions that decide exam answers.
14. [14-limits-defaults.md](14-limits-defaults.md): quotas, defaults, and numbers that matter.
15. [15-quick-review.md](15-quick-review.md): the must-know summary.
16. [16-tagging.md](16-tagging.md): the tag model, `tag:` targeting, the `Patch Group` key, and taggable resources.
17. [17-exam-questions.md](17-exam-questions.md): twelve original SOA-C03 practice questions covering this topic.
18. [18-exam-traps.md](18-exam-traps.md): recurring misconceptions.
19. [19-hands-on-project.md](19-hands-on-project.md): a project that onboards a node, patches it by group, and inventories it.

Each document ends with its own `Sources` section; there is no separate `sources.md`.

## Relationship map

- **Depends On**, EC2 (managed nodes), IAM (the instance role and caller permissions), and the Systems Manager service endpoints the agent contacts.
- **Integrates With**, CloudWatch (metrics and dashboards), AWS Config (compliance records and remediation), EventBridge (event-driven automation), CloudFormation (parameter and resource provisioning), and Secrets Manager (secret storage).
- **Monitored By**, CloudWatch, AWS Config, Systems Manager Compliance, and OpsCenter.
- **Secured By**, IAM (instance role plus caller policies), KMS (Parameter Store `SecureString`), and VPC endpoints for private access without the public internet.
- **Automated By**, EventBridge, Maintenance Windows, AWS Config remediation, and Automation runbooks.

See also (these documents are planned, not yet created):

- Domain 1: Monitoring, Logging, and Remediation
- Domain 3: Deployment, Provisioning, and Automation
- Domain 4: Security and Compliance
- EC2 + Systems Manager (cross-service)

## Sources

- AWS: *What is AWS Systems Manager?*. https://docs.aws.amazon.com/systems-manager/latest/userguide/what-is-systems-manager.html
- AWS: *Working with SSM Agent*. https://docs.aws.amazon.com/systems-manager/latest/userguide/ssm-agent.html
- AWS: *SOA-C03 exam guide (local copy)*, Content Domains 1, 3, and 4. `assets/docs/soa-c03-exam-guide.pdf`
- AWS: *AWS Certified CloudOps Engineer - Associate*. https://aws.amazon.com/certification/certified-cloudops-engineer-associate/
