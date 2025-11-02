#!/usr/bin/env python3
"""
Clear All Data Script (Including Blob Storage)
Deletes all papers, textbooks, and parsed questions from Cosmos DB AND Blob Storage
Use this to start fresh when there are data inconsistencies
"""

import os
from dotenv import load_dotenv
from cosmos_db import get_cosmos_container
from azure.cosmos import exceptions
from azure.storage.blob import BlobServiceClient

load_dotenv()

# Blob Storage Configuration
BLOB_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
BLOB_CONTAINER_NAME = os.getenv('BLOB_CONTAINER_NAME', 'qadam-files')

def clear_container(container_name, description):
    """Clear all items from a Cosmos DB container"""
    try:
        container = get_cosmos_container(container_name)
        print(f"\n🗑️  Clearing {description} from Cosmos DB...")
        
        # Query all items
        query = "SELECT c.id, c.user_id FROM c"
        
        # For containers with different partition keys
        if container_name == 'textbooks':
            query = "SELECT c.id, c.subject FROM c"
        elif container_name == 'parsed_questions':
            query = "SELECT c.id, c.paper_id FROM c"
        elif container_name == 'ai_search_results':
            query = "SELECT c.id, c.paper_id FROM c"
        
        items = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        print(f"   Found {len(items)} items")
        
        if len(items) == 0:
            print(f"   ✓ Container is already empty")
            return 0
        
        deleted_count = 0
        failed_count = 0
        
        for item in items:
            try:
                item_id = item.get('id')
                
                # Get partition key based on container
                if container_name == 'textbooks':
                    partition_key = item.get('subject')
                elif container_name == 'parsed_questions':
                    partition_key = item.get('paper_id')
                elif container_name == 'ai_search_results':
                    partition_key = item.get('paper_id')
                else:
                    partition_key = item.get('user_id')
                
                # Delete the item
                container.delete_item(item=item_id, partition_key=partition_key)
                deleted_count += 1
                
                if deleted_count % 10 == 0:
                    print(f"   Deleted {deleted_count}/{len(items)}...")
                    
            except Exception as e:
                failed_count += 1
                print(f"   ⚠️  Failed to delete {item_id}: {e}")
        
        print(f"   ✅ Deleted {deleted_count} items")
        if failed_count > 0:
            print(f"   ⚠️  Failed to delete {failed_count} items")
        
        return deleted_count
        
    except Exception as e:
        print(f"   ❌ Error clearing {description}: {e}")
        return 0

def clear_blob_storage():
    """Clear all files from Blob Storage"""
    try:
        if not BLOB_CONNECTION_STRING:
            print("\n⚠️  Blob Storage connection string not found - skipping blob cleanup")
            return 0
        
        print(f"\n🗑️  Clearing Blob Storage ({BLOB_CONTAINER_NAME})...")
        
        blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)
        
        # List all blobs
        blobs = list(container_client.list_blobs())
        print(f"   Found {len(blobs)} files")
        
        if len(blobs) == 0:
            print(f"   ✓ Blob storage is already empty")
            return 0
        
        deleted_count = 0
        failed_count = 0
        
        for blob in blobs:
            try:
                container_client.delete_blob(blob.name)
                deleted_count += 1
                
                if deleted_count % 10 == 0:
                    print(f"   Deleted {deleted_count}/{len(blobs)} files...")
                    
            except Exception as e:
                failed_count += 1
                print(f"   ⚠️  Failed to delete {blob.name}: {e}")
        
        print(f"   ✅ Deleted {deleted_count} files")
        if failed_count > 0:
            print(f"   ⚠️  Failed to delete {failed_count} files")
        
        return deleted_count
        
    except Exception as e:
        print(f"   ❌ Error clearing blob storage: {e}")
        return 0

def main():
    """Main function"""
    print("=" * 60)
    print("🗑️  CLEAR ALL DATA - Cosmos DB + Blob Storage")
    print("=" * 60)
    print()
    print("⚠️  WARNING: This will delete ALL data from:")
    print("   - Uploaded Papers (DB + Files)")
    print("   - Textbooks (DB + Files)")
    print("   - Parsed Questions (DB)")
    print("   - AI Search Results (DB)")
    print()
    
    # Confirm
    confirm = input("Are you sure you want to continue? Type 'YES' to confirm: ")
    if confirm != 'YES':
        print("❌ Cancelled")
        return
    
    print("\n🚀 Starting cleanup...\n")
    
    total_deleted = 0
    
    # Clear Cosmos DB containers
    total_deleted += clear_container('uploaded_papers', 'Uploaded Papers')
    total_deleted += clear_container('textbooks', 'Textbooks')
    total_deleted += clear_container('parsed_questions', 'Parsed Questions')
    total_deleted += clear_container('ai_search_results', 'AI Search Results')
    
    # Clear Blob Storage
    total_deleted += clear_blob_storage()
    
    print("\n" + "=" * 60)
    print(f"✅ Cleanup complete! Total items deleted: {total_deleted}")
    print("=" * 60)
    print()
    print("📝 Note: User accounts and question bank are preserved")
    print("   You can now upload papers and textbooks fresh")
    print()
    print("🔄 IMPORTANT: Restart the backend service for changes to take effect:")
    print("   sudo systemctl restart qadam-backend")
    print()
    print("🌐 Then refresh the frontend (Ctrl+Shift+R) to clear browser cache")

if __name__ == '__main__':
    main()
