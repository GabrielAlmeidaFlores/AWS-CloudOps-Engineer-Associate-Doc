# IP addressing exam traps

### Common Mistake

A subnet's usable count is `2^(32−n) − 2`.

### Actual AWS Behavior

AWS reserves **five** addresses per subnet, so the usable count is `2^(32−n) − 5`. A `/28` gives 11 usable, not 14.

### Why It Matters

Sizing questions hinge on this. A subnet with 16 addresses answers "how many instances fit?" with 11, and a scenario that needs 12 fails on a `/28`.

---

### Common Mistake

A VPC's CIDR block can be resized later.

### Actual AWS Behavior

A CIDR block cannot be made larger or smaller after creation. You can only add **additional** non-overlapping blocks, and you cannot remove the primary one.

### Why It Matters

"Fix the undersized VPC" scenarios reward adding a secondary CIDR, not resizing. The primary block is permanent.

---

### Common Mistake

Two VPCs can peer even if their CIDRs overlap.

### Actual AWS Behavior

CIDRs **must not overlap** for VPC peering, Transit Gateway attachments, or a Direct Connect gateway. Overlap makes the peering request fail.

### Why It Matters

Address planning across accounts is the real decision. Overlapping CIDRs hard-block connectivity, and fixing it later means rebuilding the VPC.

---

### Common Mistake

A `/28` is too small to be useful.

### Actual AWS Behavior

`/28` is the *minimum* subnet size AWS allows. It provides 16 addresses and 11 usable, enough for a few instances or a small endpoint subnet.

### Why It Matters

A question that needs the smallest possible subnet has exactly one answer: `/28`.

## Sources

- AWS — *Subnet CIDR blocks*. https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html
- AWS — *VPC CIDR blocks*. https://docs.aws.amazon.com/vpc/latest/userguide/vpc-cidr-blocks.html
- AWS — *SOA-C03 exam guide, Content Domain 5*. https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/sysops-administrator-associate-03-domain5.html
