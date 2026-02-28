import os
import time
import boto3
import paramiko
from dotenv import load_dotenv
from pathlib import Path
import urllib3

# Disable urllib3 warnings
urllib3.disable_warnings()

# Load credentials from .env in ec2 folder
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configuration from .env
REGION = os.getenv('REGION')
AMI_ID = os.getenv('AMI_ID')
INSTANCE_TYPE = os.getenv('INSTANCE_TYPE')
SECURITY_GROUP = os.getenv('SECURITY_GROUP')
VPC_ID = os.getenv('VPC_ID')
NAME = os.getenv('NAME')
SSH_USERNAME = os.getenv('SSH_USERNAME', 'ec2-user')
SSH_PASSWORD = os.getenv('SSH_PASSWORD')

# Get EC2 client
def get_ec2_client():
    return boto3.client(
        'ec2',
        region_name=REGION,
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
        verify=False
    )

def install_terraform_via_ssh(public_ip, username, password):
    """Connect via SSH and install Terraform"""
    print(f"\nConnecting to {public_ip} via SSH...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    max_retries = 10
    for attempt in range(max_retries):
        try:
            ssh.connect(
                hostname=public_ip,
                username=username,
                password=password,
                timeout=10,
                look_for_keys=False,
                allow_agent=False
            )
            print("SSH connection established!")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Waiting for SSH... (attempt {attempt + 1}/{max_retries})")
                time.sleep(30)
            else:
                print(f"Failed to connect via SSH: {e}")
                return False
    
    # Install Terraform
    commands = [
        "sudo yum install -y yum-utils shadow-utils",
        "sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo",
        "sudo yum install -y terraform",
        "terraform version",
    ]
    
    print("\nInstalling Terraform...")
    for cmd in commands:
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        exit_status = stdout.channel.recv_exit_status()
        
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        
        if output:
            print(output)
        if error and exit_status != 0:
            print(f"Error: {error}")
        
        if exit_status != 0:
            print(f"Command failed with exit status {exit_status}")
            ssh.close()
            return False
    
    ssh.close()
    print("\nTerraform installation completed successfully!")
    print("\n" + "="*60)
    print("IMPORTANT: Configure AWS CLI to use Terraform")
    print("="*60)
    print("\nSSH into your instance and run:")
    print("*"*50)
    print(f"  ssh {SSH_USERNAME}@{public_ip}")
    print("*"*50)
    print("\nThen configure AWS CLI:")
    print("*"*50)
    print("  aws configure")
    print("\nYou'll need to provide:")
    print("  - AWS Access Key ID")
    print("  - AWS Secret Access Key")
    print("  - Default region name (e.g., us-east-1)")
    print("  - Default output format (json)")
    print("*"*50)
    print("\nVerify configuration:")
    print("  aws sts get-caller-identity")
    print("\nNow you can use Terraform:")
    print("  terraform init")
    print("  terraform plan")
    print("  terraform apply")
    print("="*60)
    return True

def create_instance():
    start_time = time.time()
    ec2 = get_ec2_client()
    
    # Find subnet in VPC
    subnets = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [VPC_ID]}])
    subnet_id = subnets['Subnets'][0]['SubnetId']
    print(f"Using subnet: {subnet_id}")
    
    # Launch instance (no user data needed, will use SSH)
    response = ec2.run_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        MinCount=1,
        MaxCount=1,
        NetworkInterfaces=[{
            'DeviceIndex': 0,
            'SubnetId': subnet_id,
            'Groups': [SECURITY_GROUP],
            'AssociatePublicIpAddress': True
        }],
        BlockDeviceMappings=[{
            'DeviceName': '/dev/xvda',
            'Ebs': {'VolumeSize': 8, 'VolumeType': 'gp3', 'DeleteOnTermination': True}
        }],
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name', 'Value': NAME}]
        }]
    )
    
    instance_id = response['Instances'][0]['InstanceId']
    print(f"Instance launched: {instance_id}")
    
    # Wait for instance to be running
    print("Waiting for instance to start...")
    ec2.get_waiter('instance_running').wait(InstanceIds=[instance_id])
    
    # Get public IP
    info = ec2.describe_instances(InstanceIds=[instance_id])
    public_ip = info['Reservations'][0]['Instances'][0].get('PublicIpAddress', 'N/A')
    
    print(f"\n{'='*50}")
    print(f"Instance ID: {instance_id}")
    print(f"Public IP: {public_ip}")
    print(f"{'='*50}")
    
    # Install Terraform via SSH
    if SSH_PASSWORD:
        install_terraform_via_ssh(public_ip, SSH_USERNAME, SSH_PASSWORD)
    else:
        print("\nNo SSH password configured. Skipping Terraform installation.")
        print("To enable auto-install, add SSH_PASSWORD to .env file")
    
    elapsed = time.time() - start_time
    minutes, seconds = divmod(elapsed, 60)
    print(f"\nTime taken: {int(minutes)}m {seconds:.1f}s")

def delete_instance():
    start_time = time.time()
    ec2 = get_ec2_client()
    
    # List running instances
    response = ec2.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'stopped']}]
    )
    
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            name = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'N/A')
            instances.append({
                'id': instance['InstanceId'],
                'name': name,
                'state': instance['State']['Name']
            })
    
    if not instances:
        print("No instances found.")
        return
    
    print("\nAvailable instances:")
    for i, inst in enumerate(instances, 1):
        print(f"{i}. {inst['id']} - {inst['name']} ({inst['state']})")
    
    print("\nOptions:")
    print("  Enter a number (1-{len(instances)}) to delete a specific instance")
    print("  Enter 'all' to delete ALL instances")
    print("  Enter 'q' to quit")
    
    choice = input("\nYour choice: ").strip()
    if choice.lower() == 'q':
        return
    
    if choice.lower() == 'all':
        # Delete all instances
        all_ids = [inst['id'] for inst in instances]
        print(f"\nYou are about to terminate ALL {len(all_ids)} instance(s):")
        for inst in instances:
            print(f"  - {inst['id']} ({inst['name']})")
        confirm = input(f"\nTerminate all {len(all_ids)} instance(s)? (yes/no): ")
        if confirm.lower() in ('yes', 'y'):
            ec2.terminate_instances(InstanceIds=all_ids)
            print(f"Terminating {len(all_ids)} instance(s)...")
            for iid in all_ids:
                print(f"  - {iid}")
            elapsed = time.time() - start_time
            minutes, seconds = divmod(elapsed, 60)
            print(f"\nTime taken: {int(minutes)}m {seconds:.1f}s")
        else:
            print("Cancelled.")
        return
    
    # Find instance by number, ID, or name
    instance_id = None
    try:
        # Try as number first
        idx = int(choice) - 1
        if 0 <= idx < len(instances):
            instance_id = instances[idx]['id']
    except ValueError:
        # Not a number, try as ID or name
        for inst in instances:
            if choice == inst['id'] or choice == inst['name']:
                instance_id = inst['id']
                break
    
    if not instance_id:
        print("Invalid selection.")
        return
    
    # Show selected instance details
    selected = next(inst for inst in instances if inst['id'] == instance_id)
    confirm = input(f"Terminate {instance_id} ({selected['name']})? (yes/no): ")
    if confirm.lower() in ('yes', 'y'):
        ec2.terminate_instances(InstanceIds=[instance_id])
        print(f"Terminating {instance_id}...")
        elapsed = time.time() - start_time
        minutes, seconds = divmod(elapsed, 60)
        print(f"\nTime taken: {int(minutes)}m {seconds:.1f}s")
    else:
        print("Cancelled.")

# Main menu
print("EC2 Instance Manager")
print("1. Create instance")
print("2. Delete instance")

choice = input("\nChoose (1 or 2): ")

if choice == '1':
    create_instance()
elif choice == '2':
    delete_instance()
else:
    print("Invalid choice.")
