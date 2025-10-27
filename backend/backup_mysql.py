"""
MySQL Backup Script
Alternative to mysqldump - creates a Python-based backup
"""

import mysql.connector
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# MySQL Configuration
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'qadam_academic'),
}

def backup_table(cursor, table_name):
    """Backup a single table"""
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute(f"DESCRIBE {table_name}")
        columns = [col[0] for col in cursor.fetchall()]
        
        # Convert to list of dicts
        data = []
        for row in rows:
            row_dict = {}
            for i, col in enumerate(columns):
                value = row[i]
                # Convert datetime to string
                if hasattr(value, 'isoformat'):
                    value = value.isoformat()
                row_dict[col] = value
            data.append(row_dict)
        
        return {
            'table': table_name,
            'columns': columns,
            'row_count': len(data),
            'data': data
        }
    except Exception as e:
        print(f"❌ Error backing up {table_name}: {e}")
        return None

def backup_database():
    """Backup entire database to JSON file"""
    print("🔄 Starting MySQL backup...")
    
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        print(f"📊 Found {len(tables)} tables: {', '.join(tables)}")
        
        backup_data = {
            'backup_date': datetime.now().isoformat(),
            'database': MYSQL_CONFIG['database'],
            'tables': {}
        }
        
        # Backup each table
        for table in tables:
            print(f"📦 Backing up table: {table}...")
            table_data = backup_table(cursor, table)
            if table_data:
                backup_data['tables'][table] = table_data
                print(f"   ✅ {table_data['row_count']} rows backed up")
        
        cursor.close()
        conn.close()
        
        # Save to JSON file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"mysql_backup_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        file_size = os.path.getsize(filename) / 1024  # KB
        
        print("\n" + "="*60)
        print("✅ BACKUP COMPLETE")
        print("="*60)
        print(f"File: {filename}")
        print(f"Size: {file_size:.2f} KB")
        print(f"Tables: {len(backup_data['tables'])}")
        
        # Print summary
        for table_name, table_data in backup_data['tables'].items():
            print(f"  - {table_name}: {table_data['row_count']} rows")
        
        print("="*60)
        print("\n✅ You can now run the migration script:")
        print("   python migrate_mysql_to_cosmos.py")
        
        return filename
        
    except mysql.connector.Error as e:
        print(f"❌ MySQL Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("\n" + "🔒"*30)
    print("  MYSQL DATABASE BACKUP")
    print("🔒"*30 + "\n")
    
    backup_database()
