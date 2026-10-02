# IP addressing quick review

> [!NOTE]
> This is the last thing you read before the exam — a one-page gate. If any line below isn't instantly obvious, go back to the source document: the math is in `01-concepts.md`, the AWS rules in `02-aws-addressing.md`, and the numbers in `06-limits-defaults.md`.

## Non-negotiables

- **Addresses in a block** = `2^(32 − n)`.
- **Usable in an AWS subnet** = `2^(32 − n) − 5` (five reserved, not two).
- A `/28` = 16 addresses, **11 usable**. It is the smallest subnet AWS allows.
- VPC IPv4 CIDR: `/16` to `/28`. Subnet IPv4 CIDR: `/28` to `/16`.
- CIDRs **cannot be resized**; you can only add non-overlapping secondary blocks.
- Overlapping CIDRs block VPC peering, Transit Gateway, and Direct Connect gateway.

## The five reserved addresses

Network, VPC router (`.1`), DNS (`.2`), future use (`.3`), broadcast (last).

## Private ranges

`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`. Avoid `172.17.0.0/16` (used by some AWS services).

## Sizing shortcut

Count resources, add 5, round up to the next power of two. 20 instances → 25 → `/27`.

## Sources

- Full references live in the per-topic documents: `01-concepts.md`, `02-aws-addressing.md`, and `06-limits-defaults.md`.
