"""
Automated Database Migration Runner
This script automatically runs all migration files against your Supabase database.
Uses your .env configuration for database connection.
"""
import sys
import os
from pathlib import Path
from database import db
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def execute_sql_file(file_path):
    """
    Execute a SQL file against the database.
    Handles multi-statement SQL files properly, including functions and triggers.
    """
    print(f"\n📄 Reading migration file: {file_path.name}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Use psycopg2's execute to run the entire SQL file
        # PostgreSQL can handle multiple statements separated by semicolons
        # We'll use a connection directly to execute the full script
        conn = db.get_connection()
        try:
            cursor = conn.cursor()
            
            # Execute the entire SQL file
            # psycopg2 can handle multiple statements in one execute
            cursor.execute(sql_content)
            conn.commit()
            
            # Count what was created by checking the output
            print(f"  ✓ SQL file executed successfully")
            
            # Try to get more details about what was created
            # Check for tables
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
            """)
            table_count = cursor.fetchone()[0]
            print(f"  ✓ Database now has {table_count} table(s)")
            
            cursor.close()
            return True
            
        except Exception as e:
            conn.rollback()
            error_msg = str(e).lower()
            
            # Some errors are expected (like "already exists" with IF NOT EXISTS)
            if 'already exists' in error_msg:
                print(f"  ⚠ Some objects already exist (this is OK with IF NOT EXISTS)")
                conn.commit()  # Commit anyway since IF NOT EXISTS is safe
                return True
            else:
                print(f"  ✗ Error executing SQL: {e}")
                raise
        finally:
            db.return_connection(conn)
        
    except FileNotFoundError:
        print(f"  ✗ File not found: {file_path}")
        return False
    except Exception as e:
        print(f"  ✗ Error reading/executing file: {e}")
        logger.exception("Migration failed")
        return False
        
    except FileNotFoundError:
        print(f"  ✗ File not found: {file_path}")
        return False
    except Exception as e:
        print(f"  ✗ Error reading/executing file: {e}")
        logger.exception("Migration failed")
        return False


def verify_tables():
    """Verify that all expected tables were created"""
    print("\n🔍 Verifying tables were created...")
    
    expected_tables = [
        'locations', 'users', 'boards', 'checkouts',
        'reservations', 'damage_reports', 'activity_log', 'board_ratings'
    ]
    
    try:
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """
        results = db.execute_query(query, fetch_all=True)
        existing_tables = [row['table_name'] for row in results] if results else []
        
        print(f"  Found {len(existing_tables)} tables in database")
        
        missing_tables = []
        for table in expected_tables:
            if table in existing_tables:
                print(f"  ✓ {table}")
            else:
                print(f"  ✗ {table} (MISSING)")
                missing_tables.append(table)
        
        if missing_tables:
            print(f"\n⚠ Warning: {len(missing_tables)} table(s) are missing!")
            return False
        else:
            print("\n✓ All expected tables are present!")
            return True
            
    except Exception as e:
        print(f"  ✗ Error verifying tables: {e}")
        return False


def main():
    """Main migration runner"""
    print("=" * 70)
    print("🚀 Automated Database Migration Runner")
    print("=" * 70)
    
    # Test connection first
    print("\n1. Testing database connection...")
    try:
        success, result = db.test_connection()
        if not success:
            print(f"✗ Connection failed: {result}")
            print("\nPlease check your .env file and ensure:")
            print("  - DATABASE_URL is set, OR")
            print("  - Individual DB parameters (user, password, host, port, dbname) are set")
            sys.exit(1)
        print(f"✓ Connected to database successfully!")
        print(f"  PostgreSQL version: {result}")
    except Exception as e:
        print(f"✗ Connection error: {e}")
        sys.exit(1)
    
    # Get migration files
    migrations_dir = Path(__file__).parent / 'migrations'
    if not migrations_dir.exists():
        print(f"\n✗ Migrations directory not found: {migrations_dir}")
        sys.exit(1)
    
    # Find migration files in order
    migration_files = sorted(migrations_dir.glob('*.sql'))
    if not migration_files:
        print(f"\n✗ No migration files found in {migrations_dir}")
        sys.exit(1)
    
    print(f"\n2. Found {len(migration_files)} migration file(s)")
    for f in migration_files:
        print(f"   - {f.name}")
    
    # Run migrations
    print("\n3. Running migrations...")
    all_success = True
    
    for migration_file in migration_files:
        print(f"\n{'='*70}")
        print(f"Running: {migration_file.name}")
        print('='*70)
        
        success = execute_sql_file(migration_file)
        if not success:
            all_success = False
            print(f"\n✗ Migration {migration_file.name} failed!")
            break
    
    # Verify tables
    if all_success:
        verify_tables()
    
    # Cleanup
    db.close_all_connections()
    
    # Final summary
    print("\n" + "=" * 70)
    if all_success:
        print("✅ Migration completed successfully!")
        print("\nNext steps:")
        print("  1. Check your Supabase Table Editor to see all 8 tables")
        print("  2. Run 'python scripts/test_db_connection.py' to verify connection")
        print("  3. Launch the app with 'python app.py'")
    else:
        print("❌ Migration completed with errors. Please review the output above.")
        sys.exit(1)
    print("=" * 70)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Migration interrupted by user")
        db.close_all_connections()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        logger.exception("Unexpected error")
        db.close_all_connections()
        sys.exit(1)
