# IP addressing comparisons

## CIDR vs subnet mask

Same information, two syntaxes.

| CIDR | Subnet mask | Meaning |
|------|-------------|---------|
| `/16` | `255.255.0.0` | 16 network bits |
| `/24` | `255.255.255.0` | 24 network bits |
| `/28` | `255.255.255.240` | 28 network bits |

AWS uses CIDR notation everywhere (console, CLI, API), so prefer it.

## Public vs private IP

| Attribute | Public IP | Private IP |
|-----------|-----------|------------|
| Reachable from internet | Yes | No |
| Assigned from | AWS public pool (or Elastic IP) | VPC CIDR / RFC 1918 |
| Persistence | Auto-assigned changes on stop/start; Elastic IP persists | Persists for the resource's life |
| Cost | Free while attached to a running instance; Elastic IP charged when unattached | Free |
| Typical use | Bastion hosts, public-facing load balancers | Internal instances, databases, private subnets |

## /28 vs /24 vs /16

| Prefix | Addresses | AWS usable (subnet) | Typical use |
|--------|-----------|---------------------|-------------|
| `/16` | 65,536 | 65,531 | Whole VPC |
| `/24` | 256 | 251 | A standard subnet |
| `/28` | 16 | 11 | Smallest allowed subnet |

## Sources

- AWS — *IP addressing for your VPCs and subnets*. https://docs.aws.amazon.com/vpc/latest/userguide/vpc-ip-addressing.html
- AWS — *Subnet CIDR blocks*. https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html
