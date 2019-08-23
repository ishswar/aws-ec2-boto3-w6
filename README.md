# aws-ec2-boto3-w6

## Introduction 

   This is sample Boto3 sample code for creating,managing and destroying AWS EC2 instance.
   
   Code has 6 main blocks 
   
   - [ ]    Get Connection to AWS 
- [ ]    Get Custom VPC and Subnet-id 
- [ ]    Get Security group - if not found create a new one 
- [ ]    Create a EC2 instance, wait for it to come-up 
- [ ]    Once comes up log-in into it and run some commands 
- [ ]    Terminate EC2 instance 

## Code 

<details>
  <summary>Click to see</summary>
   Code
   ```BASH
   ```
</details>


## Sample output 
``` BASH
➜  w6 git:(master) ✗ ./run_instance.py
======================= Getting boto3 session for AWS ========================
Connection to AWS was successful
Python version: 3.7.3 (default, Mar 27 2019, 09:23:39)
[Clang 10.0.0 (clang-1000.11.45.5)]
Boto3 version: 1.9.142
======================= Getting VPC and Subnet to use ========================
2019-08-23 14:57:47 Subnet ID: {'AvailabilityZone': 'us-west-2b', 'AvailabilityZoneId': 'usw2-az2', 'AvailableIpAddressCount': 251, 'CidrBlock': '10.0.1.0/24', 'DefaultForAz': False, 'MapPublicIpOnLaunch': True, 'State': 'available', 'SubnetId': 'subnet-04b61c4ffab7793a3', 'VpcId': 'vpc-06efa2c8cf36becbe', 'OwnerId': '858619844792', 'AssignIpv6AddressOnCreation': False, 'Ipv6CidrBlockAssociationSet': [], 'Tags': [{'Key': 'Name', 'Value': 'ucsc-subnet-2'}], 'SubnetArn': 'arn:aws:ec2:us-west-2:858619844792:subnet/subnet-04b61c4ffab7793a3'}
================ Creating/getting Security Group information =================
2019-08-23 14:57:47 No security group named [awsclass01] found, will create new security groupawsclass01
2019-08-23 14:57:47 created security group:sg-0c91454c8b07ced4c
=========================== Starting EC2 instance ============================
2019-08-23 14:57:48 About to create a EC2 instance with :
AMI ID: ami-0f2176987ee50226e
sshkeypair: pshah2019v2
secgrpidlist: ['sg-0c91454c8b07ced4c']
subnetid: subnet-04b61c4ffab7793a3
numinstances: 1

2019-08-23 14:57:49 EC2 instance has been created with ID : i-0b4c50b1373be3d3f
  Now ... Waiting for instance to enter running state
2019-08-23 14:58:17 Instance is running now waiting for it to initialized
2019-08-23 14:58:17 Instance status : initializing
2019-08-23 14:59:02 Instance status : initializing
2019-08-23 14:59:47 Instance status : initializing
2019-08-23 15:00:32 Instance status : initializing
2019-08-23 15:01:18 Instance status : initializing
2019-08-23 15:02:03 Instance status : ok
2019-08-23 15:02:03 Checking if instance has Public IP - else we will wait for it be assigned
2019-08-23 15:02:03 Public IP assigned to this instance is: 52.89.45.141
2019-08-23 15:02:03 Now logging into instance using SSH and public key
2019-08-23 15:02:03 Command we are using is
ssh -i ../../../../AWS/ubuntuvm/pshah2019v2.pem ec2-user@52.89.45.141 "echo "Inside EC2 instance";echo "Machine info";uname -a;echo "Host name:";hostname;echo "IP Address";hostname -i;echo "Public IP";curl -s ipecho.net/plain; echo;"
Warning: Permanently added '52.89.45.141' (ECDSA) to the list of known hosts.
Inside EC2 instance
Machine info
Linux ip-10-0-1-64 4.14.123-86.109.amzn1.x86_64 #1 SMP Mon Jun 10 19:44:53 UTC 2019 x86_64 x86_64 x86_64 GNU/Linux
Host name:
ip-10-0-1-64
IP Address
10.0.1.64
Public IP
52.89.45.141
=========================== Stopping EC2 instance ============================
2019-08-23 15:02:04 Instance has changed state from: [stopping] to new state: [shutting-down]
```

## Output video 

### Screen captures  
    Screen grab of Security Group and EC2 instances while they are getting created

