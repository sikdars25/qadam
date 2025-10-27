"""
Migration Script: MySQL to Cosmos DB
Migrates all data from MySQL to Azure Cosmos DB
"""

import mysql.connector
from cosmos_db import (
    init_cosmos_db,
    create_user,
    save_question_to_bank,
    save_uploaded_paper,
    save_textbook,
    log_user_activity,
    get_user_by_username
)
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# MySQL Configuration
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'qadam_academic'),
}

def get_mysql_connection():
    """Get MySQL connection"""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Error connecting to MySQL: {e}")
        return None

def migrate_users():
    """Migrate users from MySQL to Cosmos DB"""
    print("\n" + "="*60)
    print("📊 MIGRATING USERS")
    print("="*60)
    
    conn = get_mysql_connection()
    if not conn:
        return 0
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        
        migrated = 0
        skipped = 0
        
        for user in users:
            # Check if user already exists
            existing = get_user_by_username(user['username'])
            if existing:
                print(f"⚠️ User already exists: {user['username']}")
                skipped += 1
                continue
            
            # Create user in Cosmos DB
            result = create_user(
                username=user['username'],
                password=user['password'],
                full_name=user['full_name'],
                email=user.get('email'),
                phone=user.get('phone'),
                is_admin=user.get('is_admin', False)
            )
            
            if result:
                migrated += 1
                print(f"✅ Migrated user: {user['username']}")
            else:
                print(f"❌ Failed to migrate: {user['username']}")
        
        cursor.close()
        conn.close()
        
        print(f"\n📊 Users Migration Summary:")
        print(f"   Total: {len(users)}")
        print(f"   Migrated: {migrated}")
        print(f"   Skipped: {skipped}")
        
        return migrated
        
    except Exception as e:
        print(f"❌ Error migrating users: {e}")
        return 0

def migrate_uploaded_papers():
    """Migrate uploaded papers from MySQL to Cosmos DB"""
    print("\n" + "="*60)
    print("📄 MIGRATING UPLOADED PAPERS")
    print("="*60)
    
    conn = get_mysql_connection()
    if not conn:
        return 0
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM uploaded_papers")
        papers = cursor.fetchall()
        
        migrated = 0
        
        for paper in papers:
            # Map MySQL user ID to Cosmos DB user ID
            # Note: You'll need to handle ID mapping if IDs changed
            result = save_uploaded_paper(
                user_id=str(paper['user_id']),  # Convert to string for Cosmos
                title=paper['title'],
                subject=paper.get('subject', 'Unknown'),
                board=paper.get('board', 'Unknown'),
                year=paper.get('year'),
                file_path=paper['file_path']
            )
            
            if result:
                migrated += 1
                print(f"✅ Migrated paper: {paper['title']}")
            else:
                print(f"❌ Failed to migrate: {paper['title']}")
        
        cursor.close()
        conn.close()
        
        print(f"\n📊 Papers Migration Summary:")
        print(f"   Total: {len(papers)}")
        print(f"   Migrated: {migrated}")
        
        return migrated
        
    except Exception as e:
        print(f"❌ Error migrating papers: {e}")
        import traceback
        traceback.print_exc()
        return 0

def migrate_textbooks():
    """Migrate textbooks from MySQL to Cosmos DB"""
    print("\n" + "="*60)
    print("📚 MIGRATING TEXTBOOKS")
    print("="*60)
    
    conn = get_mysql_connection()
    if not conn:
        return 0
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM textbooks")
        textbooks = cursor.fetchall()
        
        migrated = 0
        
        for textbook in textbooks:
            result = save_textbook(
                title=textbook['title'],
                subject=textbook.get('subject', 'Unknown'),
                board=textbook.get('board', 'Unknown'),
                file_path=textbook['file_path'],
                user_id=str(textbook.get('user_id')) if textbook.get('user_id') else None
            )
            
            if result:
                migrated += 1
                print(f"✅ Migrated textbook: {textbook['title']}")
            else:
                print(f"❌ Failed to migrate: {textbook['title']}")
        
        cursor.close()
        conn.close()
        
        print(f"\n📊 Textbooks Migration Summary:")
        print(f"   Total: {len(textbooks)}")
        print(f"   Migrated: {migrated}")
        
        return migrated
        
    except Exception as e:
        print(f"❌ Error migrating textbooks: {e}")
        import traceback
        traceback.print_exc()
        return 0

def migrate_question_bank():
    """Migrate question bank from MySQL to Cosmos DB"""
    print("\n" + "="*60)
    print("💾 MIGRATING QUESTION BANK")
    print("="*60)
    
    conn = get_mysql_connection()
    if not conn:
        return 0
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM question_bank")
        questions = cursor.fetchall()
        
        migrated = 0
        
        for question in questions:
            result = save_question_to_bank(
                user_id=str(question['user_id']),
                question_text=question['question_text'],
                solution=question['solution'],
                source=question.get('source', 'unknown'),
                subject=question.get('subject'),
                paper_id=str(question['paper_id']) if question.get('paper_id') else None,
                textbook_id=str(question['textbook_id']) if question.get('textbook_id') else None,
                chapter_name=question.get('chapter_name'),
                timestamp=question.get('created_at').isoformat() if question.get('created_at') else None
            )
            
            if result:
                migrated += 1
                if migrated % 10 == 0:
                    print(f"✅ Migrated {migrated} questions...")
            else:
                print(f"❌ Failed to migrate question {question.get('id')}")
        
        cursor.close()
        conn.close()
        
        print(f"\n📊 Question Bank Migration Summary:")
        print(f"   Total: {len(questions)}")
        print(f"   Migrated: {migrated}")
        
        return migrated
        
    except Exception as e:
        print(f"❌ Error migrating question bank: {e}")
        import traceback
        traceback.print_exc()
        return 0

def run_full_migration():
    """Run complete migration from MySQL to Cosmos DB"""
    print("\n" + "🚀"*30)
    print("  MYSQL TO COSMOS DB MIGRATION")
    print("🚀"*30)
    
    # Initialize Cosmos DB
    print("\n📦 Initializing Cosmos DB...")
    if not init_cosmos_db():
        print("❌ Failed to initialize Cosmos DB. Aborting migration.")
        return
    
    # Confirm migration
    print("\n⚠️ WARNING: This will migrate data from MySQL to Cosmos DB")
    print("Make sure:")
    print("1. Cosmos DB Emulator is running")
    print("2. MySQL database is accessible")
    print("3. You have backed up your MySQL data")
    
    confirm = input("\nProceed with migration? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Migration cancelled")
        return
    
    start_time = datetime.now()
    
    # Migrate in order (users first, then dependent tables)
    users_count = migrate_users()
    papers_count = migrate_uploaded_papers()
    textbooks_count = migrate_textbooks()
    questions_count = migrate_question_bank()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Print final summary
    print("\n" + "="*60)
    print("🎉 MIGRATION COMPLETE")
    print("="*60)
    print(f"Users migrated: {users_count}")
    print(f"Papers migrated: {papers_count}")
    print(f"Textbooks migrated: {textbooks_count}")
    print(f"Questions migrated: {questions_count}")
    print(f"Total time: {duration:.2f} seconds")
    print("="*60)
    
    print("\n✅ Next steps:")
    print("1. Verify data in Cosmos DB Emulator")
    print("2. Test the application with Cosmos DB")
    print("3. Update app.py to use Cosmos DB")
    print("4. Deploy to Azure with production Cosmos DB")

if __name__ == "__main__":
    run_full_migration()
