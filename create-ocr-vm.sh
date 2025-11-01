#!/bin/bash
# Azure VM Creation Script for OCR Service

set -e

echo "🚀 Creating Azure VM for OCR Service..."

# Configuration
RESOURCE_GROUP="rg-qadam"
VM_NAME="vm-qadam-ocr"
LOCATION="eastus"
VM_SIZE="Standard_B2s"
IMAGE="Ubuntu2204"
ADMIN_USERNAME="azureuser"

# Login to Azure (if not already logged in)
echo "🔐 Checking Azure login..."
az account show > /dev/null 2>&1 || az login

# Create resource group (if not exists)
echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION --output table

# Create VM
echo "🖥️  Creating Virtual Machine..."
az vm create \
  --resource-group $RESOURCE_GROUP \
  --name $VM_NAME \
  --image $IMAGE \
  --size $VM_SIZE \
  --admin-username $ADMIN_USERNAME \
  --generate-ssh-keys \
  --public-ip-sku Standard \
  --output table

# Open required ports
echo "🔓 Opening ports..."
az vm open-port --resource-group $RESOURCE_GROUP --name $VM_NAME --port 80 --priority 1000 --output table
az vm open-port --resource-group $RESOURCE_GROUP --name $VM_NAME --port 443 --priority 1001 --output table
az vm open-port --resource-group $RESOURCE_GROUP --name $VM_NAME --port 8000 --priority 1002 --output table

# Get public IP
echo "🌐 Getting public IP..."
PUBLIC_IP=$(az vm show --resource-group $RESOURCE_GROUP --name $VM_NAME --show-details --query publicIps -o tsv)

echo ""
echo "✅ VM Created Successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 VM Name: $VM_NAME"
echo "🌐 Public IP: $PUBLIC_IP"
echo "👤 Username: $ADMIN_USERNAME"
echo "🔑 SSH Key: ~/.ssh/id_rsa"
echo ""
echo "🔗 SSH Command:"
echo "   ssh $ADMIN_USERNAME@$PUBLIC_IP"
echo ""
echo "📝 Next Steps:"
echo "   1. Add these GitHub Secrets:"
echo "      - VM_HOST: $PUBLIC_IP"
echo "      - VM_USERNAME: $ADMIN_USERNAME"
echo "      - VM_SSH_KEY: (contents of ~/.ssh/id_rsa)"
echo ""
echo "   2. SSH to VM and run initial setup:"
echo "      ssh $ADMIN_USERNAME@$PUBLIC_IP"
echo "      sudo apt update && sudo apt upgrade -y"
echo "      sudo apt install -y python3.10 python3.10-venv python3-pip nginx git"
echo "      sudo apt install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev"
echo "      sudo mkdir -p /opt/qadam-ocr"
echo "      sudo chown $ADMIN_USERNAME:$ADMIN_USERNAME /opt/qadam-ocr"
echo ""
echo "   3. Push deployment files to backend-ocr branch"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
