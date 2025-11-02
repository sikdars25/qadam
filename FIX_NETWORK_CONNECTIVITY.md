# Fix Network Connectivity Between Proxy and OCR VMs

## 🐛 Problem
POST request from frontend reaches Proxy VM but Proxy VM **cannot connect to OCR VM**.

**Evidence:**
- Frontend logs show POST request is sent with JWT token ✅
- Proxy VM logs show OPTIONS request but no POST ❌
- OCR VM never receives any request ❌
- Different IP ranges: 130.107.48.166 vs 4.229.225.140

**Root Cause:** Network connectivity issue between VMs, likely due to:
1. Different Azure regions
2. Different Virtual Networks (VNets) without peering
3. Network Security Group (NSG) blocking traffic
4. Firewall rules blocking traffic

## 🔍 Diagnosis

### Step 1: Test Connectivity from Proxy VM

SSH into Proxy VM:
```bash
ssh azureuser@130.107.48.166
```

Test basic connectivity:
```bash
# Test ping
ping -c 3 4.229.225.140

# Test port 80
telnet 4.229.225.140 80
# Or
nc -zv 4.229.225.140 80

# Test HTTP
curl -v http://4.229.225.140/api/health
```

**Expected if working:**
```
✅ Ping replies received
✅ Port 80 is open
✅ HTTP 200 OK response
```

**If failing:**
```
❌ Request timeout
❌ Connection refused
❌ No route to host
```

### Step 2: Check Azure Network Configuration

#### A. Check if VMs are in same Virtual Network

**Azure Portal:**
1. Go to Virtual Machines
2. Click on Proxy VM (130.107.48.166)
3. Go to Networking → Note the **Virtual Network** name
4. Click on OCR VM (4.229.225.140)
5. Go to Networking → Note the **Virtual Network** name

**If different VNets:** You need VNet peering (see Solution 1)
**If same VNet:** Check NSG rules (see Solution 2)

#### B. Check Network Security Groups (NSG)

**For OCR VM:**
1. Azure Portal → Virtual Machines → OCR VM
2. Networking → Network Security Group
3. Inbound security rules
4. Look for rule allowing port 80

**For Proxy VM:**
1. Azure Portal → Virtual Machines → Proxy VM
2. Networking → Network Security Group
3. Outbound security rules
4. Should allow outbound traffic

## ✅ Solutions

### Solution 1: Set Up VNet Peering (If VMs in Different VNets)

**Azure Portal:**

1. Go to **Virtual Networks**
2. Select Proxy VM's VNet
3. Click **Peerings** in left menu
4. Click **+ Add**
5. Configure peering:
   - Name: `proxy-to-ocr-peering`
   - Remote VNet: Select OCR VM's VNet
   - Allow virtual network access: **Yes**
   - Allow forwarded traffic: **Yes**
6. Click **Add**

7. Repeat for OCR VM's VNet:
   - Name: `ocr-to-proxy-peering`
   - Remote VNet: Select Proxy VM's VNet

**Verify:**
```bash
# From Proxy VM
ping 4.229.225.140
curl http://4.229.225.140/api/health
```

### Solution 2: Configure Network Security Groups

#### A. Allow Inbound Traffic on OCR VM

**Azure Portal:**
1. Go to OCR VM → Networking
2. Click on Network Security Group name
3. Click **Inbound security rules**
4. Click **+ Add**
5. Configure:
   - Source: **IP Addresses**
   - Source IP addresses: `130.107.48.166`
   - Source port ranges: `*`
   - Destination: **Any**
   - Destination port ranges: `80`
   - Protocol: **TCP**
   - Action: **Allow**
   - Priority: `100`
   - Name: `Allow-Proxy-VM`
6. Click **Add**

#### B. Allow Outbound Traffic on Proxy VM (Usually already allowed)

**Azure Portal:**
1. Go to Proxy VM → Networking
2. Click on Network Security Group name
3. Click **Outbound security rules**
4. Verify there's a rule allowing outbound to Internet or specific IP

**Default rule should exist:**
- Name: `AllowInternetOutBound`
- Destination: `Internet`
- Action: `Allow`

### Solution 3: Configure VM Firewalls

#### On OCR VM:

```bash
ssh azureuser@4.229.225.140

# Check firewall status
sudo ufw status

# Allow port 80 from Proxy VM
sudo ufw allow from 130.107.48.166 to any port 80

# Or allow port 80 from anywhere (less secure)
sudo ufw allow 80/tcp

# Enable firewall if not enabled
sudo ufw enable
```

#### On Proxy VM:

```bash
# Usually no changes needed for outbound
# But verify firewall allows outbound
sudo ufw status
```

### Solution 4: Use Azure Connection Troubleshoot

**Azure Portal:**
1. Go to Proxy VM
2. Click **Connection troubleshoot** (under Support + troubleshooting)
3. Configure:
   - Source: Proxy VM
   - Destination: Manual input
   - Destination IP: `4.229.225.140`
   - Destination port: `80`
   - Protocol: TCP
4. Click **Check**

This will show exactly where the connection is failing.

## 🔧 Alternative: Use Azure Private Endpoint or Service Endpoint

If VNet peering doesn't work, consider:

### Option A: Put both VMs in same VNet

1. Create new VNet or use existing
2. Move both VMs to same VNet
3. Update NSG rules

### Option B: Use Public IP with NSG rules

Keep VMs in different VNets but:
1. Ensure OCR VM has public IP
2. Configure NSG to allow traffic from Proxy VM's public IP
3. Use public IP in `OCR_SERVICE_URL`

## 📊 Verify Fix

After applying fixes, test from Proxy VM:

```bash
# Test connectivity
ping -c 3 4.229.225.140

# Test HTTP
curl http://4.229.225.140/api/health

# Should return:
# {"status":"healthy","service":"OCR","version":"1.0.0"}
```

Test from backend:
```bash
cd /opt/qadam-backend/proxy
source venv/bin/activate
python -c "from ocr_client import check_ocr_service; print('OCR Available:', check_ocr_service())"

# Should print: OCR Available: True
```

## 🎯 Quick Checklist

- [ ] VMs in same VNet OR VNet peering configured
- [ ] NSG allows inbound port 80 on OCR VM from Proxy VM
- [ ] NSG allows outbound traffic on Proxy VM
- [ ] VM firewall (ufw) allows port 80 on OCR VM
- [ ] OCR service is running on OCR VM
- [ ] Can ping OCR VM from Proxy VM
- [ ] Can curl OCR health endpoint from Proxy VM

## 🆘 Still Not Working?

### Check Azure Region

```bash
# On Proxy VM
curl -H Metadata:true "http://169.254.169.254/metadata/instance?api-version=2021-02-01" | jq '.compute.location'

# On OCR VM  
curl -H Metadata:true "http://169.254.169.254/metadata/instance?api-version=2021-02-01" | jq '.compute.location'
```

If in different regions, VNet peering is required.

### Check Subnet Configuration

Ensure subnets don't have conflicting routes or NSGs.

### Contact Azure Support

If nothing works, open Azure support ticket:
- Issue: VM-to-VM connectivity
- Provide: Both VM resource IDs
- Describe: Cannot connect from 130.107.48.166 to 4.229.225.140:80

---

**Most likely fix: Configure NSG to allow inbound port 80 on OCR VM from Proxy VM's IP address.**
