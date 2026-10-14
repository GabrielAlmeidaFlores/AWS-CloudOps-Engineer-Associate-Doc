# Systems Manager limits and defaults

Values verified against the AWS Systems Manager endpoints and quotas page and the per-tool documentation. The behavioral defaults matter more than the quota ceilings for the exam; the quotas appear when a scenario asks why something stopped working at scale.

## Must remember

| Item | Value | Why it matters |
|------|-------|----------------|
| Managed nodes per account per Region | 2,400 default | Default safe fleet size; exceeding it can drop nodes from Systems Manager |
| Run Command / State Manager / Maintenance Windows | Free | No per-action charge |
| Session Manager on EC2 | Free | Pay-as-you-go applies on **hybrid** nodes from September 30, 2026 |
| Automation free tier | Removed for new customers (Aug 14, 2025); ended for existing (Dec 31, 2025) | Automation is now billable |
| Automation max run time in a user context | 12 hours | Longer runs must use a service role |
| `aws:executeScript` max run time | 10 minutes | Split long scripts into steps |
| Parameter Store Standard | 10,000 parameters, 4 KB, no policies, free | The default tier |
| Parameter Store Advanced | 100,000 parameters, 8 KB, policies, shareable, billed, not downgradeable | The expensive tier |
| Parameter Store versions retained | 100 | How far back you can reconstruct a value |
| Inventory minimum collection interval | 30 minutes | The shortest schedule |
| Inventory data retention | 30 days | Use Config or S3 for longer retention |
| Session idle timeout | 20 minutes default (1-60 configurable) | Why a session drops |
| State Manager associations | 2,000 default; 20 per node | Scale ceiling |
| Patch baselines | 50 default; 25 patch groups per baseline | Scale ceiling |
| Maintenance windows | 50; 20 tasks and 100 targets each | Scale ceiling |
| OpsItems | 10,000 per account per month; 500,000 max | Security Hub OpsItems are not bound by the 500,000 cap |
| Document size | 64 KB; 500 documents; 1,000 versions each | Limits for custom documents |
| `GetCalendarState` | 10 requests per second | Change Calendar query rate |

## Good to know

- **SSM Agent communication ports.** Outbound HTTPS (TCP 443) to `ssm.*`, `ssmmessages.*`, and `ec2messages.*`. No inbound ports are required.
- **Minimum agent versions.** Session Manager needs 2.3.68.0 or later; Default Host Management Configuration needs 3.2.582.0 or later; environment-variable interpolation in documents needs 3.3.2746.0 or later.
- **Hybrid node prefixes.** `mi-` for hybrid-activated nodes, `i-` for EC2 instances.
- **Hybrid managed node count.** Was capped by the advanced-instances tier; the tier was removed on June 30, 2026, removing the 1,000-node limit.
- **Automation concurrency.** 100 concurrent default, up to 500 with adaptive concurrency; 25 concurrent rate-control automations; a queue of 1,000 or 5,000 depending on type; 5 levels of nested runbooks.
- **Distributor.** 500 packages, 25 versions per package, 20 GB package size, 20 attachments, 64 KB manifest.
- **Fleet Manager RDP.** 5 concurrent sessions default, 60-minute maximum duration, 10-minute idle timeout (Microsoft licensing limits concurrent RDP).
- **Parameter Store throughput.** Default 40 TPS shared across `GetParameter`, `GetParameters`, and `GetParametersByPath`; higher throughput is billed and can reach 10,000 TPS for `GetParameter`. `SecureString` reads are further bounded by KMS throughput.
- **Explorer / Inventory resource data syncs.** 5 each.
- **Enabling higher throughput or the advanced tier incurs charges.** Treat these as cost decisions, not just configuration.

## How to read a quota

Quotas are per account and per Region unless stated otherwise, and most can be raised through Service Quotas. When a scenario reports that a Systems Manager feature stopped working at a specific scale, check whether the applicable quota was reached before inspecting the configuration: hitting the managed-node, association, or patch-baseline default is a common cause.

## Sources

- AWS: *AWS Systems Manager endpoints and quotas*. https://docs.aws.amazon.com/general/latest/gr/ssm.html
- AWS: *AWS Systems Manager Parameter Store quotas*. https://docs.aws.amazon.com/general/latest/gr/ssm.html#parameter-store
- AWS: *AWS Systems Manager pricing*. https://aws.amazon.com/systems-manager/pricing/
