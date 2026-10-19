# IAM troubleshooting

This document turns access-denied into a diagnostic chain: confirm the principal, check for an explicit deny, check the allows, then check the boundary, SCP, and conditions. It is a troubleshooting guide, so it assumes the evaluation model in [01-concepts.md](01-concepts.md) and focuses on the tools that show each step of the decision.

> [!TIP]
> Start with the **IAM policy simulator** before any live call. It evaluates the effective permissions of a principal against a specific action and resource ARN and reports allow or deny plus the reason, without you triggering the real request or waiting for CloudTrail. Only when the simulator says "allowed" but the live call still fails do you reach for CloudTrail, the boundary/SCP, and `DecodeAuthorizationMessage`.

The checklist below turns that chain into an ordered flow, so a denial is worked from the top until one step explains it.

```mermaid
flowchart TD
    A["Access denied on action X"] --> B["Confirm the principal running the call (sts get-caller-identity)"]
    B --> C["Check the explicit Deny first (a Deny overrides every Allow)"]
    C --> D["Check identity or resource policy allows it (union)"]
    D --> E["Check a boundary or SCP caps it (intersection)"]
    E --> F["Check conditions (Region, SourceIp, MFA, tag)"]
    F --> G["Check the resource ARN the action targets"]
    classDef deny fill:#DD344C,stroke:#DD344C,color:#ffffff
    classDef step fill:#147EBA,stroke:#147EBA,color:#ffffff
    class A deny
    class B,C,D,E,F,G step
```

Following the flow from the top, you confirm which identity is really making the call, then eliminate the three causes that silently remove access: an explicit deny, a missing allow, and a boundary or SCP cap. The last two steps catch failures specific to one request rather than the whole principal, a condition that did not match and a resource ARN that points somewhere else.

## Diagnose in order

Follow these checks in order. The evaluation chain makes the early steps the most decisive: an explicit deny or a wrong principal explains more failures than a subtle condition later in the chain.

1. **Confirm the principal.** `aws sts get-caller-identity` shows which identity and account the call is actually using. It is often not the one you assumed, a stale `AWS_PROFILE`, an environment variable access key overriding a role, or an instance role instead of a user.
2. **Look for an explicit deny.** A `Deny` anywhere (identity policy, resource policy, permissions boundary, or SCP) overrides every `Allow`. This is the most common cause of a request that "should" be allowed but isn't.
3. **Check for an allow.** If nothing explicitly allows the action, the implicit deny applies. Remember that identity and resource policies combine as a union for same-account access, so an allow in either one is enough.
4. **Check the boundary and SCP.** These are intersections: even with a valid allow, the action must also be permitted by the permissions boundary and by any SCP on the account.
5. **Check conditions.** A condition that fails blocks an otherwise-allowed action, `aws:RequestedRegion`, `aws:SourceIp`, `aws:MultiFactorAuthPresent`, or a resource tag condition.
6. **Check the resource ARN.** A policy that allows `s3:GetObject` but names the wrong bucket ARN will deny the real request.

## Tools

These tools show the decision from different angles: one simulates the policy, one records the actual call, and one analyzes the resource policy for external access.

- **IAM policy simulator**, evaluates a policy set against a specific action and resource without making a live call. First stop for "why is this denied."
- **CloudTrail**, records the API call, the principal, and whether access was denied. Search for the error code (`AccessDenied`) and the caller identity.
- **IAM Access Analyzer**, finds policies that grant external access to a resource; it also validates policy syntax and IAM grammar.
- **`DecodeAuthorizationMessage`**, decodes the encoded authorization failure in an `AccessDenied` response into the reason and the matched policy, which is faster than reproducing the call.

The policy simulator is a console tool rather than a CLI command, and it is usually the fastest way to answer an access question because it makes no live call. The screenshot below shows it loaded with a role as the principal and that role's applicable policies pulled in.

![IAM Policy simulator showing a role and the policies that apply to it](../../../assets/images/screenshots/iam/08-iam-policy-simulator-simulation.png)

*The IAM Policy simulator. Pick the principal (1); the simulator loads every policy that applies to it, identity-based, boundary, resource-based, and SCP (2). Add the actions and resources to test, then Simulate (3) to get an allow or deny with the reason, all without making a live call.*

## Common causes

| Symptom | Likely cause |
|---------|--------------|
| Denied even though the policy looks right | An explicit `Deny` elsewhere, or a boundary/SCP |
| Role works in the console but not the CLI | Wrong credential chain; a stale access key in the environment |
| EC2 application can't reach S3 | The instance has no role, the wrong role, or no instance profile |
| Cross-account call fails | The trust policy is missing the caller ARN, or the identity policy is missing the action |
| A new policy still denies | The policy has not propagated yet, or it names the wrong resource ARN |

## The decisive rule

When two policies disagree, **deny wins**. If you see an allow and a deny for the same action, the deny is what AWS enforces. Most "mystery" access failures trace back to an overlooked deny in a permissions boundary, an SCP, or an old inline policy that was never removed.

## Sources

The references below are the official AWS pages behind the behavior and numbers in this document; use them when a value or rule needs checking against the source.

- AWS: *IAM policy simulator*. https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_testing-policies.html
- AWS: *IAM Access Analyzer*. https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html
- AWS: *Logging IAM and AWS STS API calls with CloudTrail*. https://docs.aws.amazon.com/IAM/latest/UserGuide/cloudtrail-integration.html
