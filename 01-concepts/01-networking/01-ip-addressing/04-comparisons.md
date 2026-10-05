# IP addressing comparisons

## CIDR vs subnet mask

CIDR and a subnet mask express the same idea (how many leading bits identify the network) in two different syntaxes. A subnet mask writes the boundary in dotted-decimal; CIDR writes it as a prefix length. AWS uses CIDR notation everywhere (console, CLI, API, CloudFormation), so read it directly rather than converting.

| CIDR | Subnet mask | Network bits | Host bits |
|------|-------------|--------------|-----------|
| `/16` | `255.255.0.0` | 16 | 16 |
| `/24` | `255.255.255.0` | 24 | 8 |
| `/28` | `255.255.255.240` | 28 | 4 |

To convert in your head: each `255` octet is 8 network bits. A final octet of `240` is `11110000`, which adds 4 network bits, so `255.255.255.240` is a `/28`.

## Public vs private IP

The public/private distinction decides whether a resource can be reached from the internet and how it is billed.

| Attribute | Public IP | Private IP |
|-----------|-----------|------------|
| Reachable from internet | Yes | No, only inside the VPC or connected networks |
| Assigned from | AWS public pool, or an Elastic IP you keep | The VPC CIDR (typically RFC 1918) |
| Persistence | An auto-assigned public IP changes on stop/start; an Elastic IP is static | Persists for the life of the resource |
| Cost | An hourly charge applies to every public IPv4 address, attached or idle | Free |
| Typical use | Bastion hosts, internet-facing load balancers, NAT gateways | Application servers, databases, endpoints in private subnets |

Two details decide exam answers. First, a public IP on an instance is not the instance's identity, stopping and starting the instance replaces an auto-assigned address unless you attached an Elastic IP. Second, since 2024 every public IPv4 address is billed per hour whether or not it is in use, so an idle Elastic IP is a cost, not a free reservation. Instances in a private subnet hold no public IP at all; their outbound internet traffic passes through a NAT gateway.

## /28 vs /24 vs /16

The prefix you choose is a sizing decision: start from the number of resources, add the 5 reserved addresses, and round up.

| Prefix | Addresses | Usable in an AWS subnet | Typical use |
|--------|-----------|-------------------------|-------------|
| `/16` | 65,536 | 65,531 | A whole VPC |
| `/24` | 256 | 251 | A standard subnet holding many instances |
| `/28` | 16 | 11 | The smallest allowed subnet, a few instances or a small endpoint subnet |

A `/16` is a common VPC size because it leaves room to carve many `/24` subnets across Availability Zones. A `/28` exists mainly to satisfy AWS's minimum; using it for a workload that grows is a trap, because subnets cannot be resized.

## Sources

- AWS: *IP addressing for your VPCs and subnets*. https://docs.aws.amazon.com/vpc/latest/userguide/vpc-ip-addressing.html
- AWS: *Subnet CIDR blocks*. https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html
- AWS: *New – AWS Public IPv4 Address Charge + Public IP Insights*. https://aws.amazon.com/blogs/aws/new-aws-public-ipv4-address-charge-public-ip-insights/
