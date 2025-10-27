"""
Cosmos DB Database Layer
Migrated from MySQL to Azure Cosmos DB
"""

from azure.cosmos import CosmosClient, PartitionKey, exceptions
import os
from dotenv import load_dotenv
from datetime import datetime
import uuid

load_dotenv()

# Cosmos DB Configuration
COSMOS_ENDPOINT = os.getenv('COSMOS_ENDPOINT', 'https://localhost:8081')  # Emulator default
COSMOS_KEY = os.getenv('COSMOS_KEY', 'C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==')  # Emulator default key
DATABASE_NAME = os.getenv('COSMOS_DATABASE', 'qadam_academic')

# Initialize Cosmos Client
try:
    client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
    print(f"✓ Connected to Cosmos DB: {COSMOS_ENDPOINT}")
except Exception as e:
    print(f"❌ Error connecting to Cosmos DB: {e}")
    client = None

# Container names (equivalent to MySQL tables)
CONTAINERS = {
    'users': 'users',
    'uploaded_papers': 'uploaded_papers',
    'textbooks': 'textbooks',
    'question_bank': 'question_bank',
    'usage_logs': 'usage_logs',
    'ai_search_results': 'ai_search_results'
}

def init_cosmos_db():
    """Initialize Cosmos DB database and containers"""
    if not client:
        print("❌ Cosmos DB client not initialized")
        return False
    
    try:
        # Create database if it doesn't exist
        database = client.create_database_if_not_exists(id=DATABASE_NAME)
        print(f"✓ Database '{DATABASE_NAME}' ready")
        
        # Create containers (tables) with partition keys
        containers_config = [
            {
                'id': 'users',
                'partition_key': PartitionKey(path="/username"),
                'description': 'User accounts and authentication'
            },
            {
                'id': 'uploaded_papers',
                'partition_key': PartitionKey(path="/user_id"),
                'description': 'Question papers uploaded by users'
            },
            {
                'id': 'textbooks',
                'partition_key': PartitionKey(path="/subject"),
                'description': 'Textbooks for different subjects'
            },
            {
                'id': 'question_bank',
                'partition_key': PartitionKey(path="/user_id"),
                'description': 'Saved questions and solutions'
            },
            {
                'id': 'usage_logs',
                'partition_key': PartitionKey(path="/user_id"),
                'description': 'User activity logs'
            },
            {
                'id': 'ai_search_results',
                'partition_key': PartitionKey(path="/paper_id"),
                'description': 'AI-powered search results'
            }
        ]
        
        for config in containers_config:
            container = database.create_container_if_not_exists(
                id=config['id'],
                partition_key=config['partition_key'],
                offer_throughput=400  # Minimum RU/s
            )
            print(f"✓ Container '{config['id']}' ready - {config['description']}")
        
        print("✅ Cosmos DB initialization complete")
        return True
        
    except exceptions.CosmosHttpResponseError as e:
        print(f"❌ Error initializing Cosmos DB: {e.message}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def get_cosmos_container(container_name):
    """Get a Cosmos DB container reference"""
    if not client:
        raise Exception("Cosmos DB client not initialized")
    
    database = client.get_database_client(DATABASE_NAME)
    return database.get_container_client(container_name)

# ============================================================================
# USER OPERATIONS (Migrated from MySQL users table)
# ============================================================================

def create_user(username, password, full_name, email=None, phone=None, is_admin=False):
    """Create a new user in Cosmos DB"""
    try:
        container = get_cosmos_container('users')
        
        # Generate unique ID
        user_id = str(uuid.uuid4())
        
        user_doc = {
            'id': user_id,  # Cosmos DB requires 'id' field
            'username': username,  # Partition key
            'password': password,  # Should be hashed before calling this
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'is_active': True,
            'is_admin': is_admin,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'type': 'user'  # Document type identifier
        }
        
        # Create user document
        created_user = container.create_item(body=user_doc)
        print(f"✅ User created: {username} (ID: {user_id})")
        return created_user
        
    except exceptions.CosmosResourceExistsError:
        print(f"❌ User already exists: {username}")
        return None
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return None

def get_user_by_username(username):
    """Get user by username (for login)"""
    try:
        container = get_cosmos_container('users')
        
        # Query by username (partition key makes this efficient)
        query = "SELECT * FROM c WHERE c.username = @username AND c.type = 'user'"
        parameters = [{"name": "@username", "value": username}]
        
        items = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=False  # Efficient since we're using partition key
        ))
        
        if items:
            user = items[0]
            print(f"✓ User found: {username}")
            return user
        else:
            print(f"❌ User not found: {username}")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching user: {e}")
        return None

def get_user_by_id(user_id):
    """Get user by ID"""
    try:
        container = get_cosmos_container('users')
        
        # Query by ID across all partitions
        query = "SELECT * FROM c WHERE c.id = @user_id AND c.type = 'user'"
        parameters = [{"name": "@user_id", "value": user_id}]
        
        items = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))
        
        if items:
            return items[0]
        return None
            
    except Exception as e:
        print(f"❌ Error fetching user by ID: {e}")
        return None

def update_user(user_id, username, updates):
    """Update user document"""
    try:
        container = get_cosmos_container('users')
        
        # Read existing user
        user = container.read_item(item=user_id, partition_key=username)
        
        # Update fields
        for key, value in updates.items():
            user[key] = value
        
        user['updated_at'] = datetime.utcnow().isoformat()
        
        # Replace document
        updated_user = container.replace_item(item=user_id, body=user)
        print(f"✅ User updated: {username}")
        return updated_user
        
    except Exception as e:
        print(f"❌ Error updating user: {e}")
        return None

def delete_user(user_id, username):
    """Delete user"""
    try:
        container = get_cosmos_container('users')
        container.delete_item(item=user_id, partition_key=username)
        print(f"✅ User deleted: {username}")
        return True
    except Exception as e:
        print(f"❌ Error deleting user: {e}")
        return False

def get_all_users():
    """Get all users (for admin)"""
    try:
        container = get_cosmos_container('users')
        
        query = "SELECT * FROM c WHERE c.type = 'user' ORDER BY c.created_at DESC"
        
        items = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        return items
            
    except Exception as e:
        print(f"❌ Error fetching all users: {e}")
        return []

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def cosmos_to_mysql_format(cosmos_doc):
    """Convert Cosmos DB document to MySQL-like dict for compatibility"""
    if not cosmos_doc:
        return None
    
    # Map Cosmos DB fields to MySQL field names
    mysql_doc = {
        'id': cosmos_doc.get('id'),
        'username': cosmos_doc.get('username'),
        'password': cosmos_doc.get('password'),
        'full_name': cosmos_doc.get('full_name'),
        'email': cosmos_doc.get('email'),
        'phone': cosmos_doc.get('phone'),
        'is_active': cosmos_doc.get('is_active', True),
        'is_admin': cosmos_doc.get('is_admin', False),
        'created_at': cosmos_doc.get('created_at'),
        'updated_at': cosmos_doc.get('updated_at')
    }
    
    return mysql_doc

# ============================================================================
# MIGRATION HELPER
# ============================================================================

def migrate_user_from_mysql(mysql_user):
    """Migrate a single user from MySQL to Cosmos DB"""
    try:
        # Check if user already exists
        existing = get_user_by_username(mysql_user['username'])
        if existing:
            print(f"⚠️ User already exists in Cosmos DB: {mysql_user['username']}")
            return existing
        
        # Create user in Cosmos DB
        return create_user(
            username=mysql_user['username'],
            password=mysql_user['password'],  # Already hashed
            full_name=mysql_user['full_name'],
            email=mysql_user.get('email'),
            phone=mysql_user.get('phone'),
            is_admin=mysql_user.get('is_admin', False)
        )
        
    except Exception as e:
        print(f"❌ Error migrating user: {e}")
        return None

# ============================================================================
# QUESTION BANK OPERATIONS
# ============================================================================

def save_question_to_bank(user_id, question_text, solution, source='unknown', 
                          subject=None, paper_id=None, textbook_id=None, 
                          chapter_name=None, timestamp=None):
    """Save a solved question to Question Bank"""
    try:
        container = get_cosmos_container('question_bank')
        
        question_id = str(uuid.uuid4())
        
        question_doc = {
            'id': question_id,
            'user_id': user_id,  # Partition key
            'question_text': question_text,
            'solution': solution,
            'source': source,
            'subject': subject,
            'paper_id': paper_id,
            'textbook_id': textbook_id,
            'chapter_name': chapter_name,
            'created_at': timestamp or datetime.utcnow().isoformat(),
            'type': 'question'
        }
        
        created = container.create_item(body=question_doc)
        print(f"✅ Question saved to bank: {question_id}")
        return created
        
    except Exception as e:
        print(f"❌ Error saving question: {e}")
        return None

def get_user_questions(user_id):
    """Get all questions for a user"""
    try:
        container = get_cosmos_container('question_bank')
        
        query = """
            SELECT * FROM c 
            WHERE c.user_id = @user_id AND c.type = 'question'
            ORDER BY c.created_at DESC
        """
        parameters = [{"name": "@user_id", "value": user_id}]
        
        items = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=False
        ))
        
        return items
        
    except Exception as e:
        print(f"❌ Error fetching questions: {e}")
        return []

def delete_question(question_id, user_id):
    """Delete a question from Question Bank"""
    try:
        container = get_cosmos_container('question_bank')
        container.delete_item(item=question_id, partition_key=user_id)
        print(f"✅ Question deleted: {question_id}")
        return True
    except Exception as e:
        print(f"❌ Error deleting question: {e}")
        return False

# ============================================================================
# UPLOADED PAPERS OPERATIONS
# ============================================================================

def save_uploaded_paper(user_id, title, subject, board, year, file_path):
    """Save uploaded paper metadata"""
    try:
        container = get_cosmos_container('uploaded_papers')
        
        paper_id = str(uuid.uuid4())
        
        paper_doc = {
            'id': paper_id,
            'user_id': user_id,  # Partition key
            'title': title,
            'subject': subject,
            'board': board,
            'year': year,
            'file_path': file_path,
            'uploaded_at': datetime.utcnow().isoformat(),
            'type': 'paper'
        }
        
        created = container.create_item(body=paper_doc)
        print(f"✅ Paper saved: {title}")
        return created
        
    except Exception as e:
        print(f"❌ Error saving paper: {e}")
        return None

def get_user_papers(user_id):
    """Get all papers for a user"""
    try:
        container = get_cosmos_container('uploaded_papers')
        
        query = """
            SELECT * FROM c 
            WHERE c.user_id = @user_id AND c.type = 'paper'
            ORDER BY c.uploaded_at DESC
        """
        parameters = [{"name": "@user_id", "value": user_id}]
        
        items = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=False
        ))
        
        return items
        
    except Exception as e:
        print(f"❌ Error fetching papers: {e}")
        return []

def get_all_papers():
    """Get ALL papers across all users"""
    try:
        container = get_cosmos_container('uploaded_papers')
        
        query = """
            SELECT * FROM c 
            WHERE c.type = 'paper'
            ORDER BY c.uploaded_at DESC
        """
        
        items = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        return items
        
    except Exception as e:
        print(f"❌ Error fetching all papers: {e}")
        return []

def get_paper_by_id(paper_id):
    """Get paper by ID"""
    try:
        container = get_cosmos_container('uploaded_papers')
        
        query = "SELECT * FROM c WHERE c.id = @paper_id AND c.type = 'paper'"
        parameters = [{"name": "@paper_id", "value": paper_id}]
        
        items = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))
        
        return items[0] if items else None
        
    except Exception as e:
        print(f"❌ Error fetching paper: {e}")
        return None

def delete_paper(paper_id, user_id):
    """Delete a paper"""
    try:
        container = get_cosmos_container('uploaded_papers')
        container.delete_item(item=paper_id, partition_key=user_id)
        print(f"✅ Paper deleted: {paper_id}")
        return True
    except Exception as e:
        print(f"❌ Error deleting paper: {e}")
        return False

# ============================================================================
# TEXTBOOKS OPERATIONS
# ============================================================================

def save_textbook(title, subject, board, file_path, user_id=None):
    """Save textbook metadata"""
    try:
        container = get_cosmos_container('textbooks')
        
        textbook_id = str(uuid.uuid4())
        
        textbook_doc = {
            'id': textbook_id,
            'subject': subject,  # Partition key
            'title': title,
            'board': board,
            'file_path': file_path,
            'user_id': user_id,
            'uploaded_at': datetime.utcnow().isoformat(),
            'type': 'textbook'
        }
        
        created = container.create_item(body=textbook_doc)
        print(f"✅ Textbook saved: {title}")
        return created
        
    except Exception as e:
        print(f"❌ Error saving textbook: {e}")
        return None

def get_textbooks_by_subject(subject):
    """Get textbooks by subject"""
    try:
        container = get_cosmos_container('textbooks')
        
        query = """
            SELECT * FROM c 
            WHERE c.subject = @subject AND c.type = 'textbook'
            ORDER BY c.uploaded_at DESC
        """
        parameters = [{"name": "@subject", "value": subject}]
        
        items = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=False
        ))
        
        return items
        
    except Exception as e:
        print(f"❌ Error fetching textbooks: {e}")
        return []

def get_all_textbooks():
    """Get ALL textbooks across all subjects"""
    try:
        container = get_cosmos_container('textbooks')
        
        query = """
            SELECT * FROM c 
            WHERE c.type = 'textbook'
            ORDER BY c.uploaded_at DESC
        """
        
        items = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        return items
        
    except Exception as e:
        print(f"❌ Error fetching all textbooks: {e}")
        return []

def get_textbook_by_id(textbook_id):
    """Get textbook by ID"""
    try:
        container = get_cosmos_container('textbooks')
        
        query = "SELECT * FROM c WHERE c.id = @textbook_id AND c.type = 'textbook'"
        parameters = [{"name": "@textbook_id", "value": textbook_id}]
        
        items = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))
        
        return items[0] if items else None
        
    except Exception as e:
        print(f"❌ Error fetching textbook: {e}")
        return None

def delete_textbook(textbook_id, subject):
    """Delete a textbook"""
    try:
        container = get_cosmos_container('textbooks')
        container.delete_item(item=textbook_id, partition_key=subject)
        print(f"✅ Textbook deleted: {textbook_id}")
        return True
    except Exception as e:
        print(f"❌ Error deleting textbook: {e}")
        return False

# ============================================================================
# USAGE LOGS OPERATIONS
# ============================================================================

def log_user_activity(user_id, action_type, details=None):
    """Log user activity"""
    try:
        container = get_cosmos_container('usage_logs')
        
        log_id = str(uuid.uuid4())
        
        log_doc = {
            'id': log_id,
            'user_id': user_id,  # Partition key
            'action_type': action_type,
            'details': details,
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'log'
        }
        
        container.create_item(body=log_doc)
        return True
        
    except Exception as e:
        print(f"❌ Error logging activity: {e}")
        return False

def get_user_activity_logs(user_id, limit=100):
    """Get user activity logs"""
    try:
        container = get_cosmos_container('usage_logs')
        
        query = f"""
            SELECT TOP {limit} * FROM c 
            WHERE c.user_id = @user_id AND c.type = 'log'
            ORDER BY c.timestamp DESC
        """
        parameters = [{"name": "@user_id", "value": user_id}]
        
        items = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=False
        ))
        
        return items
        
    except Exception as e:
        print(f"❌ Error fetching logs: {e}")
        return []
