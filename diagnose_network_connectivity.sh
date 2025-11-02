#!/bin/bash

# Network Connectivity Diagnostic Script
# Run this on Proxy VM (130.107.48.166) to test connectivity to OCR VM

echo "🔍 Network Connectivity Diagnostics"
echo "===================================="
echo ""
echo "Proxy VM: 130.107.48.166"
echo "OCR VM:   4.229.225.140"
echo ""

# 1. Test basic network connectivity
echo "1️⃣ Testing ICMP (ping) connectivity..."
if ping -c 3 4.229.225.140 > /dev/null 2>&1; then
    echo "   ✅ Can ping OCR VM"
else
    echo "   ❌ Cannot ping OCR VM"
    echo "   → VMs might be in different regions/VNets"
    echo "   → ICMP might be blocked by firewall"
fi
echo ""

# 2. Test TCP connectivity to port 80
echo "2️⃣ Testing TCP port 80 connectivity..."
if timeout 5 bash -c "cat < /dev/null > /dev/tcp/4.229.225.140/80" 2>/dev/null; then
    echo "   ✅ Can connect to port 80 on OCR VM"
else
    echo "   ❌ Cannot connect to port 80 on OCR VM"
    echo "   → Port might be blocked by NSG (Network Security Group)"
    echo "   → VMs might be in different VNets without peering"
fi
echo ""

# 3. Test HTTP request
echo "3️⃣ Testing HTTP request to OCR health endpoint..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://4.229.225.140/api/health 2>/dev/null)
if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ HTTP request successful (200 OK)"
    curl -s http://4.229.225.140/api/health | jq '.' 2>/dev/null || echo "   Response: $(curl -s http://4.229.225.140/api/health)"
elif [ "$HTTP_CODE" = "000" ]; then
    echo "   ❌ Connection failed (timeout or refused)"
    echo "   → Network connectivity issue"
else
    echo "   ⚠️ HTTP request returned: $HTTP_CODE"
fi
echo ""

# 4. Check routing
echo "4️⃣ Checking route to OCR VM..."
echo "   Traceroute to 4.229.225.140:"
traceroute -m 10 -w 2 4.229.225.140 2>/dev/null || echo "   traceroute not available"
echo ""

# 5. Check DNS resolution
echo "5️⃣ Checking DNS resolution..."
if host 4.229.225.140 > /dev/null 2>&1; then
    echo "   ✅ DNS resolution works"
else
    echo "   ℹ️ Using IP address directly (no DNS needed)"
fi
echo ""

# 6. Check local network config
echo "6️⃣ Local network configuration..."
echo "   Local IP addresses:"
ip addr show | grep "inet " | grep -v "127.0.0.1"
echo ""
echo "   Default gateway:"
ip route | grep default
echo ""

# 7. Test from OCR VM back to Proxy VM
echo "7️⃣ Testing reverse connectivity (run on OCR VM)..."
echo "   SSH into OCR VM and run:"
echo "   ping -c 3 130.107.48.166"
echo "   curl http://130.107.48.166/api/health"
echo ""

# 8. Check Azure Network Security Groups
echo "8️⃣ Azure Network Security Group (NSG) Check..."
echo ""
echo "   ⚠️ CRITICAL: Check Azure Portal for NSG rules"
echo ""
echo "   On Proxy VM NSG (130.107.48.166):"
echo "   - Outbound rule: Allow TCP 80 to 4.229.225.140"
echo "   - Or: Allow all outbound to Internet"
echo ""
echo "   On OCR VM NSG (4.229.225.140):"
echo "   - Inbound rule: Allow TCP 80 from 130.107.48.166"
echo "   - Or: Allow TCP 80 from Internet"
echo ""

# 9. Check Virtual Network Peering
echo "9️⃣ Virtual Network Peering Check..."
echo ""
echo "   If VMs are in different VNets, you need VNet peering:"
echo ""
echo "   Azure Portal → Virtual Networks"
echo "   → Select Proxy VM's VNet"
echo "   → Peerings → Add peering"
echo "   → Peer to OCR VM's VNet"
echo ""

# 10. Recommendations
echo "📋 Troubleshooting Steps:"
echo "========================"
echo ""
echo "If connectivity test fails, check in Azure Portal:"
echo ""
echo "1. Network Security Groups (NSG):"
echo "   - Proxy VM NSG: Allow outbound to 4.229.225.140:80"
echo "   - OCR VM NSG: Allow inbound from 130.107.48.166:80"
echo ""
echo "2. Virtual Network Configuration:"
echo "   - Check if VMs are in same VNet"
echo "   - If different VNets, set up VNet peering"
echo ""
echo "3. Firewall Rules (on VMs):"
echo "   - Proxy VM: sudo ufw status (should allow outbound)"
echo "   - OCR VM: sudo ufw status (should allow port 80)"
echo ""
echo "4. Test from Azure Portal:"
echo "   - Use 'Connection troubleshoot' feature"
echo "   - VM → Networking → Connection troubleshoot"
echo "   - Source: Proxy VM, Dest: OCR VM, Port: 80"
echo ""

# 11. Quick fix commands
echo "🔧 Quick Fix Commands:"
echo "====================="
echo ""
echo "On OCR VM (4.229.225.140):"
echo "  sudo ufw allow from 130.107.48.166 to any port 80"
echo "  sudo ufw allow 80/tcp"
echo ""
echo "On Proxy VM (130.107.48.166):"
echo "  # No firewall changes needed for outbound"
echo ""
echo "In Azure Portal:"
echo "  1. Go to OCR VM → Networking → Network Security Group"
echo "  2. Add inbound rule:"
echo "     - Source: IP Address"
echo "     - Source IP: 130.107.48.166"
echo "     - Destination port: 80"
echo "     - Protocol: TCP"
echo "     - Action: Allow"
echo ""
