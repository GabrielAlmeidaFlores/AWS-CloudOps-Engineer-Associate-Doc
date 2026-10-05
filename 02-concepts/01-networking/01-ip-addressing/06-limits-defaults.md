# IP addressing limits and defaults

## Must remember

| Item | Value |
|------|-------|
| IPv4 address size | 32 bits |
| Addresses in a block | `2^(32 − n)` |
| VPC IPv4 CIDR range | `/16` (65,536) to `/28` (16) |
| Subnet IPv4 CIDR range | `/28` (16) to `/16` (65,536) |
| Reserved per IPv4 subnet | **5** |
| Usable addresses in a subnet | `2^(32 − n) − 5` |
| Minimum subnet | `/28` (16 addresses, 11 usable) |

## Reserved addresses per subnet

Example subnet `10.0.0.0/24`:

| Address | Reserved for |
|---------|--------------|
| `10.0.0.0` | Network address |
| `10.0.0.1` | VPC router |
| `10.0.0.2` | DNS (VPC base + 2) |
| `10.0.0.3` | Future use |
| `10.0.0.255` | Broadcast |

## Address capacity

| Prefix | Addresses | Usable in an AWS subnet |
|--------|-----------|-------------------------|
| `/16` | 65,536 | 65,531 |
| `/20` | 4,096 | 4,091 |
| `/24` | 256 | 251 |
| `/25` | 128 | 123 |
| `/27` | 32 | 27 |
| `/28` | 16 | 11 |

## Good to know

- **RFC 1918:** `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`.
- **Prohibited VPC ranges:** `0.0.0.0/8`, `127.0.0.0/8`, `169.254.0.0/16`, `224.0.0.0/4`.
- **Service-reserved range to avoid:** `172.17.0.0/16` (Cloud9, SageMaker AI).
- **IPv6 (VPC):** an Amazon-provided `/56`; subnets use `/64`. (Detailed in [IPv4 vs IPv6](../02-ipv4-ipv6/README.md).)
- AWS canonicalizes CIDRs: `100.68.0.18/18` becomes `100.68.0.0/18`.

## Sources

- AWS — *VPC CIDR blocks*. https://docs.aws.amazon.com/vpc/latest/userguide/vpc-cidr-blocks.html
- AWS — *Subnet CIDR blocks*. https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html
