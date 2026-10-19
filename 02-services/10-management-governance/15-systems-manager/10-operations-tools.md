# Operations tools

This document covers Explorer and OpsCenter, the two tools that turn Systems Manager's collected data into a dashboard and a work queue. It is the operational-view layer rather than an action layer; the events and metrics that feed them are in [11-monitoring.md](11-monitoring.md).

## Explorer

Explorer is a customizable operations dashboard that reports on your AWS resources and aggregates *OpsData* across accounts and Regions.

- **What it shows.** Metadata about managed nodes; patch compliance from Patch Manager; association compliance from State Manager; and data from supporting services such as AWS Config, Trusted Advisor, Compute Optimizer, and AWS Support (support cases).
- **Widgets.** *Informational widgets* summarize state (instance count, instances by AMI, total noncompliant nodes, support cases). *OpsItem widgets* summarize the work queue (open OpsItem summary, OpsItems by status, OpsItems over time).
- **Filters and grouping.** Every widget can filter by account, Region, and tag, and some widgets group data by those dimensions.
- **Reporting tag keys.** You can nominate up to five tag keys when you set up Explorer; a key that matches a resource generating an OpsItem is carried into that OpsItem. This is how the tag model in [16-tagging.md](16-tagging.md) reaches the reporting layer: the same keys used for targeting become the dimensions you group the operations data by.
- **Display modes.** Single-account/single-Region (default), single-account/multiple-Region (via a resource data sync), and multiple-account/multiple-Region (requires AWS Organizations with All features, aggregating into the management account).
- **Deprecation.** The Explorer page is deprecated as of December 31, 2026; resource data sync moves to OpsCenter, and the operational data stays available through the API and the source service consoles.

## OpsCenter

OpsCenter is a central place to view, investigate, and resolve operational work items, called **OpsItems**, related to AWS resources. Its goal is to reduce mean time to resolution by removing the need to hop between consoles.

- **OpsItems.** Each OpsItem is an operational issue or interruption tied to one or more AWS resources, with a status, a source, and searchable custom data.
- **Automatic creation.** CloudWatch can create an OpsItem when an alarm enters the `ALARM` state, and EventBridge can create one from an event published by any AWS service. OpsItems can also be created manually.
- **Typical triggers.** A CloudWatch alarm on DynamoDB read-write thresholds, EC2 CPU utilization, billing estimated charges, an EC2 status check failure, or EBS disk space; or an EventBridge event from Security Hub CSPM, a DynamoDB throttling event, an Auto Scaling launch failure, a Systems Manager Automation failure, an AWS Health maintenance alert, or an EC2 state change.
- **Context.** Each OpsItem aggregates the resource name and ID, alarm or event details, alarm history and timeline, and data from AWS Config, CloudTrail, and CloudWatch, so the investigation happens in one page.
- **Deduplication.** Specifying related resource ARNs lets OpsCenter use built-in logic to avoid duplicate OpsItems for the same resource.
- **Remediation.** OpsItems offer recommended Systems Manager Automation runbooks to resolve the issue.
- **Integrations and reach.** CloudWatch Application Insights for .NET and SQL Server can create OpsItems, Security Hub CSPM findings can be aggregated, and the public API lets you integrate OpsCenter with existing case-management systems. It works for EC2 instances and on-premises/hybrid managed nodes.

The OpsCenter landing page states the workflow the same four steps an operator follows: wire up the sources, attach remediation, track the queue, run the fix. The first time you open it, choose **Get started** to enable OpsCenter, which creates the service role and the default rules that raise OpsItems automatically; you can disable individual rules afterward in **Settings**, and the workspace is the day-to-day view.

![OpsCenter overview page showing the four-step workflow and the mean-time-to-resolution goal](../../../assets/images/screenshots/ssm/17-ssm-opscenter-overview.png)

*The OpsCenter overview. **How it works** (1) lists configure sources for automatic OpsItem creation, associate remediation actions with OpsItem types, track OpsItems, and execute runbooks. **Get started** (2) opens the sources configuration. The **Improve mean time to resolution** block (3) is the design goal: context from the source service is attached to the OpsItem so the investigation does not require hopping between consoles.*

Once OpsCenter is enabled, the workspace is where the queue lives. It lists every open and in-progress OpsItem with its type, severity, and status, and it is where an operator raises an item that no alarm caught.

![OpsCenter OpsItems workspace listing one open OpsItem](../../../assets/images/screenshots/ssm/19-ssm-opscenter-opsitems-list.png)

*The OpsCenter OpsItems workspace. The **OpsItems (1)** counter (1) is the open and in-progress queue, filtered here to type `/aws/issue`. The row (2) is the manually created item with its severity and status. The **Create OpsItem** button (3) raises an issue by hand, for the work that no CloudWatch alarm or EventBridge event produced.*

Creating an item records the fields that later drive investigation and deduplication.

![Create OpsItem form with the title, source, and severity filled in](../../../assets/images/screenshots/ssm/20-ssm-opscenter-create-opsitem.png)

*The Create OpsItem form. The **Title** (1) labels the issue, and the **Source** (2) records the service or capability that raised it. The **Severity** (3) sets the severity band, from 1 Critical to 4 Low; the optional deduplication string lets OpsCenter collapse repeat items for the same resource.*

Opening an item is the investigation page, where the same resource, its history, and the runbooks that can resolve it sit together.

![OpsItem detail page showing status, related resources, and remediation runbooks](../../../assets/images/screenshots/ssm/21-ssm-opscenter-opsitem-detail.png)

*The OpsItem detail page. The title and the **Open** badge (1) are the status, and the item also carries its severity and source. **Related resources** (2) is where you attach the affected EC2 instance, alarm, or other ARN, which is also what drives deduplication. **Runbooks** (3) lists the Automation documents that can be executed against the item to remediate it, drawn here from the 540 runbooks available in the account.*

The diagram shows how an issue becomes an OpsItem and then a fix. The single funnel is the point: alarms, events, and application insights all land in one queue with context, and a runbook resolves them.

```mermaid
flowchart LR
    CW["CloudWatch alarm<br/>enters ALARM state"]:::mgmt
    EB["EventBridge event"]:::integ
    AI["Application Insights"]:::mgmt
    OC["OpsCenter OpsItem"]:::mgmt
    CTX["Context: Config, CloudTrail, CloudWatch"]:::mgmt
    RB["Automation runbook"]:::mgmt
    RES["AWS resources"]:::compute
    CW --> OC
    EB --> OC
    AI --> OC
    OC --> CTX
    OC --> RB
    RB --> RES
    classDef mgmt fill:#E7157B,stroke:#E7157B,color:#ffffff
    classDef integ fill:#E7157B,stroke:#E7157B,color:#ffffff
    classDef compute fill:#ED7100,stroke:#ED7100,color:#ffffff
    class CW,AI,OC,CTX,RB mgmt
    class EB integ
    class RES compute
```

Read it left to right: a signal becomes an OpsItem, OpsCenter attaches investigation context from Config, CloudTrail, and CloudWatch, and the operator runs an Automation runbook against the resource. This is the Domain 1 remediation pattern: detect with monitoring, centralize with OpsCenter, remediate with Automation.

## Explorer and OpsCenter together

Explorer is the *view*; OpsCenter is the *queue*. Explorer visualizes OpsItems by account, Region, and tag to show where issues concentrate, and links into OpsCenter when an item needs action. A common exam phrasing that points here is "reduce mean time to resolution by viewing, investigating, and remediating issues in one place", which is OpsCenter.

## Example

Create an OpsItem manually and list the open queue:

```bash
# Raise an OpsItem with searchable context
aws ssm create-ops-item \
  --title "High CPU on the web fleet" \
  --source "Custom" \
  --priority 2 \
  --operational-data '{"Environment":{"Value":"prod","Type":"SearchableString"}}'

# List open OpsItems
aws ssm describe-ops-items --filters Key=Status,Values=Open
```

## Sources

The entries below are the AWS documentation pages this document draws on.

- AWS: *AWS Systems Manager Explorer*. https://docs.aws.amazon.com/systems-manager/latest/userguide/Explorer.html
- AWS: *AWS Systems Manager OpsCenter*. https://docs.aws.amazon.com/systems-manager/latest/userguide/OpsCenter.html
