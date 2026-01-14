"""
Direct Supabase connection test
Tests both direct connection and connection pooling modes
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from urllib.parse import urlparse, urlunparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

def test_direct_connection():
    """Test direct connection (port 5432)"""
    print("=" * 70)
    print("Test 1: Direct Connection (Port 5432)")
    print("=" * 70)
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("✗ DATABASE_URL not found in environment")
        return False
    
    # Parse and modify URL
    parsed = urlparse(database_url)
    
    # Add SSL mode
    query_params = 'sslmode=require'
    if parsed.query:
        query_params = f"{parsed.query}&{query_params}"
    
    modified_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        query_params,
        parsed.fragment
    ))
    
    # Mask password for display
    display_url = modified_url.split('@')[0] + '@***' + '@'.join(modified_url.split('@')[1:])
    print(f"Attempting connection to: {display_url}")
    
    try:
        conn = psycopg2.connect(modified_url, connect_timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"✓ Direct connection successful!")
        print(f"  PostgreSQL version: {version[:60]}...")
        return True
    except psycopg2.OperationalError as e:
        print(f"✗ Direct connection failed: {e}")
        if "timeout" in str(e).lower() or "timed out" in str(e).lower():
            print("  → This usually means:")
            print("    1. IP address is not in Supabase allowlist")
            print("    2. Supabase project is paused")
            print("    3. Network/firewall blocking the connection")
        return False
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return False

def test_pooler_connection():
    """Test connection pooling mode (port 6543)"""
    print("\n" + "=" * 70)
    print("Test 2: Connection Pooling Mode (Port 6543)")
    print("=" * 70)
    print("Note: This mode doesn't require IP allowlist")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("✗ DATABASE_URL not found in environment")
        return False
    
    # Parse and modify URL to use port 6543
    parsed = urlparse(database_url)
    
    # Change port to 6543 (Supabase connection pooler)
    # netloc format: user:password@host:port
    if '@' in parsed.netloc:
        auth_part, host_part = parsed.netloc.rsplit('@', 1)
        if ':' in host_part:
            host, _ = host_part.rsplit(':', 1)
            new_netloc = f"{auth_part}@{host}:6543"
        else:
            new_netloc = f"{auth_part}@{host_part}:6543"
    else:
        if ':' in parsed.netloc:
            host, _ = parsed.netloc.rsplit(':', 1)
            new_netloc = f"{host}:6543"
        else:
            new_netloc = f"{parsed.netloc}:6543"
    
    # Add SSL mode (pgbouncer doesn't need special parameter)
    query_params = 'sslmode=require'
    if parsed.query:
        query_params = f"{parsed.query}&{query_params}"
    
    pooler_url = urlunparse((
        parsed.scheme,
        new_netloc,
        parsed.path,
        parsed.params,
        query_params,
        parsed.fragment
    ))
    
    # Mask password for display
    display_url = pooler_url.split('@')[0] + '@***' + '@'.join(pooler_url.split('@')[1:])
    print(f"Attempting connection to: {display_url}")
    
    try:
        conn = psycopg2.connect(pooler_url, connect_timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"✓ Connection pooling mode successful!")
        print(f"  PostgreSQL version: {version[:60]}...")
        return True
    except psycopg2.OperationalError as e:
        print(f"✗ Connection pooling failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return False

def main():
    print("\n" + "=" * 70)
    print("Supabase Connection Diagnostic Test")
    print("=" * 70)
    print()
    
    direct_success = test_direct_connection()
    pooler_success = test_pooler_connection()
    
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    
    if pooler_success:
        print("✓ Connection pooling mode works!")
        print("\nRecommendation: Update your DATABASE_URL to use port 6543")
        print("Example: Change port from 5432 to 6543 in your connection string")
        print("And add ?pgbouncer=true to the query string")
    elif direct_success:
        print("✓ Direct connection works!")
        print("Your current setup should work fine.")
    else:
        print("✗ Both connection methods failed")
        print("\nPossible issues:")
        print("1. Check if your Supabase project is active (not paused)")
        print("2. Verify your DATABASE_URL is correct")
        print("3. Check Supabase dashboard for IP allowlist settings")
        print("4. Verify network connectivity")
    
    print("=" * 70)
    
    return 0 if (direct_success or pooler_success) else 1

if __name__ == '__main__':
    sys.exit(main())
