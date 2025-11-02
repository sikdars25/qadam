"""
Azure Blob Storage Helper
Handles file uploads and downloads from Azure Blob Storage
"""

import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from werkzeug.utils import secure_filename
from datetime import datetime

# Get connection string from environment
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
BLOB_CONTAINER_NAME = os.getenv('BLOB_CONTAINER_NAME', 'qadam-uploads')

def get_blob_service_client():
    """Get Azure Blob Service Client"""
    if not AZURE_STORAGE_CONNECTION_STRING:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING not set in environment variables")
    
    return BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

def ensure_container_exists():
    """Ensure the blob container exists"""
    try:
        blob_service_client = get_blob_service_client()
        container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)
        
        # Try to get container properties
        try:
            container_client.get_container_properties()
            print(f"✓ Container '{BLOB_CONTAINER_NAME}' already exists")
        except Exception:
            # Container doesn't exist, create it
            container_client.create_container()
            print(f"✓ Created container '{BLOB_CONTAINER_NAME}'")
        
        return True
    except Exception as e:
        print(f"❌ Error ensuring container exists: {e}")
        return False

def upload_file_to_blob(file, folder='uploads'):
    """
    Upload a file to Azure Blob Storage
    
    Args:
        file: FileStorage object from Flask request
        folder: Folder name in blob storage (e.g., 'papers', 'textbooks')
    
    Returns:
        dict: {'success': bool, 'blob_url': str, 'blob_name': str, 'error': str}
    """
    try:
        # Ensure container exists
        if not ensure_container_exists():
            return {'success': False, 'error': 'Failed to access blob storage'}
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        blob_name = f"{folder}/{timestamp}_{filename}"
        
        # Get blob client
        blob_service_client = get_blob_service_client()
        blob_client = blob_service_client.get_blob_client(
            container=BLOB_CONTAINER_NAME,
            blob=blob_name
        )
        
        # Upload file
        print(f"📤 Uploading to blob: {blob_name}")
        file.seek(0)  # Reset file pointer
        blob_client.upload_blob(file, overwrite=True)
        
        # Get blob URL
        blob_url = blob_client.url
        
        print(f"✓ File uploaded successfully: {blob_url}")
        
        return {
            'success': True,
            'blob_url': blob_url,
            'blob_name': blob_name,
            'container': BLOB_CONTAINER_NAME
        }
        
    except Exception as e:
        print(f"❌ Blob upload error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }

def download_blob_to_file(blob_name, local_path):
    """
    Download a blob to a local file
    
    Args:
        blob_name: Name of the blob in storage
        local_path: Local path to save the file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        blob_service_client = get_blob_service_client()
        blob_client = blob_service_client.get_blob_client(
            container=BLOB_CONTAINER_NAME,
            blob=blob_name
        )
        
        # Create directory if needed
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # Download blob
        print(f"📥 Downloading blob: {blob_name} to {local_path}")
        with open(local_path, 'wb') as f:
            blob_data = blob_client.download_blob()
            blob_data.readinto(f)
        
        print(f"✓ Blob downloaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Blob download error: {e}")
        return False

def get_blob_url(blob_name):
    """
    Get the URL for a blob
    
    Args:
        blob_name: Name of the blob in storage
    
    Returns:
        str: Blob URL or None
    """
    try:
        blob_service_client = get_blob_service_client()
        blob_client = blob_service_client.get_blob_client(
            container=BLOB_CONTAINER_NAME,
            blob=blob_name
        )
        return blob_client.url
    except Exception as e:
        print(f"❌ Error getting blob URL: {e}")
        return None

def delete_blob(blob_name):
    """
    Delete a blob from storage
    
    Args:
        blob_name: Name of the blob to delete
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        blob_service_client = get_blob_service_client()
        blob_client = blob_service_client.get_blob_client(
            container=BLOB_CONTAINER_NAME,
            blob=blob_name
        )
        
        print(f"🗑️ Deleting blob: {blob_name}")
        blob_client.delete_blob()
        print(f"✓ Blob deleted successfully")
        return True
        
    except Exception as e:
        print(f"❌ Blob delete error: {e}")
        return False

def download_blob_to_temp(blob_name):
    """
    Download a blob to a temporary file
    
    Args:
        blob_name: Name of the blob in storage
    
    Returns:
        str: Path to temporary file or None
    """
    try:
        import tempfile
        
        blob_service_client = get_blob_service_client()
        blob_client = blob_service_client.get_blob_client(
            container=BLOB_CONTAINER_NAME,
            blob=blob_name
        )
        
        # Create temp file with same extension
        _, ext = os.path.splitext(blob_name)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        temp_path = temp_file.name
        temp_file.close()
        
        # Download blob
        print(f"📥 Downloading blob to temp: {blob_name}")
        with open(temp_path, 'wb') as f:
            blob_data = blob_client.download_blob()
            blob_data.readinto(f)
        
        print(f"✓ Downloaded to: {temp_path}")
        return temp_path
        
    except Exception as e:
        print(f"❌ Temp download error: {e}")
        return None

def check_blob_storage_available():
    """Check if blob storage is configured and available"""
    try:
        if not AZURE_STORAGE_CONNECTION_STRING:
            print("⚠️ AZURE_STORAGE_CONNECTION_STRING not configured")
            return False
        
        blob_service_client = get_blob_service_client()
        # Try to list containers to verify connection
        list(blob_service_client.list_containers(max_results=1))
        print("✓ Blob storage is available")
        return True
    except Exception as e:
        print(f"⚠️ Blob storage not available: {e}")
        return False

# Initialize on import
BLOB_STORAGE_ENABLED = check_blob_storage_available()

if BLOB_STORAGE_ENABLED:
    print("✅ Azure Blob Storage enabled")
    ensure_container_exists()
else:
    print("⚠️ Azure Blob Storage disabled - files will be stored locally (ephemeral)")
