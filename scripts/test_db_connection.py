"""
Test script to verify Supabase PostgreSQL database connection
Run this script to ensure your database connection is working correctly.
"""
import sys
from database import db
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_connection():
    """Test the database connection"""
    print("=" * 60)
    print("Testing Supabase PostgreSQL Database Connection")
    print("=" * 60)
    
    try:
        print("\n1. Testing basic connection...")
        success, result = db.test_connection()
        
        if success:
            print(f"✓ Connection successful!")
            print(f"  PostgreSQL version: {result}")
        else:
            print(f"✗ Connection failed!")
            print(f"  Error: {result}")
            return False
        
        print("\n2. Testing query execution...")
        try:
            query_result = db.execute_query("SELECT current_database(), current_user, version();", fetch_one=True)
            if query_result:
                print("✓ Query execution successful!")
                print(f"  Database: {query_result['current_database']}")
                print(f"  User: {query_result['current_user']}")
                print(f"  Version: {query_result['version'][:50]}...")
            else:
                print("✗ Query returned no results")
                return False
        except Exception as e:
            print(f"✗ Query execution failed: {e}")
            return False
        
        print("\n3. Testing connection pool...")
        try:
            conn1 = db.get_connection()
            conn2 = db.get_connection()
            if conn1 and conn2:
                print("✓ Connection pool working correctly!")
                db.return_connection(conn1)
                db.return_connection(conn2)
            else:
                print("✗ Failed to get connections from pool")
                return False
        except Exception as e:
            print(f"✗ Connection pool test failed: {e}")
            return False
        
        print("\n" + "=" * 60)
        print("✓ All tests passed! Database is ready for use.")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with exception: {e}")
        logger.exception("Test failed")
        return False
    finally:
        db.close_all_connections()

if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)
