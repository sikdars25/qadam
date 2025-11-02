# 🔑 Get Storage Account Connection String

## Updated Steps for Azure Portal (2024)

### Method 1: Using Access Keys (Recommended)

1. **Go to Storage Account:**
   - Open Azure Portal: https://portal.azure.com
   - Search for your storage account name (e.g., `qadamstorage`)
   - Click on the storage account

2. **Navigate to Access Keys:**
   - In the left sidebar, look under **Security + networking**
   - Click **Access keys**

3. **Show and Copy Connection String:**
   - You'll see **key1** and **key2**
   - Under **key1**, find the field labeled **Connection string**
   - Click the **Show** button (eye icon) next to it
   - Click the **Copy to clipboard** icon
   - This is your connection string!

### Method 2: Using Azure CLI (Faster)

```bash
# Login to Azure
az login

# Get connection string (replace STORAGE_NAME with your storage account name)
az storage account show-connection-string \
  --name qadamstorage \
  --resource-group qadam-resources \
  --query connectionString -o tsv
```

This will output the connection string directly.

### Method 3: Manual Construction

If you can't find it, construct it manually:

**Format:**
```
DefaultEndpointsProtocol=https;AccountName=STORAGE_NAME;AccountKey=STORAGE_KEY;EndpointSuffix=core.windows.net
```

**Steps:**
1. Go to Storage Account → **Access keys**
2. Copy **Storage account name** (e.g., `qadamstorage`)
3. Click **Show** next to **key1**
4. Copy the **Key** value
5. Build the connection string:
   ```
   DefaultEndpointsProtocol=https;AccountName=qadamstorage;AccountKey=YOUR_COPIED_KEY;EndpointSuffix=core.windows.net
   ```

---

## What the Connection String Looks Like

```
DefaultEndpointsProtocol=https;
AccountName=qadamstorage;
AccountKey=abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ==;
EndpointSuffix=core.windows.net
```

(All on one line, no line breaks)

---

## Where to Use It

Once you have the connection string:

1. **Go to Function App** → `qadam-backend`
2. **Configuration** → **Application settings**
3. **+ New application setting**
4. **Name:** `AzureWebJobsStorage`
5. **Value:** [Paste the entire connection string]
6. **Save**

---

## Troubleshooting

### Can't Find "Access keys"?

**New Azure Portal Layout:**
- Click on your storage account
- Look in the left menu under **Security + networking** section
- Click **Access keys**

### Still Can't Find It?

**Alternative Path:**
1. Storage account → **Settings** section
2. Look for **Access keys** or **Shared access signature**
3. Use **Access keys** option

### Permission Error?

If you see "You do not have permission to view keys":
- You need **Storage Account Contributor** or **Owner** role
- Ask your Azure admin to grant access
- Or use Azure CLI with your credentials

---

## Quick CLI Command

```bash
# One command to get connection string
az storage account show-connection-string \
  --name qadamstorage \
  --resource-group qadam-resources
```

Copy the value from the output.

---

## Visual Guide

```
Azure Portal
  └── Storage Account (qadamstorage)
      └── Left Sidebar
          └── Security + networking
              └── Access keys
                  └── key1
                      └── Connection string [Show] [Copy]
```

---

**Tip:** Use Azure CLI method if you can't find it in the portal - it's faster! 🚀
