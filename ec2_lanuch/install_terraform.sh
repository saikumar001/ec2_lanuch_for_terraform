#!/bin/bash

# Terraform Installation Script for Amazon Linux
# This script installs Terraform and helps you run your first Terraform file

echo "======================================"
echo "Installing Terraform on Amazon Linux"
echo "======================================"

# Install required utilities
echo "Step 1: Installing yum-utils and shadow-utils..."
sudo yum install -y yum-utils shadow-utils

# Add HashiCorp repository
echo "Step 2: Adding HashiCorp repository..."
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo

# Install Terraform
echo "Step 3: Installing Terraform..."
sudo yum install -y terraform

# Verify installation
echo "Step 4: Verifying Terraform installation..."
terraform version

# Check if terraform is in PATH
echo ""
echo "Step 5: Checking Terraform PATH..."
TERRAFORM_PATH=$(which terraform)
echo "Terraform is installed at: $TERRAFORM_PATH"

# Add to PATH if needed (usually not required with yum installation)
if ! command -v terraform &> /dev/null; then
    echo "WARNING: Terraform not found in PATH!"
    echo "Adding /usr/bin to PATH in ~/.bashrc..."
    echo 'export PATH=$PATH:/usr/bin' >> ~/.bashrc
    source ~/.bashrc
else
    echo "Terraform is accessible from PATH ✓"
fi

echo ""
echo "======================================"
echo "Terraform installed successfully!"
echo "======================================"
echo ""
echo "NOTE: With yum installation, PATH is configured automatically."
echo "You can run 'terraform init' without additional setup."
echo ""

# Install and configure AWS CLI
echo "======================================"
echo "Setting up AWS CLI"
echo "======================================"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "Installing AWS CLI..."
    sudo yum install -y aws-cli
else
    echo "AWS CLI is already installed ✓"
fi

echo ""
echo "AWS CLI Configuration Options:"
echo ""
echo "OPTION 1 (RECOMMENDED for EC2): Use IAM Role"
echo "  - Attach an IAM role to your EC2 instance with required permissions"
echo "  - No credentials needed in the instance"
echo "  - More secure approach"
echo ""
echo "OPTION 2: Configure AWS credentials manually"
echo "  Run: aws configure"
echo "  You'll need:"
echo "    - AWS Access Key ID"
echo "    - AWS Secret Access Key"
echo "    - Default region (e.g., us-east-1)"
echo "    - Output format (json)"
echo ""
echo "To verify AWS configuration:"
echo "  aws sts get-caller-identity"
echo ""
echo "Required IAM Permissions for Terraform:"
echo "  - EC2 (create, modify, delete instances)"
echo "  - VPC (if creating networks)"
echo "  - Route53 (if managing DNS)"
echo "  - IAM (if creating roles/policies)"
echo ""

echo "======================================"
echo "Quick Start Guide"
echo "======================================"
echo ""
echo "To run your first Terraform file:"
echo "1. Navigate to your Terraform directory"
echo "   cd /path/to/your/terraform/project"
echo ""
echo "2. Initialize Terraform (downloads provider plugins)"
echo "   terraform init"
echo ""
echo "3. Format your Terraform files"
echo "   terraform fmt"
echo ""
echo "4. Validate your configuration"
echo "   terraform validate"
echo ""
echo "5. Preview changes"
echo "   terraform plan"
echo ""
echo "6. Apply changes (create infrastructure)"
echo "   terraform apply"
echo ""
echo "7. Destroy infrastructure (when done)"
echo "   terraform destroy"
echo ""
echo "======================================"
