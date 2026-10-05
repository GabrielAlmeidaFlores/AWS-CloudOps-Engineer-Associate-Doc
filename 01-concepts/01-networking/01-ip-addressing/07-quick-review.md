# IP addressing quick review

> [!NOTE]
> This is the last thing you read before the exam — a one-page gate. If any line below isn't instantly obvious, go back to the source document: the math is in `01-concepts.md`, the AWS rules in `02-aws-addressing.md`, and the numbers in `06-limits-defaults.md`.

## Non-negotiables

- **Addresses in a block** = `2^(32 − n)`. A `/24` holds 2^8 = 256 addresses; a `/28` holds 2^4 = 16.
- **Usable in an AWS subnet** = `2^(32 − n) − 5`. AWS reserves five addresses in every subnet — not the two (network and broadcast) that plain IPv4 reserves.
- **A `/28` is 16 addresses, 11 usable.** It is the smallest IPv4 subnet AWS allows.
- **VPC IPv4 CIDR: `/16` (65,536 addresses) to `/28` (16). Subnet IPv4 CIDR: `/28` to `/16`.**
- **CIDRs cannot be resized.** To grow address space you attach a secondary, non-overlapping block; the primary block is permanent.
- **Overlapping CIDRs block connectivity.** VPC peering, Transit Gateway attachments, and Direct Connect gateways all require non-overlapping ranges.
- **Public IPv4 addresses are billed.** Every public IPv4 address — auto-assigned or Elastic — carries an hourly charge whether it is attached or idle, so leftover Elastic IPs now cost money.

## The five reserved addresses

AWS holds back five addresses in every IPv4 subnet because the subnet needs them for internal functions. For `10.0.0.0/24`:

- **`.0` — network address.** Identifies the subnet block itself and is never assigned to a resource.
- **`.1` — VPC router.** The subnet's default gateway; traffic that leaves the subnet is routed through it.
- **`.2` — DNS server.** The Amazon Route 53 Resolver address for the VPC, always at the VPC range base + 2.
- **`.3` — future use.** Held by AWS for future functionality and not assignable.
- **`.255` — broadcast.** IPv4 broadcast is not supported in a VPC, but the last address is still withheld.

That is why a `/28` yields 11 usable addresses rather than 14, and the number every sizing question expects.

## Private ranges

AWS recommends the RFC 1918 private ranges for VPC CIDRs: `10.0.0.0/8` (about 16.7 million addresses), `172.16.0.0/12` (about 1 million), and `192.168.0.0/16` (65,536). Avoid `172.17.0.0/16`, which some AWS services (Cloud9, SageMaker AI) use internally and which can conflict.

## Sizing shortcut

Count the resources the subnet must hold, add the 5 reserved addresses, and round up to the next power of two. To fit 20 instances: 20 + 5 = 25, so choose a `/27` (32 addresses). A `/28` holds only 11 usable and would fail.

## Sources

- Full references live in the per-topic documents: `01-concepts.md`, `02-aws-addressing.md`, and `06-limits-defaults.md`.
