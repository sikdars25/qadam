"""
Migrate Cosmos DB Data from Local Emulator to Azure Cosmos DB
Copies all containers and documents from local to Azure
"""

import os
import sys
from dotenv import load_dotenv
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Source: Local Cosmos DB Emulator
LOCAL_ENDPOINT = os.getenv('COSMOS_ENDPOINT_LOCAL', 'https://localhost:8081')
LOCAL_KEY = os.getenv('COSMOS_KEY_LOCAL', 'C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==')
LOCAL_DATABASE = os.getenv('COSMOS_DATABASE_LOCAL', 'qadam_academic')

# Target: Azure Cosmos DB
AZURE_ENDPOINT = os.getenv('COSMOS_ENDPOINT')
AZURE_KEY = os.getenv('COSMOS_KEY')
AZURE_DATABASE = os.getenv('COSMOS_DATABASE', 'qadam')

# Container configurations with partition keys (must match cosmos_db.py)
CONTAINERS = {
    'users': '/username',
    'uploaded_papers': '/user_id',
    'textbooks': '/subject',
    'question_bank': '/user_id',
    'usage_logs': '/user_id',
    'parsed_questions': '/paper_id',
    'ai_search_results': '/paper_id'
}

def connect_to_cosmos(endpoint, key, database_name):
    """Connect to Cosmos DB and return database reference"""
    try:
        client = CosmosClient(endpoint, key)
        database = client.get_database_client(database_name)
        print(f"✓ Connected to: {endpoint}")
        return client, database
    except Exception as e:
        print(f"❌ Failed to connect to {endpoint}: {e}")
        return None, None

def create_container_if_not_exists(database, container_name, partition_key):
    """Create container in target database if it doesn't exist"""
    try:
        container = database.get_container_client(container_name)
        # Try to read to check if exists
        container.read()
        print(f"  ✓ Container '{container_name}' already exists")
        return container
    except exceptions.CosmosResourceNotFoundError:
        # Container doesn't exist, create it
        print(f"  📦 Creating container '{container_name}'...")
        container = database.create_container(
            id=container_name,
            partition_key=PartitionKey(path=partition_key)
        )
        print(f"  ✓ Container '{container_name}' created")
        return container
    except Exception as e:
        print(f"  ❌ Error with container '{container_name}': {e}")
        return None

def migrate_container(source_db, target_db, container_name, partition_key):
    """Migrate all documents from source to target container"""
    print(f"\n📂 Migrating container: {container_name}")
    
    try:
        # Get source container
        source_container = source_db.get_container_client(container_name)
        
        # Create or get target container
        target_container = create_container_if_not_exists(target_db, container_name, partition_key)
        if not target_container:
            return 0, 0
        
        # Query all documents from source
        print(f"  📖 Reading documents from local...")
        query = "SELECT * FROM c"
        items = list(source_container.query_items(query=query, enable_cross_partition_query=True))
        
        if not items:
            print(f"  ℹ No documents found in '{container_name}'")
            return 0, 0
        
        print(f"  📊 Found {len(items)} documents")
        
        # Migrate documents
        migrated = 0
        skipped = 0
        
        for item in items:
            try:
                # Check if document already exists in target
                doc_id = item.get('id')
                partition_key_field = partition_key.replace('/', '')
                partition_key_value = item.get(partition_key_field)
                
                # Handle missing partition key field
                if not partition_key_value:
                    print(f"    ⚠ Warning: Document {doc_id} missing partition key '{partition_key_field}'")
                    # Add default partition key based on container
                    if container_name == 'uploaded_papers':
                        # Use paper_id as user_id for papers without user_id
                        item['user_id'] = item.get('id', 'unknown')
                        partition_key_value = item['user_id']
                        print(f"      → Added default user_id: {partition_key_value}")
                    elif container_name == 'textbooks':
                        # Try to get subject from various fields
                        subject = item.get('subject') or item.get('title') or item.get('name') or 'General'
                        item['subject'] = subject
                        partition_key_value = subject
                        print(f"      → Added default subject: {partition_key_value}")
                    elif container_name == 'users':
                        # Use email or id as username for users without username
                        username = item.get('username') or item.get('email') or item.get('id', 'unknown')
                        item['username'] = username
                        partition_key_value = username
                        print(f"      → Added default username: {partition_key_value}")
                    else:
                        # For other containers, try to use a generic approach
                        # Use the document ID as the partition key value
                        item[partition_key_field] = item.get('id', 'unknown')
                        partition_key_value = item[partition_key_field]
                        print(f"      → Added default {partition_key_field}: {partition_key_value}")
                
                # Double-check partition key value exists
                if not partition_key_value:
                    print(f"      ❌ Skipping document - cannot determine partition key")
                    skipped += 1
                    continue
                
                try:
                    target_container.read_item(item=doc_id, partition_key=partition_key_value)
                    print(f"    ⏭ Skipped (exists): {doc_id}")
                    skipped += 1
                    continue
                except exceptions.CosmosResourceNotFoundError:
                    pass  # Document doesn't exist, proceed with insert
                
                # Insert document into target
                target_container.create_item(body=item)
                migrated += 1
                print(f"    ✓ Migrated: {doc_id}")
                
            except Exception as e:
                print(f"    ❌ Failed to migrate document {item.get('id', 'unknown')}: {e}")
        
        print(f"  ✅ Migration complete: {migrated} migrated, {skipped} skipped")
        return migrated, skipped
        
    except exceptions.CosmosResourceNotFoundError:
        print(f"  ℹ Container '{container_name}' not found in source database")
        return 0, 0
    except Exception as e:
        print(f"  ❌ Error migrating container '{container_name}': {e}")
        return 0, 0

def main():
    """Main migration function"""
    print("=" * 70)
    print("🚀 Cosmos DB Migration: Local Emulator → Azure")
    print("=" * 70)
    
    # Validate Azure credentials
    if not AZURE_ENDPOINT or not AZURE_KEY:
        print("\n❌ ERROR: Azure Cosmos DB credentials not found!")
        print("Please set the following environment variables:")
        print("  - COSMOS_ENDPOINT (Azure Cosmos DB URI)")
        print("  - COSMOS_KEY (Azure Cosmos DB Primary Key)")
        print("  - COSMOS_DATABASE (optional, defaults to 'qadam')")
        print("\nYou can add these to your .env file:")
        print(f"  COSMOS_ENDPOINT=https://your-account.documents.azure.com:443/")
        print(f"  COSMOS_KEY=your_primary_key_here")
        print(f"  COSMOS_DATABASE=qadam")
        sys.exit(1)
    
    print(f"\n📍 Source: {LOCAL_ENDPOINT} (Database: {LOCAL_DATABASE})")
    print(f"📍 Target: {AZURE_ENDPOINT} (Database: {AZURE_DATABASE})")
    
    # Confirm migration
    print("\n⚠️  WARNING: This will copy all data from local to Azure.")
    print("   Existing documents with same IDs will be skipped.")
    response = input("\nProceed with migration? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("❌ Migration cancelled")
        sys.exit(0)
    
    # Connect to source (local)
    print("\n🔌 Connecting to local Cosmos DB emulator...")
    local_client, local_db = connect_to_cosmos(LOCAL_ENDPOINT, LOCAL_KEY, LOCAL_DATABASE)
    if not local_db:
        print("❌ Failed to connect to local Cosmos DB")
        sys.exit(1)
    
    # Connect to target (Azure)
    print("\n🔌 Connecting to Azure Cosmos DB...")
    azure_client, azure_db = connect_to_cosmos(AZURE_ENDPOINT, AZURE_KEY, AZURE_DATABASE)
    if not azure_db:
        print("❌ Failed to connect to Azure Cosmos DB")
        sys.exit(1)
    
    # Migrate each container
    print("\n" + "=" * 70)
    print("📦 Starting container migration...")
    print("=" * 70)
    
    total_migrated = 0
    total_skipped = 0
    
    for container_name, partition_key in CONTAINERS.items():
        migrated, skipped = migrate_container(local_db, azure_db, container_name, partition_key)
        total_migrated += migrated
        total_skipped += skipped
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ MIGRATION COMPLETE")
    print("=" * 70)
    print(f"📊 Total documents migrated: {total_migrated}")
    print(f"⏭  Total documents skipped: {total_skipped}")
    print(f"📦 Containers processed: {len(CONTAINERS)}")
    print(f"\n🌐 Azure Cosmos DB: {AZURE_ENDPOINT}")
    print(f"📁 Database: {AZURE_DATABASE}")
    print("\n✨ Your data is now in Azure Cosmos DB!")
    
    # Create backup log
    log_file = f"migration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'source': LOCAL_ENDPOINT,
        'target': AZURE_ENDPOINT,
        'database': AZURE_DATABASE,
        'total_migrated': total_migrated,
        'total_skipped': total_skipped,
        'containers': list(CONTAINERS.keys())
    }
    
    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2)
    
    print(f"\n📝 Migration log saved: {log_file}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
