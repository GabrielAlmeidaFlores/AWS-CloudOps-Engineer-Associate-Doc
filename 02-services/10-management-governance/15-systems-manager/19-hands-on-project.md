# Hands-on project: operate a small fleet end to end

This is the topic's practice project. It takes the Systems Manager capabilities documented in this folder and wires them into one fleet workflow: managed nodes and the instance role, tagging, Resource Groups, Parameter Store, Inventory with a resource data sync, Patch Manager with a patch group, Run Command, State Manager, Session Manager, Distributor, AppConfig, Automation, a Maintenance Window, Compliance, OpsCenter, and Fleet Manager. Nothing depends on it; it depends only on this topic.

## Goal

Take two EC2 instances from unmanaged to a fully operated fleet: patched, inventoried, configured from Parameter Store, managed by runbooks, and observable, all through Systems Manager instead of a login.

## What you build

A two-node fleet sharing one patch group, one resource group, and one configuration store, driven by Systems Manager.

```mermaid
flowchart LR
    subgraph CLOUD["AWS Cloud"]
      direction TB
      subgraph REGION["Region us-east-2"]
        subgraph VPC["VPC 10.0.0.0/16"]
          subgraph PRIV["Private subnet"]
            N1["Node A<br/>SSM Agent Online"]:::compute
            N2["Node B<br/>SSM Agent Online"]:::compute
          end
        end
        ROLE["IAM role<br/>AmazonSSMManagedInstanceCore"]:::security
        PS["Parameter Store<br/>/lab/config"]:::mgmt
        INV["Inventory"]:::mgmt
        PM["Patch Manager<br/>custom baseline"]:::mgmt
        MW["Maintenance Window"]:::mgmt
        AUTO["Automation runbook"]:::mgmt
        DIST["Distributor package"]:::mgmt
        OC["OpsCenter OpsItem"]:::mgmt
        COMP["Compliance"]:::mgmt
      end
    end
    ROLE -.->|"attached"| N1
    ROLE -.->|"attached"| N2
    PS -->|"read config"| N1
    N1 --> INV
    N2 --> INV
    PM -->|"scan and install"| N1
    PM -->|"scan and install"| N2
    MW -->|"schedules"| PM
    AUTO -->|"acts on"| N1
    DIST -->|"installs on"| N2
    N1 --> COMP
    N2 --> COMP
    COMP --> OC
    classDef compute fill:#ED7100,stroke:#ED7100,color:#ffffff
    classDef mgmt fill:#E7157B,stroke:#E7157B,color:#ffffff
    classDef security fill:#DD344C,stroke:#DD344C,color:#ffffff
    style CLOUD fill:#ffffff,stroke:#232F3E,stroke-width:2px,stroke-dasharray:5 5,color:#232F3E
    style REGION fill:#ffffff,stroke:#00A4A6,stroke-width:2px,color:#147EBA
    style VPC fill:#ffffff,stroke:#8C4FFF,stroke-width:2px,color:#8C4FFF
    style PRIV fill:#ffffff,stroke:#00A4A6,color:#147EBA
```

## Concepts covered

| Capability | Document | Where it appears in the build |
|------------|----------|-------------------------------|
| Managed nodes and the instance role | [01-fundamentals.md](01-fundamentals.md) | Step 1 |
| Default Host Management Configuration | [01-fundamentals.md](01-fundamentals.md) | The alternative to an explicit role |
| Fleet Manager | [02-node-tools.md](02-node-tools.md) | Validation |
| Compliance | [02-node-tools.md](02-node-tools.md) | Validation |
| Inventory and resource data sync | [02-node-tools.md](02-node-tools.md) | Step 4 |
| Run Command | [03-session-run-state.md](03-session-run-state.md) | Step 5 |
| State Manager | [03-session-run-state.md](03-session-run-state.md) | Step 6 |
| Session Manager | [03-session-run-state.md](03-session-run-state.md) | Step 7 |
| Patch Manager and baselines | [04-patch-manager.md](04-patch-manager.md) | Step 8 |
| Distributor | [05-distributor.md](05-distributor.md) | Step 9 |
| Automation, Maintenance Windows, Documents | [06-change-management.md](06-change-management.md) | Steps 10 and 11 |
| Parameter Store | [07-parameter-store.md](07-parameter-store.md) | Step 3 |
| AppConfig | [08-application-tools.md](08-application-tools.md) | Step 12 |
| Resource Groups | [09-resource-groups.md](09-resource-groups.md) | Step 2 |
| OpsCenter and Explorer | [10-operations-tools.md](10-operations-tools.md) | Step 13 |
| Tagging and tag-based targeting | [16-tagging.md](16-tagging.md) | Everywhere a target is set |

## Prerequisites

- Read [01-fundamentals.md](01-fundamentals.md), [04-patch-manager.md](04-patch-manager.md), and [16-tagging.md](16-tagging.md) first.
- Two EC2 instances running a supported Linux AMI with the SSM Agent and an instance role that includes `AmazonSSMManagedInstanceCore` (or Default Host Management Configuration enabled). A private subnet needs a NAT route or VPC endpoints for `ssm`, `ssmmessages`, and `ec2messages`.
- AWS CLI configured for `us-east-2`.

## Steps

1. **Confirm both nodes are managed.** If a node is missing, work the four layers in [12-troubleshooting.md](12-troubleshooting.md): agent, role, network, IMDS.

   ```bash
   aws ssm describe-instance-information \
     --query 'InstanceInformationList[].[InstanceId,PingStatus,AgentVersion]' --output table
   ```

2. **Tag both nodes and build a resource group.** Tags drive targeting and the group; the group is a reusable target that follows membership.

   ```bash
   aws ec2 create-tags --resources i-AAA i-BBB --tags Key=Env,Value=lab Key="Patch Group",Value=LAB
   aws resource-groups create-group --name lab-fleet \
     --resource-query '{"Type":"TAG_FILTERS_1_0","Query":"{\"ResourceTypeFilters\":[\"AWS::EC2::Instance\"],\"TagFilters\":[{\"Key\":\"Env\",\"Values\":[\"lab\"]}]}"}'
   ```

3. **Store configuration in Parameter Store.** A plain value and an encrypted value the nodes will read.

   ```bash
   aws ssm put-parameter --name "/lab/config/log-level" --value "info" --type String
   aws ssm put-parameter --name "/lab/config/api-token" --value "example-token" --type SecureString
   ```

4. **Collect inventory on a schedule** and centralize it with a resource data sync.

   ```bash
   aws ssm create-association --name "AWS-GatherSoftwareInventory" \
     --targets "Key=tag:Env,Values=lab" --schedule-expression "rate(1 day)"
   aws ssm create-resource-data-sync --sync-name lab-inventory \
     --s3-destination '{"BucketName":"example-ssm-inventory-111122223333","SyncType":"SyncFromSource","SyncSource":{"SourceType":"AWS::SSM::ManagedInstanceInventory"}}'
   ```

5. **Run a command once across the fleet** with Run Command, targeting the tag.

   ```bash
   aws ssm send-command --document-name "AWS-RunShellScript" \
     --targets "Key=tag:Env,Values=lab" \
     --parameters 'commands=["hostname","uptime"]'
   ```

6. **Enforce a state on a schedule** with State Manager so a setting self-heals.

   ```bash
   aws ssm create-association --name "AWS-ConfigureAWSPackage" \
     --targets "Key=tag:Env,Values=lab" \
     --parameters 'action=Install,name=AmazonCloudWatchAgent' \
     --schedule-expression "rate(7 days)"
   ```

7. **Open a shell with no inbound port** using Session Manager.

   ```bash
   aws ssm start-session --target i-AAA
   ```

8. **Patch by group.** Create a custom baseline, register the patch group, and scan. The node resolves to the baseline through its `Patch Group` tag.

   ```bash
   aws ssm create-patch-baseline --name "lab-baseline" --operating-system AMAZON_LINUX_2023 \
     --approval-rules '{"PatchRules":[{"PatchFilterGroup":{"PatchFilters":[{"Key":"CLASSIFICATION","Values":["Security","Bugfix"]}]},"ApproveAfterDays":7,"ComplianceLevel":"HIGH"}]}'
   aws ssm register-patch-baseline-for-patch-group --baseline-id pb-0c10e65780EXAMPLE --patch-group LAB
   aws ssm send-command --document-name "AWS-RunPatchBaseline" \
     --targets "Key=tag:Patch Group,Values=LAB" --parameters 'Operation=Scan'
   ```

9. **Deploy a versioned artifact** with Distributor through the AWS-managed package document.

   ```bash
   aws ssm send-command --document-name "AWS-ConfigureAWSPackage" \
     --targets "Key=tag:Env,Values=lab" \
     --parameters 'action=Install,name=AWSPVDriver'
   ```

10. **Run a runbook** with Automation, using rate control so the rollout is bounded.

    ```bash
    aws ssm start-automation-execution --document-name "AWS-RunPatchBaseline" \
      --parameters 'Operation=Scan' --max-concurrency "50%" --max-errors "1"
    ```

11. **Schedule the patching** inside a bounded Maintenance Window and gate it with a Change Calendar.

    ```bash
    aws ssm create-maintenance-window --name "lab-weekly-patch" \
      --schedule "cron(0 3 ? * SUN *)" --duration 3 --cutoff 1 --allow-unassociated-targets
    aws ssm create-document --name "lab-freeze" --document-type "ChangeCalendar" \
      --content 'BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//AWS//Change Calendar//EN
END:VCALENDAR'
    ```

12. **Serve validated configuration** with AppConfig so a bad change rolls back.

    ```bash
    aws appconfig create-application --name lab-app
    aws appconfig create-configuration-profile --application-id APP-ID --name lab-profile \
      --location-uri ssm-document://lab-config
    ```

13. **Raise an OpsItem** for a fleet issue so it lands in the OpsCenter queue with context.

    ```bash
    aws ssm create-ops-item --title "Lab fleet needs an audit" --source "Custom" --priority 3
    ```

## How it works

Patching is the clearest flow, because it shows the tag-to-baseline path and the two ways to trigger it. The node's `Patch Group` tag selects the baseline; the operation is either a one-time Run Command or a scheduled Maintenance Window task, and both end at the same compliance report.

```mermaid
flowchart TD
    A["Node tagged Patch Group = LAB"] --> B["Patch group LAB"]
    B --> C["Custom baseline lab-baseline"]
    C --> D{"Trigger?"}
    D -->|"Run Command now"| E["AWS-RunPatchBaseline Scan"]
    D -->|"Maintenance Window"| F["Scheduled AWS-RunPatchBaseline"]
    E --> G["Compliance report"]
    F --> G
    G --> H["Security Hub CSPM and AWS Config"]
    classDef step fill:#147EBA,stroke:#147EBA,color:#ffffff
    classDef decision fill:#FF9900,stroke:#FF9900,color:#232F3E
    classDef ok fill:#7AA116,stroke:#7AA116,color:#ffffff
    class A,B,C,E,F step
    class D decision
    class G,H ok
```

Targeting is the second flow. Every task points at the same tag, so membership changes with the tag, not with an edited list: retag a node and it joins or leaves every association, command, and patch run at once.

```mermaid
flowchart LR
    TAG["Tag Env = lab"] --> RC["Run Command"]
    TAG --> ST["State Manager association"]
    TAG --> PM["Patch Manager group"]
    TAG --> ARG["Resource group lab-fleet"]
    classDef step fill:#147EBA,stroke:#147EBA,color:#ffffff
    class TAG,RC,ST,PM,ARG step
```

## Validation

1. **Fleet health.** Both nodes are `Online` with a current agent version in Fleet Manager.

   ```bash
   aws ssm describe-instance-information --query 'InstanceInformationList[].{Id:InstanceId,Status:PingStatus}' --output table
   ```

2. **Compliance.** The nodes report patch and association status.

   ```bash
   aws ssm list-compliance-summaries --query 'ComplianceSummaryItems[].{Type:ComplianceType,Compliant:CompliantSummary.CompliantCount,NonCompliant:NonCompliantSummary.NonCompliantCount}' --output table
   ```

3. **Inventory.** The association is `Success` and inventory is returned.

   ```bash
   aws ssm get-inventory --query 'Entities[].Id' --output text
   ```

4. **Parameter read from a node.** In a Session Manager shell, read the parameter with the AWS CLI using the instance role.

   ```bash
   aws ssm get-parameter --name "/lab/config/log-level" --with-decryption --query Parameter.Value
   ```

## Failure injection

- **Lost tag.** Remove the `Patch Group` tag from one node and re-scan; it falls to the OS default baseline, the fallback path [04-patch-manager.md](04-patch-manager.md) describes.
- **Broken registration.** Detach the instance role on one node and watch it drop to unmanaged, the first failure in [12-troubleshooting.md](12-troubleshooting.md).
- **Association without tag.** Target an association at a tag no node carries and confirm it matches zero nodes, which is the AND rule in [16-tagging.md](16-tagging.md).
- **Missing KMS permission.** Remove `kms:Decrypt` from the node role and confirm the `SecureString` read fails after the parameter is found.

## Cleanup

```bash
aws ssm delete-association --association-id ASSOC-EXAMPLE     # repeat for each association
aws ssm delete-resource-data-sync --sync-name lab-inventory
aws ssm deregister-patch-baseline-for-patch-group --baseline-id pb-0c10e65780EXAMPLE --patch-group LAB
aws ssm delete-patch-baseline --baseline-id pb-0c10e65780EXAMPLE
aws ssm delete-maintenance-window --window-id mw-EXAMPLE
aws ssm delete-document --name lab-freeze
aws appconfig delete-application --application-id APP-ID
aws resource-groups delete-group --group-name lab-fleet
aws ssm delete-parameter --name "/lab/config/log-level"
aws ssm delete-parameter --name "/lab/config/api-token"
aws ec2 delete-tags --resources i-AAA i-BBB --tags Key=Env Key="Patch Group"
```

## What it practices

- **Domain 1, Task 1.1 (monitoring and logging):** Fleet Manager, Inventory, Compliance, and OpsCenter.
- **Domain 1, Task 1.2 (remediation):** Automation, EventBridge-driven remediation, and OpsCenter follow-up.
- **Domain 3, Task 3.1 (provision and maintain):** patch baselines, State Manager associations, Distributor, and Maintenance Windows.
- **Domain 3, Task 3.2 (automation):** runbooks and event-driven automation.
- **Domain 4 (compliance and secrets):** patch compliance and `SecureString` storage.

## Sources

- AWS: *AWS Systems Manager User Guide*. https://docs.aws.amazon.com/systems-manager/latest/userguide/
- AWS: *Patch Manager*. https://docs.aws.amazon.com/systems-manager/latest/userguide/patch-manager.html
- AWS: *Maintenance Windows*. https://docs.aws.amazon.com/systems-manager/latest/userguide/maintenance-windows.html
- AWS: *AWS AppConfig*. https://docs.aws.amazon.com/appconfig/latest/userguide/what-is-appconfig.html
