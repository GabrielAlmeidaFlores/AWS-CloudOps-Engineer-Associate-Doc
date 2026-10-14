# IP addressing exam traps

### Common Mistake

A subnet's usable address count is `2^(32 − n) − 2`, reserving only the network and broadcast address.

### Actual AWS Behavior

AWS reserves **five** addresses in every subnet: the network address, the VPC router, the DNS resolver, one address held for future use, and the broadcast address. The usable count is `2^(32 − n) − 5`. A `/28` therefore provides 11 usable addresses, not 14.

### Why It Matters

Sizing questions hinge on this single subtraction. A subnet with 16 addresses answers "how many instances fit?" with 11, and a scenario that needs 12 instances fails on a `/28`; it needs at least a `/27`.

---

### Common Mistake

A VPC's CIDR block can be resized later to hold more addresses.

### Actual AWS Behavior

A CIDR block cannot be made larger or smaller after creation. You can only attach **additional** non-overlapping blocks, and you cannot remove the primary block. The primary block and every secondary block count against the same default quota of five IPv4 CIDR blocks per VPC.

### Why It Matters

"Fix the undersized VPC" scenarios reward attaching a secondary CIDR, not resizing. Because the primary block is permanent, address planning must happen before the VPC is created, a wrong choice at creation is only ever mitigated, never undone.

---

### Common Mistake

Two VPCs can peer even if their CIDR blocks overlap.

### Actual AWS Behavior

CIDRs **must not overlap** for VPC peering, Transit Gateway attachments, or a Direct Connect gateway. An overlapping block causes the connection request to fail outright rather than connecting partially.

### Why It Matters

Address planning across accounts and Regions is the real decision point. Overlapping CIDRs hard-block connectivity, and because neither VPC's CIDR can be resized, the only remedy is to re-address and rebuild one side.

---

### Common Mistake

A `/28` is too small to be worth using.

### Actual AWS Behavior

`/28` is the *minimum* subnet size AWS allows. It provides 16 addresses and 11 usable, enough for a few instances or a small interface-endpoint subnet.

### Why It Matters

A question asking for "the smallest possible subnet" has exactly one answer: `/28`. Any prefix larger than `/28` (for example `/30`) is rejected.

---

### Common Mistake

A public IP attached to an instance is stable, like a private IP.

### Actual AWS Behavior

An auto-assigned public IPv4 address is released when the instance is stopped and a different one is assigned on the next start. Only an **Elastic IP** is a static public address that survives stop/start.

### Why It Matters

Scenarios that whitelist an instance's address in a partner firewall, DNS record, or security rule break when the instance restarts with a new public IP. The correct answer is an Elastic IP (now billed hourly whether attached or idle), not a reboot-and-hope.

---

### Common Mistake

Public IPv4 addresses and Elastic IPs that are idle cost nothing.

### Actual AWS Behavior

Every public IPv4 address is billed on an hourly basis whether it is attached to a resource or sitting idle. An Elastic IP that is not associated with a running instance is still charged.

### Why It Matters

Cost-optimization questions now include "release unused Elastic IPs" as a correct action. The old assumption that an idle Elastic IP is free is a trap.

## Sources

- AWS: *Subnet CIDR blocks*. https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html
- AWS: *VPC CIDR blocks*. https://docs.aws.amazon.com/vpc/latest/userguide/vpc-cidr-blocks.html
- AWS: *Amazon VPC quotas*. https://docs.aws.amazon.com/vpc/latest/userguide/amazon-vpc-limits.html
- AWS: *SOA-C03 exam guide, Content Domain 5*. https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/sysops-administrator-associate-03-domain5.html
