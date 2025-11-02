# Move OCR VM to Same VNet as Proxy VM

## 🎯 Goal
Move OCR VM (4.229.225.140) to the same Virtual Network as Proxy VM (130.107.48.166)

## ⚠️ Important Notes
- **Cannot move a VM between VNets directly**
- Must create new VM from snapshot/image
- Will get new IP address
- Requires updating backend configuration with new IP

## 📋 Prerequisites

1. **Identify Proxy VM's VNet:**
   ```
   Azure Portal → Virtual Machines → Proxy VM (130.107.48.166)
   → Networking → Virtual Network name
   ```

2. **Backup OCR VM data** (if any important data exists)

## ✅ Easiest Method: Recreate OCR VM in Same VNet

### Option A: Quick Recreation (Recommended if OCR setup is simple)

This is the **fastest** method if you can quickly reinstall the OCR service.

#### Step 1: Note Current OCR VM Configuration

```bash
# SSH into OCR VM
ssh azureuser@4.229.225.140

# Note the VM size
# Azure Portal → OCR VM → Size (e.g., Standard_B2s)

# Backup any configuration files
cd /opt/qadam-ocr
tar -czf ~/ocr-backup.tar.gz .
scp ~/ocr-backup.tar.gz your-local-machine:~/
```

#### Step 2: Create New VM in Proxy's VNet

**Azure Portal:**

1. **Home → Virtual Machines → + Create**

2. **Basics:**
   - Subscription: Same as Proxy VM
   - Resource Group: Same as Proxy VM
   - VM Name: `qadam-ocr-vm-new`
   - Region: **Same as Proxy VM** (check Proxy VM's region)
   - Image: Ubuntu 22.04 LTS
   - Size: Same as old OCR VM (e.g., Standard_B2s or Standard_D2s_v3)
   - Authentication: SSH public key
   - Username: `azureuser`

3. **Networking:**
   - Virtual Network: **Select Proxy VM's VNet**
   - Subnet: Same subnet as Proxy VM (or different subnet in same VNet)
   - Public IP: Create new (or None if not needed)
   - NIC NSG: Basic
   - Public inbound ports: SSH (22)

4. **Review + Create**

#### Step 3: Setup OCR Service on New VM

```bash
# SSH into new VM
ssh azureuser@<NEW_VM_IP>

# Install dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv nginx

# Create directory
sudo mkdir -p /opt/qadam-ocr
sudo chown azureuser:azureuser /opt/qadam-ocr
cd /opt/qadam-ocr

# Clone or copy OCR service code
# Option 1: If you have backup
scp your-local-machine:~/ocr-backup.tar.gz .
tar -xzf ocr-backup.tar.gz

# Option 2: Clone from git (if available)
# git clone <your-repo> .

# Option 3: Reinstall from scratch
# Follow OCR_VM_SETUP.md

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Configure systemd service
sudo nano /etc/systemd/system/qadam-ocr.service
```

**Service file content:**
```ini
[Unit]
Description=Qadam OCR Service
After=network.target

[Service]
Type=simple
User=azureuser
WorkingDirectory=/opt/qadam-ocr
Environment="PATH=/opt/qadam-ocr/venv/bin"
ExecStart=/opt/qadam-ocr/venv/bin/gunicorn --workers 2 --timeout 300 --bind 127.0.0.1:8000 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable qadam-ocr
sudo systemctl start qadam-ocr
sudo systemctl status qadam-ocr
```

#### Step 4: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/qadam-ocr
```

```nginx
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
        
        proxy_buffering off;
    }
    
    client_max_body_size 20M;
}
```

```bash
sudo ln -s /etc/nginx/sites-available/qadam-ocr /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

#### Step 5: Test New OCR VM

```bash
# Test locally
curl http://localhost:8000/api/health
curl http://localhost/api/health

# Note the new PRIVATE IP
ip addr show | grep "inet " | grep -v "127.0.0.1"
```

#### Step 6: Update Proxy VM Configuration

```bash
# SSH into Proxy VM
ssh azureuser@130.107.48.166

# Update environment variable
cd /opt/qadam-backend/proxy
nano .env

# Change OCR_SERVICE_URL to new PRIVATE IP
OCR_SERVICE_URL=http://<NEW_PRIVATE_IP>

# Restart backend
sudo systemctl restart qadam-backend
```

#### Step 7: Test Connectivity

```bash
# From Proxy VM
ping <NEW_OCR_PRIVATE_IP>
curl http://<NEW_OCR_PRIVATE_IP>/api/health

# Should work since both VMs are in same VNet!
```

#### Step 8: Delete Old OCR VM

Once everything works:
```
Azure Portal → Virtual Machines → Old OCR VM (4.229.225.140)
→ Delete → Yes, delete associated resources
```

---

### Option B: Create from Snapshot (If you want to preserve everything)

This preserves the exact state of the old VM.

#### Step 1: Create Snapshot of Old OCR VM

**Azure Portal:**
1. Go to old OCR VM (4.229.225.140)
2. **Disks** → Click on OS disk
3. **+ Create snapshot**
   - Name: `ocr-vm-snapshot`
   - Snapshot type: Full
   - Click **Review + create**

#### Step 2: Create Image from Snapshot

1. Go to **Snapshots** → `ocr-vm-snapshot`
2. **+ Create image**
   - Name: `ocr-vm-image`
   - OS type: Linux
   - VM generation: Gen 1 (or Gen 2 if original was Gen 2)
   - Click **Review + create**

#### Step 3: Create New VM from Image

1. Go to **Images** → `ocr-vm-image`
2. **+ Create VM**
3. Configure:
   - Region: **Same as Proxy VM**
   - Virtual Network: **Proxy VM's VNet**
   - Subnet: Same or different subnet in VNet
4. Create VM

#### Step 4: Update IP in Proxy VM Config

Same as Option A, Step 6

---

## 🎯 Recommended Approach

**Use Option A (Quick Recreation)** because:
- ✅ Faster (30-60 minutes)
- ✅ Clean setup
- ✅ No snapshot/image overhead
- ✅ Latest packages
- ✅ Easier to troubleshoot

**Use Option B (Snapshot)** only if:
- ❌ Complex OCR configuration
- ❌ Custom models or data
- ❌ Unknown dependencies

## 📊 After Migration Checklist

- [ ] New OCR VM created in same VNet as Proxy VM
- [ ] OCR service running on new VM
- [ ] Nginx configured on new VM
- [ ] Can curl health endpoint locally on new VM
- [ ] Proxy VM updated with new OCR IP
- [ ] Can ping new OCR VM from Proxy VM
- [ ] Can curl new OCR VM from Proxy VM
- [ ] Backend restarted on Proxy VM
- [ ] Test OCR from frontend (upload image)
- [ ] Old OCR VM deleted

## 🔍 Verify Same VNet

After creating new VM, verify both are in same VNet:

```bash
# On Proxy VM
ip addr show | grep "inet " | grep -v "127.0.0.1"
# Should show: 130.107.x.x

# On new OCR VM
ip addr show | grep "inet " | grep -v "127.0.0.1"
# Should show: 130.107.x.x (same 130.107 prefix)
```

## 💰 Cost Consideration

- New VM will have same cost as old VM
- Delete old VM to avoid double charges
- Snapshot/Image storage is minimal cost

## ⏱️ Estimated Time

- **Option A (Recreation):** 30-60 minutes
- **Option B (Snapshot):** 60-90 minutes

---

**Recommendation: Go with Option A (Quick Recreation) - it's faster and cleaner!**
