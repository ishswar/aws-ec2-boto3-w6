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
   ``` PYTHON
   #!/usr/bin/env python3
from datetime import datetime
import subprocess
import time


###
# Helper methods
###
from awsGetConnection import get_aws_connection


def banner(text, ch='=', length=78):
    spaced_text = ' %s ' % text
    banner = spaced_text.center(length, ch)
    return banner


def printlog(text):
    strformat = "%Y-%m-%d %H:%M:%S"
    print(datetime.strftime(datetime.now(), strformat), text)


print(banner("Getting boto3 session for AWS"))

# Get boto3 session
# This will also check of connectivity
session = get_aws_connection()

# Constance

region = 'us-west-2'
vpc = 'ucsc-vpc'
vpc_subnet = 'ucsc-subnet-2'
secgrpname = 'awsclass01'

amiid = 'ami-0f2176987ee50226e'
insttype = 't2.micro'
sshkeypair = 'pshah2019v2'  # use your own ssh keypair
numinstances = 1

ec2c = session.client('ec2', region_name=region)

print(banner("Getting VPC and Subnet to use"))

# Get UCSC vpc that we have created
resp = ec2c.describe_vpcs(Filters=[{'Name': 'tag:Name', 'Values': [vpc]}])
vpcidtouse = resp['Vpcs'][0]['VpcId']

# Get VPC Id and get first ucsc subnet
subnetlist = ec2c.describe_subnets(
    Filters=[{'Name': 'vpc-id', 'Values': [vpcidtouse]}, {'Name': 'tag:Name', 'Values': [vpc_subnet]}])

if len(subnetlist) > 0:
    subnet_to_use = subnetlist['Subnets'][0];
    #printlog("Subnet to use is :")
    #printlog(subnet_to_use)
    subnetid = subnetlist['Subnets'][0]['SubnetId']
    printlog("Subnet ID: " + str(subnet_to_use))
else:
    printlog("We could not find subnet to use - need to invastigate this error")
    exit(-2)

secgrpid = ''

print(banner("Creating/getting Security Group information"))

# Get Security group that we are about to create - if it exists then no point creating it again
# Since our security group is non-default VPC we need to use Filters to get that
response = ec2c.describe_security_groups(
    Filters=[
        {
            'Name': 'group-name',
            'Values': [
                secgrpname,
            ]
        },
    ]
)

# If we got reply then it looks it does exists
if len(response['SecurityGroups']) > 0:
    secgrpid = response['SecurityGroups'][0]['GroupId']

if not secgrpid:
    try:
        secgrpfilter = [{'Name': 'group-name', 'Values': [secgrpname]}]
        secgroups = ec2c.describe_security_groups(Filters=secgrpfilter)
        secgrptouse = secgroups["SecurityGroups"][0]
        secgrpid = secgrptouse['GroupId']
    except:
        printlog('No security group named ['+secgrpname+'] found, will create new security group' + secgrpname)

    secgrptouse = ec2c.create_security_group(GroupName=secgrpname, Description='aws class open ssh,http,https',
                                             VpcId=vpcidtouse)
    secgrpid = secgrptouse['GroupId']
    printlog("created security group:" + secgrpid)

    portlist = [22, 80, 443]
    for port in portlist:
        try:
            ec2c.authorize_security_group_ingress(CidrIp='0.0.0.0/0', FromPort=port, GroupId=secgrpid,
                                                  IpProtocol='tcp', ToPort=port)
        except:
            printlog("error opening port:" + str(port))
            exit()
else:
    printlog("No need to create Security Group " + secgrpname + " It seems to be exists already ")

secgrpidlist = [secgrpid]

print(banner("Starting EC2 instance"))

printlog("About to create a EC2 instance with :\n" +
         "AMI ID: " + amiid + "\n" +
         "sshkeypair: " + sshkeypair + "\n" +
         "secgrpidlist: " + str(secgrpidlist) + "\n" +
         "subnetid: " + subnetid + "\n" +
         "numinstances: " + str(numinstances) + "\n"
         )

resp = ec2c.run_instances(ImageId=amiid, InstanceType=insttype, KeyName=sshkeypair, SecurityGroupIds=secgrpidlist,
                          SubnetId=subnetid, MaxCount=numinstances, MinCount=numinstances)


inst = resp["Instances"][0]
instid = inst["InstanceId"]

printlog('EC2 instance has been created with ID : ' + instid + '\n  Now ... Waiting for instance to enter running state')

bIsRunning = False
bDidWePrintRunning = False
while bIsRunning == False:
    rz = ec2c.describe_instance_status(InstanceIds=[instid])

    # call can return before all data is available
    if not bool(rz):
        continue
    if len(rz["InstanceStatuses"]) == 0:
        continue

    inststate = rz["InstanceStatuses"][0]["InstanceState"]
    state = inststate["Name"]

    if state == 'running':
        if not bDidWePrintRunning:
            #printlog(json.dumps(inststate, indent=2, separators=(',', ':')))
            printlog("Instance is running now waiting for it to initialized")
            bDidWePrintRunning = True

    instatus = rz["InstanceStatuses"][0]["InstanceStatus"]["Status"]
    printlog("Instance status : " + instatus)

    if instatus == 'ok':
        bIsRunning = True
    else:
        time.sleep(45) # Wait for 20 seconds before next poll
        continue

printlog('Checking if instance has Public IP - else we will wait for it be assigned')
bGotIp = False
while bGotIp == False:
    outp = ec2c.describe_instances(InstanceIds=[instid])
    inst = outp["Reservations"][0]["Instances"][0]
    instid = inst["InstanceId"]
    publicip = inst.get('PublicIpAddress')
    if not publicip:
        printlog('do not have ip address yet')
        time.sleep(20)
        continue
    else:
        bGotIp = True

printlog('Public IP assigned to this instance is: ' + publicip)

printlog("Now logging into instance using SSH and public key ")

remoteCommandToRunOnInstance = 'echo \"Inside EC2 instance\";echo \"Machine info\";uname -a;echo \"Host ' \
                               'name:\";hostname;echo ' \
                               '\"IP Address\";hostname -i;echo "Public IP";curl -s ipecho.net/plain; echo;'

printlog("Command we are using is \n\rssh -i ../../../../AWS/ubuntuvm/pshah2019v2.pem ec2-user@"+publicip+" \""+ remoteCommandToRunOnInstance + "\"")
banner("SSH login")
subprocess.call('ssh -i ../../../../AWS/ubuntuvm/pshah2019v2.pem ec2-user@'+publicip+' "'+remoteCommandToRunOnInstance+'"', shell=True)


resp=ec2c.stop_instances(InstanceIds=[instid])

resp=ec2c.terminate_instances(InstanceIds=[instid])

currentInstanceState = resp["TerminatingInstances"][0]["CurrentState"]["Name"]
beforeInstanceState = resp["TerminatingInstances"][0]["PreviousState"]["Name"]

print(banner("Stopping EC2 instance"))
printlog("Instance has changed state from: ["+beforeInstanceState+"] to new state: ["+currentInstanceState+"]")
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

![Demo](https://raw.githubusercontent.com/ishswar/aws-ec2-boto3-w6/blob/master/boto3_ec2_demo.gif)

### Screen captures  
    Screen grab of Security Group and EC2 instances while they are getting created

