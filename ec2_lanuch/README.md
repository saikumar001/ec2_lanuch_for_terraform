# EC2 Instance Manager with Terraform Auto-Install

Simple Python script to create/delete EC2 instances with automatic Terraform installation.

## Features

- **Create EC2 instances** with automatic Terraform installation
- **Delete instances** by number, ID, or name
- **Auto-loads credentials** from `.env` file
- **User data script** installs Terraform on first boot

## Getting Started

1. **Create a project folder:**
   ```bash
   mkdir ec2_project
   cd ec2_project
   ```

2. **Create a virtual environment:**
   ```bash
   # On Windows
   python -m venv .venv
   
   # On Linux/Mac
   python3 -m venv .venv
   ```

3. **Activate the virtual environment:**
   ```bash
   # On Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   
   # On Windows (Command Prompt)
   .venv\Scripts\activate.bat
   
   # On Linux/Mac
   source .venv/bin/activate
   ```

4. **Copy the ec2_lanuch folder** into your project directory

## Setup

1. **Install dependencies:**
   ```bash
   pip install python-dotenv boto3
   ```

2. **Configure `.env` file** in the `ec2/` folder:
   ```env
   AWS_ACCESS_KEY_ID=your_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_here
   AWS_SESSION_TOKEN=
   
   REGION=us-east-1
   AMI_ID=ami-0220d79f3f480ecf5
   INSTANCE_TYPE=t3.micro
   SECURITY_GROUP=sg-05f6d4e8dbe538e8e
   VPC_ID=vpc-00f24019f0f28e65e
   NAME=terraform-main-instance
   ```

## Usage

Run the script:
```bash
python ec2/ec2_lanuch.py
```

**Menu:**
```
EC2 Instance Manager
1. Create instance
2. Delete instance

Choose (1 or 2):
```

### Create Instance

- Launches EC2 instance with your configuration
- Automatically installs Terraform via user data script
- Installation runs in background (takes 2-3 minutes)
- Shows instance ID and public IP

**After creation:**
```bash
ssh ec2-user@<public-ip>
terraform version
cat /home/ec2-user/terraform_version.txt
```

### Delete Instance

Lists all running/stopped instances:
```
Available instances:
1. i-0abc123def456 - terraform-main-instance (running)
2. i-0xyz789abc123 - test-server (stopped)

Enter number, instance ID, or instance name (or 'q' to quit):
```

You can delete by:
- **Number**: `1`, `2`
- **Instance ID**: `i-0abc123def456`
- **Instance Name**: `terraform-main-instance`

## What Gets Installed

The user data script automatically installs:
- Terraform (latest version from HashiCorp repo)
- AWS CLI
- Required utilities (yum-utils, shadow-utils)

Installation creates a log file at:
```
/home/ec2-user/terraform_version.txt
```

## Manual Installation

If you need to install Terraform manually or customize the installation, use:
```bash
bash ec2/install_terraform.sh
```

This provides:
- Step-by-step installation
- PATH configuration
- AWS CLI setup guide
- Terraform quick start guide

## Files

- `ec2_lanuch.py` - Main script
- `.env` - Configuration and credentials
- `install_terraform.sh` - Manual installation script (optional)

## Security Notes

- `.env` file contains sensitive credentials - never commit to git
- SSL verification is disabled (`verify=False`) for corporate proxies
- Consider using IAM roles instead of access keys for production

## Terraform Quick Start

After SSH into the instance:

1. **Create a Terraform file** (`main.tf`):
   ```hcl
   provider "aws" {
     region = "us-east-1"
   }
   
   resource "aws_instance" "example" {
     ami           = "ami-0220d79f3f480ecf5"
     instance_type = "t3.micro"
     tags = {
       Name = "terraform-example"
     }
   }
   ```

2. **Run Terraform commands:**
   ```bash
   terraform init       # Initialize
   terraform plan       # Preview changes
   terraform apply      # Create resources
   terraform destroy    # Clean up
   ```
