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
* AWS::EC2::VpcGatewayAttachment
  
### Partial Support
* AWS::EC2::SecurityGroup

### Limitations

* **Security Groups with AWS owned Prefix Lists**: at present, the script will fail if you use AWS-managed prefix lists
  in your security groups.  It's currently hard to work out the difference between customer-managed and aws-managed 
  groups at the point of contact.
  
* **VpcGatewayAttachment**: at present, this applies only to InternetGateways.  VpnGateways are "coming soon".

## Usage

CloudPrep requires permission to query your AWS infrastructure. Specifically:

* DescribeVpcs
* DescribeVpcAttribute
* DescribeSubnets
* DescribeSecurityGroups
* DescribeManagedPrefixLists
* GetManagedPrefixListEntries

You may find the following IAM policy helpful.  A CFN script is provided that will create a Role that can be assumed.

````
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "CloudPrep",
            "Effect": "Allow",
            "Action": [ 
              "ec2:DescribeVpcs",
              "ec2:DescribeVpcAttribute",
              "ec2:DescribeSubnets",
              "ec2:DescribeSecurityGroups",
              "ec2:DescribeManagedPrefixLists",
              "ec2:GetManagedPrefixListEntries",
              "ec2:DescribeInternetGateways"
            ],
            "Resource": "*"
        }
    ]
}
````
