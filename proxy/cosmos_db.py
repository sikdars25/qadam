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
DATABASE_NAME = os.getenv('COSMOS_DATABASE', 'qadam')  # Changed default to match Azure

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
    'ai_search_results': 'ai_search_results',
    'parsed_questions': 'parsed_questions'
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
            },
            {
                'id': 'parsed_questions',
                'partition_key': PartitionKey(path="/paper_id"),
                'description': 'Parsed questions from uploaded papers'
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
        
        print(f"🔍 Querying users container for username={username}")
        
        # Query by username with cross-partition query
        # Note: Container has partition key /user_id, not /username
        # So we need to use cross-partition query to find by username
        query = "SELECT * FROM c WHERE c.username = @username"
        parameters = [{"name": "@username", "value": username}]
        
        print(f"   Query: {query}")
        print(f"   Using cross-partition query (partition key is /user_id)")
        
        items = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True  # Required since we're not filtering by partition key
        ))
        
        print(f"   Items returned: {len(items)}")
        
        if items:
            user = items[0]
            print(f"✓ User found: {username}")
            print(f"   User ID: {user.get('id')}")
            print(f"   Has password: {bool(user.get('password'))}")
            return user
        else:
            print(f"❌ User not found: {username}")
            print(f"   Query returned 0 items")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching user: {e}")
        print(f"   Exception type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
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
    """Delete a paper - tries multiple approaches to handle partition key issues"""
    try:
        container = get_cosmos_container('uploaded_papers')
        print(f"🔍 Attempting to delete paper_id={paper_id} with partition_key={user_id}")
        
        # First, try to find the document to get the exact partition key value
        query = "SELECT * FROM c WHERE c.id = @paper_id"
        parameters = [{"name": "@paper_id", "value": paper_id}]
        items = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))
        
        if not items:
            print(f"❌ Paper not found in Cosmos DB: {paper_id}")
            return False
        
        paper_doc = items[0]
        actual_user_id = paper_doc.get('user_id')
        doc_id = paper_doc.get('id')
        doc_rid = paper_doc.get('_rid')
        
        print(f"📋 Found paper: {paper_doc.get('title')}")
        print(f"📋 Document ID: {doc_id}")
        print(f"📋 Document _rid: {doc_rid}")
        print(f"📋 Actual user_id in document: {actual_user_id} (type: {type(actual_user_id).__name__})")
        print(f"📋 Provided user_id: {user_id} (type: {type(user_id).__name__})")
        
        deleted = False
        
        # Method 1: Try using upsert to "delete" by replacing with a tombstone, then delete
        try:
            print(f"🔑 Method 1: Trying direct delete with id and partition key")
            container.delete_item(item=doc_id, partition_key=actual_user_id)
            print(f"✅ Successfully deleted paper")
            deleted = True
        except exceptions.CosmosResourceNotFoundError as e:
            print(f"   ❌ Method 1 failed: NotFound - {str(e)[:200]}")
        except Exception as e:
            print(f"   ❌ Method 1 failed: {type(e).__name__} - {str(e)[:200]}")
        
        # Method 2: Try with document's _self link
        if not deleted and '_self' in paper_doc:
            try:
                print(f"🔑 Method 2: Trying with _self link")
                # Use read to get the latest etag, then delete
                read_doc = container.read_item(item=doc_id, partition_key=actual_user_id)
                container.delete_item(item=read_doc['id'], partition_key=read_doc['user_id'])
                print(f"✅ Successfully deleted paper using fresh read")
                deleted = True
            except Exception as e:
                print(f"   ❌ Method 2 failed: {type(e).__name__} - {str(e)[:200]}")
        
        # Method 3: Try replacing the document to mark as deleted, then actually delete
        if not deleted:
            try:
                print(f"🔑 Method 3: Trying replace then delete")
                paper_doc['_deleted'] = True
                paper_doc['deleted_at'] = datetime.utcnow().isoformat()
                container.upsert_item(body=paper_doc)
                print(f"   ✓ Marked as deleted, now removing...")
                container.delete_item(item=doc_id, partition_key=actual_user_id)
                print(f"✅ Successfully deleted after marking")
                deleted = True
            except Exception as e:
                print(f"   ❌ Method 3 failed: {type(e).__name__} - {str(e)[:200]}")
        
        if not deleted:
            print(f"❌ Failed to delete paper after trying all partition key formats")
            return False
        
        # Also delete associated parsed questions
        try:
            parsed_container = get_cosmos_container('parsed_questions')
            query = "SELECT * FROM c WHERE c.paper_id = @paper_id"
            parameters = [{"name": "@paper_id", "value": paper_id}]
            items = list(parsed_container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            for item in items:
                parsed_container.delete_item(item=item['id'], partition_key=item['paper_id'])
                print(f"✅ Deleted parsed question: {item['id']}")
        except Exception as pq_error:
            print(f"⚠️ Error deleting parsed questions: {pq_error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error deleting paper from Cosmos DB: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
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
        print(f"🔍 Attempting delete: id={textbook_id}, partition_key={subject}")
        
        # First, query to find the item and get the actual partition key
        # This is more reliable than assuming the partition key is correct
        query = "SELECT * FROM c WHERE c.id = @id AND c.type = 'textbook'"
        items = list(container.query_items(
            query=query,
            parameters=[{"name": "@id", "value": textbook_id}],
            enable_cross_partition_query=True
        ))
        
        if not items:
            print(f"❌ Textbook not found in database: {textbook_id}")
            return False
        
        # Get the actual partition key from the document
        actual_item = items[0]
        actual_subject = actual_item.get('subject')
        actual_title = actual_item.get('title', 'Unknown')
        
        print(f"✓ Found textbook: '{actual_title}' with partition_key={actual_subject}")
        
        # Use the actual partition key for deletion
        if actual_subject != subject:
            print(f"⚠️ Partition key mismatch! Expected: {subject}, Actual: {actual_subject}")
            print(f"   Using actual partition key: {actual_subject}")
        
        # Delete with the correct partition key
        container.delete_item(item=textbook_id, partition_key=actual_subject)
        print(f"✅ Textbook deleted successfully: {textbook_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error deleting textbook: {e}")
        import traceback
        traceback.print_exc()
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

# ============================================================================
# PARSED QUESTIONS OPERATIONS
# ============================================================================

def save_parsed_question(paper_id, question_number, question_text, question_type='unknown',
                         sub_parts=None, has_diagram=False, marks=None, embedding_id=None, 
                         parsed_data=None):
    """Save a parsed question from a paper"""
    try:
        container = get_cosmos_container('parsed_questions')
        
        question_id = str(uuid.uuid4())
        
        question_doc = {
            'id': question_id,
            'paper_id': paper_id,  # Partition key
            'question_number': str(question_number),
            'question_text': question_text,
            'question_type': question_type,
            'sub_parts': sub_parts or [],
            'has_diagram': has_diagram,
            'marks': marks,
            'embedding_id': embedding_id,
            'parsed_data': parsed_data,
            'created_at': datetime.utcnow().isoformat(),
            'type': 'parsed_question'
        }
        
        created = container.create_item(body=question_doc)
        return created
        
    except Exception as e:
        print(f"❌ Error saving parsed question: {e}")
        return None

def get_parsed_questions_by_paper(paper_id):
    """Get all parsed questions for a paper"""
    try:
        container = get_cosmos_container('parsed_questions')
        
        query = """
            SELECT * FROM c 
            WHERE c.paper_id = @paper_id AND c.type = 'parsed_question'
            ORDER BY c.question_number
        """
        parameters = [{"name": "@paper_id", "value": paper_id}]
        
        items = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=False
        ))
        
        # Convert parsed_data objects to JSON strings for frontend compatibility
        import json
        for item in items:
            if item.get('parsed_data') and isinstance(item['parsed_data'], dict):
                item['parsed_data'] = json.dumps(item['parsed_data'])
            if item.get('sub_parts') and isinstance(item['sub_parts'], list):
                item['sub_parts'] = json.dumps(item['sub_parts'])
        
        print(f"✓ Found {len(items)} parsed questions in Cosmos DB for paper {paper_id}")
        return items
        
    except exceptions.CosmosResourceNotFoundError:
        print(f"⚠️ Parsed questions container not found - please restart the server to initialize")
        return []
    except Exception as e:
        print(f"❌ Error fetching parsed questions: {e}")
        return []

def delete_parsed_questions_by_paper(paper_id):
    """Delete all parsed questions for a paper"""
    try:
        container = get_cosmos_container('parsed_questions')
        
        # First, get all questions for this paper
        questions = get_parsed_questions_by_paper(paper_id)
        
        # Delete each question
        deleted_count = 0
        for question in questions:
            try:
                container.delete_item(item=question['id'], partition_key=paper_id)
                deleted_count += 1
            except Exception as e:
                print(f"⚠️ Error deleting question {question['id']}: {e}")
        
        print(f"✅ Deleted {deleted_count} parsed questions for paper {paper_id}")
        return deleted_count
        
    except Exception as e:
        print(f"❌ Error deleting parsed questions: {e}")
        return 0

def get_all_parsed_questions():
    """Get all parsed questions across all papers"""
    try:
        container = get_cosmos_container('parsed_questions')
        
        query = """
            SELECT * FROM c 
            WHERE c.type = 'parsed_question'
            ORDER BY c.created_at DESC
        """
        
        items = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        # Convert parsed_data objects to JSON strings for frontend compatibility
        import json
        for item in items:
            if item.get('parsed_data') and isinstance(item['parsed_data'], dict):
                item['parsed_data'] = json.dumps(item['parsed_data'])
            if item.get('sub_parts') and isinstance(item['sub_parts'], list):
                item['sub_parts'] = json.dumps(item['sub_parts'])
        
        print(f"✓ Found {len(items)} total parsed questions in Cosmos DB")
        return items
        
    except exceptions.CosmosResourceNotFoundError:
        print(f"⚠️ Parsed questions container not found - please restart the server to initialize")
        return []
    except Exception as e:
        print(f"❌ Error fetching all parsed questions: {e}")
        return []

# ============================================================================
# AI SEARCH RESULTS OPERATIONS
# ============================================================================

def save_ai_search_results(paper_id, textbook_id, search_results, total_chapters=0, 
                           total_questions=0, unmatched_count=0):
    """Save AI search results for a paper-textbook combination"""
    try:
        container = get_cosmos_container('ai_search_results')
        
        result_id = str(uuid.uuid4())
        
        result_doc = {
            'id': result_id,
            'paper_id': paper_id,  # Partition key
            'textbook_id': textbook_id,
            'search_results': search_results,  # Store as object, not JSON string
            'total_chapters': total_chapters,
            'total_questions': total_questions,
            'unmatched_count': unmatched_count,
            'created_at': datetime.utcnow().isoformat(),
            'type': 'ai_search_result'
        }
        
        created = container.create_item(body=result_doc)
        print(f"✓ Saved AI search results for paper {paper_id} + textbook {textbook_id}")
        return created
        
    except Exception as e:
        print(f"❌ Error saving AI search results: {e}")
        return None

def get_last_ai_search_result(paper_id, textbook_id):
    """Get the most recent AI search result for a paper-textbook combination"""
    try:
        container = get_cosmos_container('ai_search_results')
        
        query = """
            SELECT TOP 1 * FROM c 
            WHERE c.paper_id = @paper_id 
            AND c.textbook_id = @textbook_id 
            AND c.type = 'ai_search_result'
            ORDER BY c.created_at DESC
        """
        parameters = [
            {"name": "@paper_id", "value": paper_id},
            {"name": "@textbook_id", "value": textbook_id}
        ]
        
        items = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=False
        ))
        
        if items:
            print(f"✓ Found AI search result for paper {paper_id} + textbook {textbook_id}")
            return items[0]
        else:
            print(f"⚠️ No AI search results found for paper {paper_id} + textbook {textbook_id}")
            return None
        
    except exceptions.CosmosResourceNotFoundError:
        print(f"⚠️ AI search results container not found")
        return None
    except Exception as e:
        print(f"❌ Error fetching AI search result: {e}")
        return None
