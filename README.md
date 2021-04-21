# CloudPrep

CloudPrep is a tool for taking an existing cloud environment and translating into CloudFormation.

###Key design considerations
* Cloud agnostic by intent; however, currently heavily AWS focussed.
* Idempotent.  Run twice, get the same output.  This means you should be able to use it to create ChangeSets and update
  environments in-situ without considerable data loss.

## Supported AWS Elements
 
### Full Support
* AWS::EC2::VPC
* AWS::EC2::Subnet
* AWS::EC2::PrefixList
* AWS::EC2::InternetGateway
* AWS::EC2::EgressOnlyInternetGateway
* AWS::EC2::RouteTable (plus attachments)
* AWS::EC2::NatGateway
* AWS::EC2::NetworkAcl (plus entries and associations)
* AWS::EC2::VPCEndpoint

### Partial Support
* AWS::EC2::VpcGatewayAttachment
  * This applies only to InternetGateways.  VpnGateways are "coming soon"
* AWS::EC2::SecurityGroup
  * At present, the script will fail if you use AWS-managed prefix lists in your security groups.  It's currently hard
    to work out the difference between customer-managed and aws-managed groups at the point of contact.
* AWS::EC2::Route
  * A subset of targets is supported; see Limitations.
* AWS::EC2::EIP
  * Plain old EIPs work; multicast, different domains etc are not yet supported.
* AWS::EC2::TransitGateway
  * Routes pointing at a TransitGateway will cause the script to capture that TGW and its attachments to the VPC;
    however,the script currenly stopes there. RouteTables, DX connections etc are not captured.  Peering will likely
    always require a manual step.  

### Notes
* **RouteTables, NetworkACLs and SecurityGroups**: 
  * One cannot modify the main route table, default NACL or default Security Group in CloudFormation.  Consequently, 
    if the main route table or default NACL if either of these have associations, they will be captured as a custom 
    table/NACL any implicit associations made explicit.  The default security group wil lbe replicated in all cases. 
  * Bear this in mind if you go on to create new subnets or ENIs in your reproduced environment as you will need to 
    add an explicit association.
  * Route tables / NACLs without associations will not be captured (I route, therefore I am).  To force capture, assign
    the tag `cloudprep:forceCapture: True`
* **EgressOnlyInternetGateways, VpcEndpoints**: Cloudformation currently does not support tagging, thus all your tags
  will be lost.  Sorry about that.
  

### Limitations

* **Route**: Only a subset of Route targets is supported.  These are:
  * Internet Gateways
  * NAT Gateways
  * VPC Endpoints


## Usage

### Credentials

CloudPrep requires a variety of permissions to query your AWS infrastructure.  A CFN script is provided that will 
create a Policy that grants these permissions; it also provides a Role which uses this Policy that can be assumed by
the user specified on the command line.

```commandline
support/install_role.sh <IAM usser>
```

You can of course invoke the script using your own credentials / configuration if you wish.

### Invocation

```commandline
./cloudprep.py > my_json_output
```

This will take the default profile's credentials and examine the default profile's region for VPCs.  It'll then follow
the VPC outwards, touching on Subnets, NACLs, RouteTables, Routes and so forth.

* The resulting CloudFormation script it written to stdout.  
* Logging is written to stderr.