# IP addressing limits and defaults

These are the values that decide sizing and connectivity questions. The first table is what the exam expects you to recall without thinking; the rest is operational context. Every value is verified against current AWS documentation.

## Must remember

| Item | Value | Why it matters |
|------|-------|----------------|
| IPv4 address size | 32 bits | The basis of every `2^(32 − n)` calculation |
| Addresses in a block | `2^(32 − n)` | `/24` = 256, `/16` = 65,536, `/28` = 16 |
| VPC IPv4 CIDR range | `/16` (65,536) to `/28` (16) | Smaller or larger blocks are rejected at creation |
| Subnet IPv4 CIDR range | `/28` (16) to `/16` (65,536) | A subnet can match the whole VPC or be a subset of it |
| Reserved per IPv4 subnet | **5** | The five addresses AWS withholds before you can use any |
| Usable addresses in a subnet | `2^(32 − n) − 5` | Not `− 2`; the extra three are the AWS reservations |
| Minimum subnet | `/28` (16 addresses, 11 usable) | There is no smaller subnet |

## Reserved addresses per subnet

AWS withholds five addresses in every IPv4 subnet because the subnet needs them to function. For a `10.0.0.0/24` subnet:

| Address | Reserved for | Used for |
|---------|--------------|----------|
| `10.0.0.0` | Network address | Identifies the subnet block; never assigned |
| `10.0.0.1` | VPC router | The subnet's default gateway for routed traffic |
| `10.0.0.2` | DNS | Amazon Route 53 Resolver, at the VPC range base + 2 |
| `10.0.0.3` | Future use | Held by AWS; not assignable |
| `10.0.0.255` | Broadcast | IPv4 broadcast is unsupported, but the address is held |

A `/24` therefore yields 251 usable addresses and a `/28` yields 11.

## Address capacity

| Prefix | Addresses | Usable in an AWS subnet |
|--------|-----------|-------------------------|
| `/16` | 65,536 | 65,531 |
| `/20` | 4,096 | 4,091 |
| `/24` | 256 | 251 |
| `/25` | 128 | 123 |
| `/27` | 32 | 27 |
| `/28` | 16 | 11 |

## VPC quotas that affect addressing

Defaults are per Region and most are adjustable through Service Quotas.

| Resource | Default | Adjustable to |
|----------|---------|---------------|
| VPCs per Region | 5 | Higher on request (hundreds) |
| Subnets per VPC | 200 | Yes |
| IPv4 CIDR blocks per VPC | 5 | 50 |
| IPv6 CIDR blocks per VPC | 5 | 50 |
| Route tables per VPC | 200 | Yes |
| Routes per route table (non-propagated) | 500 | 1,000 |
| Network ACLs per VPC | 200 | Yes |
| Rules per network ACL (each direction) | 20 | 40 |
| Internet gateways per Region | 5 | Tied to the VPC quota |
| Egress-only internet gateways per Region | 5 | Tied to the VPC quota |
| NAT gateways per Availability Zone | 5 | Yes |
| Elastic IP addresses per Region | 5 | Yes |
| Security groups per Region | 2,500 | Yes |
| Inbound or outbound rules per security group | 60 | Yes |
| Security groups per network interface | 5 | 16 |

The IPv4 CIDR-blocks limit is the one candidates miss: the primary block and every secondary block count against the same quota of five, so a VPC can hold at most five IPv4 ranges by default.

## Good to know

- **RFC 1918:** `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` — the private ranges AWS recommends for VPCs.
- **Prohibited VPC ranges:** `0.0.0.0/8`, `127.0.0.0/8`, `169.254.0.0/16`, `224.0.0.0/4` (multicast).
- **Service-reserved range to avoid:** `172.17.0.0/16` (used internally by Cloud9 and SageMaker AI).
- **IPv6 (VPC):** an Amazon-provided `/56` per VPC, with subnets typically `/64` (covered in [IPv4 vs IPv6](../02-ipv4-ipv6/README.md)).
- **Public IPv4 cost:** every public IPv4 address is billed per hour whether attached or idle, so Elastic IPs are no longer free when unused.
- **Canonicalization:** AWS stores `100.68.0.18/18` as `100.68.0.0/18`.

## Sources

- AWS — *VPC CIDR blocks*. https://docs.aws.amazon.com/vpc/latest/userguide/vpc-cidr-blocks.html
- AWS — *Subnet CIDR blocks*. https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html
- AWS — *Amazon VPC quotas*. https://docs.aws.amazon.com/vpc/latest/userguide/amazon-vpc-limits.html
- AWS — *New – AWS Public IPv4 Address Charge + Public IP Insights*. https://aws.amazon.com/blogs/aws/new-aws-public-ipv4-address-charge-public-ip-insights/
