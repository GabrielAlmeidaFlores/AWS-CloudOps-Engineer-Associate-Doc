# Hands-on project: build a peered, two-tier VPC network

This project turns the folder's address concepts into one build you can inspect, break, and repair: two peered VPCs with public and private subnets, a NAT gateway, route tables, and non-overlapping ranges. It is the practice half of the topic, not another explanation, and nothing else in the folder depends on it; the mechanics are in the linked documents, and the build applies them end to end.

## Goal

Stand up two VPCs joined by peering, with a public and a private subnet on one side, and prove that the addressing rules (reserved addresses, public/private routing, and non-overlapping peering) hold.

## What you build

Two VPCs and the gateways that connect them:

- **VPC A** `10.0.0.0/16` hosts the application: a public subnet `10.0.0.0/24` and a private subnet `10.0.10.0/24`, an internet gateway, and a NAT gateway with an Elastic IP for the private subnet's outbound traffic.
- **VPC B** `10.1.0.0/16` hosts a shared service in `10.1.0.0/24`.
- A **VPC peering** connection joins A and B. The two blocks do not overlap, which is the peering precondition.

```mermaid
flowchart LR
    subgraph CLOUD["AWS Cloud"]
      direction TB
      subgraph REGION["Region us-east-2"]
        subgraph VPCA["VPC A 10.0.0.0/16"]
          IGW["Internet gateway"]:::network
          subgraph PUBA["Public subnet 10.0.0.0/24"]
            LB["Public host"]:::compute
          end
          subgraph PRIVA["Private subnet 10.0.10.0/24"]
            APPA["Private app instance"]:::compute
          end
          NAT["NAT gateway + Elastic IP"]:::network
        end
        subgraph VPCB["VPC B 10.1.0.0/16"]
          SVC["Shared service 10.1.0.0/24"]:::compute
        end
        PEER["VPC peering"]:::network
      end
    end
    LB --> IGW
    APPA -->|"outbound only"| NAT
    VPCA <-->|"routes"| PEER
    PEER <-->|"routes"| VPCB
    classDef network fill:#8C4FFF,stroke:#8C4FFF,color:#ffffff
    classDef compute fill:#ED7100,stroke:#ED7100,color:#ffffff
    style CLOUD fill:#ffffff,stroke:#232F3E,stroke-width:2px,stroke-dasharray:5 5,color:#232F3E
    style REGION fill:#ffffff,stroke:#00A4A6,stroke-width:2px,color:#147EBA
    style VPCA fill:#ffffff,stroke:#8C4FFF,stroke-width:2px,color:#8C4FFF
    style VPCB fill:#ffffff,stroke:#8C4FFF,stroke-width:2px,color:#8C4FFF
    style PUBA fill:#ffffff,stroke:#248814,color:#248814
    style PRIVA fill:#ffffff,stroke:#00A4A6,color:#147EBA
```

## Concepts covered

| Concept | Document | Where it appears in the build |
|---------|----------|-------------------------------|
| CIDR notation and host math | [01-concepts.md](01-concepts.md) | Choosing `/16` and `/24` blocks |
| Network and broadcast, reserved addresses | [02-aws-addressing.md](02-aws-addressing.md) | The 251 usable addresses check |
| Allowed subnet sizes | [05-limits-defaults.md](05-limits-defaults.md) | `/16` VPC, `/24` subnets |
| Public versus private addresses | [02-aws-addressing.md](02-aws-addressing.md) | Public subnet versus private subnet |
| Internet gateway | [02-aws-addressing.md](02-aws-addressing.md) | Public subnet route |
| NAT gateway and Elastic IP | [02-aws-addressing.md](02-aws-addressing.md) | Private subnet outbound |
| Route tables and the local route | [02-aws-addressing.md](02-aws-addressing.md) | Both tables keep `local` |
| VPC peering and non-overlap | [03-troubleshooting.md](03-troubleshooting.md) | A to B peering |

## Prerequisites

Read these documents before starting, because the build assumes the address math and routing rules they explain.

- Read [01-concepts.md](01-concepts.md), [02-aws-addressing.md](02-aws-addressing.md), and [05-limits-defaults.md](05-limits-defaults.md) first.
- AWS CLI configured for `us-east-2`, and permission to create VPCs, subnets, gateways, and peering connections.

## Steps

Run these in order; each step depends on the resource created before it.

1. **Create both VPCs and turn on DNS hostnames.** DNS support makes the peering usable by name.

   ```bash
   aws ec2 create-vpc --cidr-block 10.0.0.0/16 --region us-east-2 \
     --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=vpc-a}]'
   aws ec2 create-vpc --cidr-block 10.1.0.0/16 --region us-east-2 \
     --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=vpc-b}]'
   aws ec2 modify-vpc-attribute --vpc-id vpc-A --enable-dns-hostnames
   ```

2. **Create the subnets in VPC A**, one public and one private, in different AZs.

   ```bash
   aws ec2 create-subnet --vpc-id vpc-A --cidr-block 10.0.0.0/24 --availability-zone us-east-2a
   aws ec2 create-subnet --vpc-id vpc-A --cidr-block 10.0.10.0/24 --availability-zone us-east-2b
   aws ec2 create-subnet --vpc-id vpc-B --cidr-block 10.1.0.0/24 --availability-zone us-east-2a
   ```

3. **Create the internet gateway and the NAT gateway.** The NAT gateway needs an Elastic IP and lives in the public subnet.

   ```bash
   aws ec2 create-internet-gateway
   aws ec2 attach-internet-gateway --vpc-id vpc-A --internet-gateway-id igw-A
   aws ec2 allocate-address --domain vpc --query 'AllocationId' --output text
   aws ec2 create-nat-gateway --subnet-id subnet-PUBA --allocation-id eipalloc-A
   ```

4. **Create route tables.** The public table routes `0.0.0.0/0` to the internet gateway; the private table routes `0.0.0.0/0` to the NAT gateway. Both keep the automatic `local` route.

   ```bash
   aws ec2 create-route-table --vpc-id vpc-A
   aws ec2 create-route --route-table-id rtb-PUB --destination-cidr-block 0.0.0.0/0 --gateway-id igw-A
   aws ec2 associate-route-table --route-table-id rtb-PUB --subnet-id subnet-PUBA
   aws ec2 create-route --route-table-id rtb-PRIV --destination-cidr-block 0.0.0.0/0 --nat-gateway-id nat-A
   aws ec2 associate-route-table --route-table-id rtb-PRIV --subnet-id subnet-PRIVA
   ```

5. **Create the peering connection and add routes both ways.** A peering connection alone does not route traffic; each VPC needs a route to the other's CIDR through the peering connection.

   ```bash
   aws ec2 create-vpc-peering-connection --vpc-id vpc-A --peer-vpc-id vpc-B
   aws ec2 accept-vpc-peering-connection --vpc-peering-connection-id pcx-A
   aws ec2 create-route --route-table-id rtb-PRIV --destination-cidr-block 10.1.0.0/16 --vpc-peering-connection-id pcx-A
   aws ec2 create-route --route-table-id rtb-B --destination-cidr-block 10.0.0.0/16 --vpc-peering-connection-id pcx-A
   ```

## Infrastructure as code (CloudFormation)

The steps above build the network with the CLI. The template below builds the same two VPCs, the subnets, the internet and NAT gateways, the route tables, and the peering connection in one stack. Because both VPCs live in the same account, CloudFormation accepts the peering request automatically, so there is no separate accept step. The zones are chosen by index (`!Select [0, !GetAZs ""]`) so the template ports to any account without editing zone names.

Save it as `peered-vpc.yaml`:

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Description: Peered two-tier VPC network for the IP addressing project

Resources:
  VpcA:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsSupport: true
      EnableDnsHostnames: true
      Tags:
        - Key: Name
          Value: vpc-a

  VpcB:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.1.0.0/16
      EnableDnsSupport: true
      EnableDnsHostnames: true
      Tags:
        - Key: Name
          Value: vpc-b

  PublicSubnetA:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VpcA
      CidrBlock: 10.0.0.0/24
      AvailabilityZone: !Select [0, !GetAZs ""]
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: subnet-pub-a

  PrivateSubnetA:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VpcA
      CidrBlock: 10.0.10.0/24
      AvailabilityZone: !Select [1, !GetAZs ""]
      Tags:
        - Key: Name
          Value: subnet-priv-a

  SubnetB:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VpcB
      CidrBlock: 10.1.0.0/24
      AvailabilityZone: !Select [0, !GetAZs ""]
      Tags:
        - Key: Name
          Value: subnet-b

  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: igw-a

  GatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VpcA
      InternetGatewayId: !Ref InternetGateway

  NatEip:
    Type: AWS::EC2::EIP
    Properties:
      Domain: vpc

  NatGateway:
    Type: AWS::EC2::NatGateway
    Properties:
      AllocationId: !GetAtt NatEip.AllocationId
      SubnetId: !Ref PublicSubnetA

  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VpcA

  PublicRoute:
    Type: AWS::EC2::Route
    DependsOn: GatewayAttachment
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway

  PublicSubnetAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnetA
      RouteTableId: !Ref PublicRouteTable

  PrivateRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VpcA

  PrivateRoute:
    Type: AWS::EC2::Route
    Properties:
      RouteTableId: !Ref PrivateRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      NatGatewayId: !Ref NatGateway

  PrivateSubnetAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PrivateSubnetA
      RouteTableId: !Ref PrivateRouteTable

  RouteTableB:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VpcB

  SubnetBAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref SubnetB
      RouteTableId: !Ref RouteTableB

  PeeringConnection:
    Type: AWS::EC2::VPCPeeringConnection
    Properties:
      VpcId: !Ref VpcA
      PeerVpcId: !Ref VpcB
      Tags:
        - Key: Name
          Value: pcx-a-b

  PrivatePeerRoute:
    Type: AWS::EC2::Route
    Properties:
      RouteTableId: !Ref PrivateRouteTable
      DestinationCidrBlock: 10.1.0.0/16
      VpcPeeringConnectionId: !Ref PeeringConnection

  PeerRouteB:
    Type: AWS::EC2::Route
    Properties:
      RouteTableId: !Ref RouteTableB
      DestinationCidrBlock: 10.0.0.0/16
      VpcPeeringConnectionId: !Ref PeeringConnection

Outputs:
  VpcAId:
    Value: !Ref VpcA
  VpcBId:
    Value: !Ref VpcB
  PrivateRouteTableId:
    Value: !Ref PrivateRouteTable
  PeeringConnectionId:
    Value: !Ref PeeringConnection
  NatGatewayEip:
    Value: !Ref NatEip
```

Deploy and remove it:

```bash
aws cloudformation deploy --stack-name lab-peered-vpc \
  --template-file peered-vpc.yaml --region us-east-2

aws cloudformation delete-stack --stack-name lab-peered-vpc --region us-east-2
```

The stack charges for the NAT gateway and its Elastic IP for as long as it exists, so delete it when the exercise is done.

## How it works

The packet path is the point. A private instance sends outbound traffic that leaves through the NAT gateway, not the internet gateway, because the private route table carries only the NAT route. Traffic to the peering peer leaves through the peering connection because the route table has a more specific route for the peer's CIDR than the `local` route's VPC range. The `local` route always matches the VPC's own CIDR and can never be removed, so intra-VPC traffic never leaves the VPC.

```mermaid
flowchart TD
    A["Private instance sends a packet"] --> B{"Destination?"}
    B -->|"Internet"| C["Private route table: 0.0.0.0/0 to NAT gateway"]
    B -->|"10.1.0.0/16 peer"| D["Private route table: peer CIDR to peering connection"]
    B -->|"Inside 10.0.0.0/16"| E["local route, stays in the VPC"]
    C --> F["NAT gateway uses its Elastic IP"]
    D --> G["Peering connection to VPC B"]
    classDef step fill:#147EBA,stroke:#147EBA,color:#ffffff
    classDef decision fill:#FF9900,stroke:#FF9900,color:#232F3E
    classDef ok fill:#7AA116,stroke:#7AA116,color:#ffffff
    class A,C,D,E step
    class B decision
    class F,G ok
```

## Validation

Check each item after the build; the expected result is stated with the command.

1. **Reserved-address math.** Each `/24` must report **251** available addresses, which is 256 minus the five AWS reserves (network, VPC router, DNS, a future-use address, and broadcast).

   ```bash
   aws ec2 describe-subnets --filters Name=vpc-id,Values=vpc-A \
     --query 'Subnets[].[CidrBlock,AvailabilityZone,AvailableIpAddressCount]' --output table
   ```

2. **Route tables.** The public table routes to the internet gateway, the private table to the NAT gateway, and both keep the `local` route.

   ```bash
   aws ec2 describe-route-tables --filters Name=vpc-id,Values=vpc-A \
     --query 'RouteTables[].Routes[].{Dest:DestinationCidrBlock,GW:GatewayId,NAT:NatGatewayId,PCX:VpcPeeringConnectionId,Origin:Origin}' --output table
   ```

3. **Peering state.** The connection is `active`, and both sides have a route for the peer CIDR.

   ```bash
   aws ec2 describe-vpc-peering-connections --vpc-peering-connection-ids pcx-A \
     --query 'VpcPeeringConnections[].Status.Code' --output text
   ```

## Failure injection

Break one dependency at a time and confirm the symptom matches the explanation.

- **Overlap.** Create a second peering request from a VPC whose CIDR overlaps A (for example `10.0.0.0/24`). The connection is created but traffic never flows, because peering requires non-overlapping CIDRs. This is the failure [03-troubleshooting.md](03-troubleshooting.md) documents.
- **Missing route.** Delete the peering route from the private table and confirm the peer becomes unreachable even though the peering connection is still `active`.
- **No default route.** Remove the `0.0.0.0/0` route from the public table and confirm the public host loses internet reachability.

## Cleanup

Delete in dependency order.

```bash
aws ec2 delete-nat-gateway --nat-gateway-id nat-A
aws ec2 release-address --allocation-id eipalloc-A
aws ec2 delete-vpc-peering-connection --vpc-peering-connection-id pcx-A
aws ec2 detach-internet-gateway --internet-gateway-id igw-A --vpc-id vpc-A
aws ec2 delete-internet-gateway --internet-gateway-id igw-A
aws ec2 delete-subnet --subnet-id subnet-EXAMPLE   # repeat for each subnet
aws ec2 delete-route-table --route-table-id rtb-EXAMPLE   # repeat
aws ec2 delete-vpc --vpc-id vpc-A
aws ec2 delete-vpc --vpc-id vpc-B
```

## What it practices

The project exercises the following SOA-C03 domain tasks and skills.

- **Domain 5, Task 5.1 (network connectivity):** Skill 5.1.1, configure a VPC, subnets, route tables, internet and NAT gateways; and private connectivity between VPCs.
- **Domain 5, Task 5.3 (network troubleshooting):** Skill 5.3.1, diagnose subnet, route-table, NAT, and peering problems; the failure injection exercises the overlap, missing-route, and missing-default-route cases.

## Sources

The entries below are the AWS documentation pages this document draws on.

- AWS: *VPC CIDR blocks*. https://docs.aws.amazon.com/vpc/latest/userguide/vpc-cidr-blocks.html
- AWS: *Subnets and reserved addresses*. https://docs.aws.amazon.com/vpc/latest/userguide/configure-subnets.html
- AWS: *VPC peering*. https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html
- AWS: *NAT gateways*. https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html
