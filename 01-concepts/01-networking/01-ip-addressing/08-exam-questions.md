# IP addressing / CIDR exam practice questions

Ten original, scenario-based questions covering the IP addressing docs in this folder. They map mainly to **Domain 5 (Networking and Content Delivery)**. Written in the SOA-C03 style, not copied from any exam.

The set covers: CIDR notation, network and broadcast addresses, the reserved addresses in a subnet, allowed subnet sizes, private versus public addresses, Elastic IP, NAT gateway placement, VPC peering overlap, and the local route.

---

## Q1

A team plans a `/24` subnet for web servers in a VPC. How many IPv4 addresses can they assign to resources?

- A. 256
- B. 255
- C. 251
- D. 254

<details><summary>Answer</summary>

**C.** A `/24` has 256 addresses, and AWS reserves five in every subnet (network, VPC router, DNS, a future-use address, and broadcast), leaving 251 usable.
- **A.** 256 ignores the reserved addresses.
- **B.** 255 subtracts only the broadcast address.
- **D.** 254 subtracts two, the non-AWS convention.

Reference: [02-aws-addressing.md](02-aws-addressing.md), [06-limits-defaults.md](06-limits-defaults.md).
</details>

---

## Q2

Which address in a subnet does AWS reserve for the VPC router?

- A. The first address (network address).
- B. The second address.
- C. The third address.
- D. The last address.

<details><summary>Answer</summary>

**B.** AWS reserves the second address for the VPC router.
- **A.** The first address is the network address.
- **C.** The third address is the DNS resolver.
- **D.** The last address is the broadcast address.

Reference: [02-aws-addressing.md](02-aws-addressing.md).
</details>

---

## Q3

A subnet is created with the CIDR block `10.0.0.0/15`. It is rejected. Why?

- A. The block overlaps the VPC.
- B. A subnet must be between `/16` and `/28`.
- C. Subnets must be `/24` or smaller.
- D. `/15` blocks are only allowed in the default VPC.

<details><summary>Answer</summary>

**B.** A VPC subnet CIDR must be between `/16` and `/28`; `/15` is larger than the maximum.
- **A.** Overlap is a separate error and does not apply to a first subnet.
- **C.** `/24` is not a requirement.
- **D.** `/15` is invalid everywhere, not only outside the default VPC.

Reference: [02-aws-addressing.md](02-aws-addressing.md), [06-limits-defaults.md](06-limits-defaults.md).
</details>

---

## Q4

Two VPCs, `10.0.0.0/16` and `10.0.0.0/24`, are meant to be joined with VPC peering. The peering connection is created but traffic does not flow. What is the cause?

- A. The route tables were not updated.
- B. Peering requires non-overlapping CIDR blocks, and the second block is inside the first.
- C. Peering only works within one Availability Zone.
- D. The security groups block ICMP.

<details><summary>Answer</summary>

**B.** Peering requires the two CIDR blocks to not overlap; `10.0.0.0/24` sits inside `10.0.0.0/16`, so the route is ambiguous and the connection is unusable.
- **A.** Route tables must also be updated, but the overlap disqualifies the design first.
- **C.** Peering is not limited to one Availability Zone.
- **D.** A security-group block would affect a specific protocol, not all traffic.

Reference: [03-troubleshooting.md](03-troubleshooting.md).
</details>

---

## Q5

Which change makes an EC2 instance reachable from the internet?

- A. Assign a private IP and add an internet gateway to the VPC.
- B. Assign a public IPv4 address (or an Elastic IP) to the instance and give its subnet a route to the internet gateway.
- C. Add a NAT gateway to the instance's subnet.
- D. Add a secondary private IP.

<details><summary>Answer</summary>

**B.** Reachability needs both a public address on the instance and a route from the subnet to an internet gateway.
- **A.** An internet gateway alone does not give the instance a public address.
- **C.** A NAT gateway provides outbound-only access.
- **D.** A secondary private IP does not add a public address.

Reference: [02-aws-addressing.md](02-aws-addressing.md), [04-comparisons.md](04-comparisons.md).
</details>

---

## Q6

An instance must keep the same public IPv4 address even after stop and start, and the address must be remappable to another instance during failover. Which should be used?

- A. An auto-assigned public IPv4 address.
- B. An Elastic IP address.
- C. A private IP with a NAT gateway.
- D. A DNS CNAME.

<details><summary>Answer</summary>

**B.** An Elastic IP is a static public IPv4 address that survives stop/start and can be reassociated with another instance.
- **A.** An auto-assigned public address changes on stop/start.
- **C.** A NAT gateway provides outbound access only.
- **D.** A CNAME is a name, not an address.

Reference: [04-comparisons.md](04-comparisons.md).
</details>

---

## Q7

Instances in a private subnet must download patches from the internet but must not be reachable from it. Where does the NAT gateway go?

- A. In the private subnet, with a private IP.
- B. In a public subnet, with an Elastic IP.
- C. In the VPC with no route table.
- D. Attached directly to each instance.

<details><summary>Answer</summary>

**B.** A NAT gateway is created in a public subnet and uses an Elastic IP, so private-subnet instances get outbound access with no inbound path.
- **A.** A NAT gateway in a private subnet has no route to the internet.
- **C.** A NAT gateway needs a route table with a route to an internet gateway.
- **D.** NAT gateways are not attached to instances.

Reference: [02-aws-addressing.md](02-aws-addressing.md).
</details>

---

## Q8

Which route is present in every VPC route table and cannot be removed?

- A. The default route `0.0.0.0/0`.
- B. The local route for the VPC CIDR block.
- C. A route to the internet gateway.
- D. A route to the NAT gateway.

<details><summary>Answer</summary>

**B.** Every route table has a local route for the VPC CIDR that enables VPC-internal traffic and cannot be deleted.
- **A.** The default route is optional and user-added.
- **C.** A route to an internet gateway is optional.
- **D.** A route to a NAT gateway is optional.

Reference: [02-aws-addressing.md](02-aws-addressing.md).
</details>

---

## Q9

The expression `192.168.1.0/26` is equivalent to which subnet mask and how many addresses?

- A. `255.255.255.0`, 256 addresses.
- B. `255.255.255.192`, 64 addresses.
- C. `255.255.255.224`, 32 addresses.
- D. `255.255.0.0`, 65536 addresses.

<details><summary>Answer</summary>

**B.** A `/26` sets 26 network bits, leaving 6 host bits: `2^6 = 64` addresses, mask `255.255.255.192`.
- **A.** That is a `/24`.
- **C.** That is a `/27`.
- **D.** That is a `/16`.

Reference: [01-concepts.md](01-concepts.md), [04-comparisons.md](04-comparisons.md).
</details>

---

## Q10

A subnet with a `/28` CIDR is running out of addresses and cannot host the planned resources, even though the team expected 16. What is the reason?

- A. `/28` has only 11 usable addresses after AWS reserves five.
- B. `/28` is not a valid subnet size.
- C. The VPC CIDR is exhausted.
- D. Public IP addresses are limited per subnet.

<details><summary>Answer</summary>

**A.** A `/28` holds 16 addresses; AWS reserves five, leaving 11, so the team should size the subnet larger or split the resources.
- **B.** `/28` is valid; it is the smallest allowed subnet.
- **C.** VPC CIDR exhaustion is a different failure.
- **D.** Public addresses are not the constraint here.

Reference: [06-limits-defaults.md](06-limits-defaults.md), [03-troubleshooting.md](03-troubleshooting.md).
</details>
