# OCR Service - Azure VM Configuration

## ⚠️ Important: Update OCR Service URL

The OCR service has been migrated from Azure Functions to Azure VM for better performance and cost efficiency.

### Update Backend Configuration

You need to set the `OCR_SERVICE_URL` environment variable in your Azure Function App:

```bash
az functionapp config appsettings set \
  --name qadam-backend \
  --resource-group qadam_bend_group \
  --settings OCR_SERVICE_URL=http://<YOUR_VM_PUBLIC_IP>
```

**Replace `<YOUR_VM_PUBLIC_IP>` with your actual VM's public IP address.**

### Find Your VM IP

```bash
# If you used the create-ocr-vm.sh script
az vm show --resource-group rg-qadam --name vm-qadam-ocr --show-details --query publicIps -o tsv

# Or check in Azure Portal
# VM → Overview → Public IP address
```

### API Endpoints

The VM Flask app uses these endpoints:

- `GET /api/health` - Health check
- `POST /api/extract-text` - Extract text from image
- `POST /api/extract-text-with-boxes` - Extract with bounding boxes
- `POST /api/extract-from-pdf` - Extract from PDF

### Test OCR Service

```bash
# Health check
curl http://<YOUR_VM_IP>/api/health

# Should return:
# {"status": "healthy", "service": "OCR Service"}
```

### Update Workflow

After setting the environment variable, redeploy the backend:

```bash
# Trigger backend deployment
git add backend/
git commit -m "fix: update OCR service URL to VM"
git push origin main
```

### Verify

After deployment, test the OCR integration:

```bash
# Check backend logs
az functionapp log tail --name qadam-backend --resource-group qadam_bend_group

# You should see:
# ✅ OCR service available at http://<YOUR_VM_IP>
```

---

## Migration Complete! 🎉

Your OCR service is now running on Azure VM with:
- ✅ No package size limits
- ✅ Better performance
- ✅ Lower cost (~$30-40/month vs $150+/month)
- ✅ Full control over environment
