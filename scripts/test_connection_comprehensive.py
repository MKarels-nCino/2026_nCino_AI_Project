"""
Comprehensive database connection test script
This script tests the Supabase connection and provides detailed diagnostics.
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Add parent directory to path to import project modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from database import db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_env_file():
    """Check if .env file exists and what variables are set"""
    print("=" * 70)
    print("Step 1: Checking Environment Configuration")
    print("=" * 70)
    
    env_path = Path(__file__).parent.parent / '.env'
    
    if not env_path.exists():
        print(f"✗ .env file not found at: {env_path}")
        print("  Please create a .env file with your database credentials.")
        return False
    
    print(f"✓ .env file found at: {env_path}")
    
    # Load environment variables
    load_dotenv(env_path)
    
    # Check for DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Mask password in URL for display
        if '@' in database_url and '://' in database_url:
            parts = database_url.split('@')
            if len(parts) == 2:
                protocol_part = parts[0]
                if ':' in protocol_part:
                    protocol, credentials = protocol_part.split('://', 1)
                    if ':' in credentials:
                        user, password = credentials.split(':', 1)
                        masked_url = f"{protocol}://{user}:***@{parts[1]}"
                    else:
                        masked_url = database_url
                else:
                    masked_url = database_url
            else:
                masked_url = database_url
        else:
            masked_url = database_url
        print(f"✓ DATABASE_URL is set: {masked_url}")
    else:
        print("  DATABASE_URL not set, checking individual parameters...")
        
        # Check individual parameters
        user = os.getenv('user') or os.getenv('DB_USER')
        password = os.getenv('password') or os.getenv('DB_PASSWORD')
        host = os.getenv('host') or os.getenv('DB_HOST')
        port = os.getenv('port') or os.getenv('DB_PORT', '5432')
        dbname = os.getenv('dbname') or os.getenv('DB_NAME')
        
        params = {
            'user': user,
            'password': '***' if password else None,
            'host': host,
            'port': port,
            'dbname': dbname
        }
        
        all_set = all([user, password, host, dbname])
        
        for key, value in params.items():
            if value:
                print(f"  ✓ {key}: {value}")
            else:
                print(f"  ✗ {key}: NOT SET")
        
        if not all_set:
            print("\n✗ Not all required database parameters are set!")
            return False
    
    print("\n✓ Environment configuration looks good!")
    return True

def test_config():
    """Test the Config class"""
    print("\n" + "=" * 70)
    print("Step 2: Testing Config Class")
    print("=" * 70)
    
    try:
        config = Config()
        
        # Check DATABASE_URL
        db_url = config.get_database_url()
        if db_url:
            # Mask password
            if '@' in db_url and '://' in db_url:
                parts = db_url.split('@')
                if len(parts) == 2:
                    protocol_part = parts[0]
                    if '://' in protocol_part:
                        protocol, credentials = protocol_part.split('://', 1)
                        if ':' in credentials:
                            user, password = credentials.split(':', 1)
                            masked_url = f"{protocol}://{user}:***@{parts[1]}"
                        else:
                            masked_url = db_url
                    else:
                        masked_url = db_url
                else:
                    masked_url = db_url
            else:
                masked_url = db_url
            print(f"✓ Config.get_database_url() returned: {masked_url}")
        else:
            print("✗ Config.get_database_url() returned None")
            db_params = config.get_db_params()
            print(f"  Individual parameters: {', '.join([f'{k}={"***" if k == "password" else v}' for k, v in db_params.items() if v])}")
            if not all(db_params.values()):
                print("✗ Not all database parameters are configured")
                return False
        
        print("✓ Config class is working correctly!")
        return True
        
    except Exception as e:
        print(f"✗ Error testing Config: {e}")
        logger.exception("Config test failed")
        return False

def test_database_connection():
    """Test the database connection"""
    print("\n" + "=" * 70)
    print("Step 3: Testing Database Connection")
    print("=" * 70)
    
    try:
        print("\n3.1 Testing basic connection...")
        success, result = db.test_connection()
        
        if success:
            print(f"✓ Connection successful!")
            print(f"  PostgreSQL version: {result}")
        else:
            print(f"✗ Connection failed!")
            print(f"  Error: {result}")
            return False
        
        print("\n3.2 Testing query execution...")
        try:
            query_result = db.execute_query(
                "SELECT current_database(), current_user, version();", 
                fetch_one=True
            )
            if query_result:
                print("✓ Query execution successful!")
                print(f"  Database: {query_result['current_database']}")
                print(f"  User: {query_result['current_user']}")
                version = query_result['version']
                print(f"  Version: {version[:60]}...")
            else:
                print("✗ Query returned no results")
                return False
        except Exception as e:
            print(f"✗ Query execution failed: {e}")
            logger.exception("Query execution failed")
            return False
        
        print("\n3.3 Testing connection pool...")
        try:
            conn1 = db.get_connection()
            conn2 = db.get_connection()
            if conn1 and conn2:
                print("✓ Connection pool working correctly!")
                print(f"  Got 2 connections from pool")
                db.return_connection(conn1)
                db.return_connection(conn2)
            else:
                print("✗ Failed to get connections from pool")
                return False
        except Exception as e:
            print(f"✗ Connection pool test failed: {e}")
            logger.exception("Connection pool test failed")
            return False
        
        print("\n3.4 Testing table access...")
        try:
            # Try to query information_schema to see if we can access tables
            tables_query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                LIMIT 5;
            """
            tables = db.execute_query(tables_query, fetch_all=True)
            if tables:
                print("✓ Can access database tables!")
                print(f"  Found {len(tables)} table(s) (showing first 5):")
                for table in tables:
                    print(f"    - {table['table_name']}")
            else:
                print("  No tables found in public schema (database might be empty)")
        except Exception as e:
            print(f"✗ Table access test failed: {e}")
            logger.exception("Table access test failed")
            return False
        
        print("\n✓ All database connection tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Database test failed with exception: {e}")
        logger.exception("Database test failed")
        return False
    finally:
        try:
            db.close_all_connections()
        except:
            pass

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("Supabase Database Connection Test")
    print("=" * 70)
    print()
    
    results = []
    
    # Step 1: Check environment file
    results.append(("Environment Configuration", check_env_file()))
    
    if not results[-1][1]:
        print("\n" + "=" * 70)
        print("✗ Tests stopped due to configuration issues.")
        print("=" * 70)
        sys.exit(1)
    
    # Step 2: Test Config
    results.append(("Config Class", test_config()))
    
    if not results[-1][1]:
        print("\n" + "=" * 70)
        print("✗ Tests stopped due to Config issues.")
        print("=" * 70)
        sys.exit(1)
    
    # Step 3: Test Database Connection
    results.append(("Database Connection", test_database_connection()))
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("✓ All tests passed! Database is ready for use.")
        print("=" * 70)
        sys.exit(0)
    else:
        print("✗ Some tests failed. Please check the errors above.")
        print("=" * 70)
        sys.exit(1)

if __name__ == '__main__':
    main()
