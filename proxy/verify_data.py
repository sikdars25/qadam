#!/usr/bin/env python3
"""
Verify Data Script
Checks how many items are in each Cosmos DB container
Use this to verify cleanup worked
"""

import os
from dotenv import load_dotenv
from cosmos_db import get_cosmos_container

load_dotenv()

def count_items(container_name):
    """Count items in a container"""
    try:
        container = get_cosmos_container(container_name)
        query = "SELECT VALUE COUNT(1) FROM c"
        items = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        return items[0] if items else 0
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return -1

def main():
    """Main function"""
    print("=" * 60)
    print("📊 COSMOS DB DATA VERIFICATION")
    print("=" * 60)
    print()
    
    containers = [
        ('uploaded_papers', 'Uploaded Papers'),
        ('textbooks', 'Textbooks'),
        ('parsed_questions', 'Parsed Questions'),
        ('ai_search_results', 'AI Search Results'),
        ('users', 'User Accounts'),
        ('question_bank', 'Question Bank'),
    ]
    
    for container_name, description in containers:
        count = count_items(container_name)
        if count >= 0:
            status = "✅ Empty" if count == 0 else f"📊 {count} items"
            print(f"{description:.<40} {status}")
        else:
            print(f"{description:.<40} ❌ Error")
    
    print()
    print("=" * 60)

if __name__ == '__main__':
    main()
