"""
Test Supabase connection with IPv6/IPv4 handling
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from urllib.parse import urlparse, urlunparse
import socket

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

def get_ipv4_address(hostname):
    """Try to get IPv4 address for hostname"""
    try:
        # Try to get IPv4 address
        addr_info = socket.getaddrinfo(hostname, None, socket.AF_INET)
        if addr_info:
            return addr_info[0][4][0]
    except:
        pass
    return None

def test_connection_with_ip():
    """Test connection using IP address directly"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("✗ DATABASE_URL not found")
        return False
    
    parsed = urlparse(database_url)
    hostname = parsed.hostname
    
    print(f"Testing connection to: {hostname}")
    
    # Try to get IPv4 address
    ipv4 = get_ipv4_address(hostname)
    if ipv4:
        print(f"Found IPv4 address: {ipv4}")
        # Replace hostname with IP in connection string
        new_netloc = parsed.netloc.replace(hostname, ipv4)
        new_url = urlunparse((
            parsed.scheme,
            new_netloc,
            parsed.path,
            parsed.params,
            'sslmode=require',
            parsed.fragment
        ))
        
        try:
            print(f"Attempting connection with IPv4...")
            conn = psycopg2.connect(new_url, connect_timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            print(f"✓ Connection successful with IPv4!")
            print(f"  Version: {version[:60]}...")
            return True
        except Exception as e:
            print(f"✗ IPv4 connection failed: {e}")
    else:
        print("No IPv4 address found")
    
    # Try with original hostname but force IPv6
    print(f"\nTrying with hostname (IPv6)...")
    try:
        # Add SSL mode
        query = 'sslmode=require'
        if parsed.query:
            query = f"{parsed.query}&{query}"
        
        test_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            query,
            parsed.fragment
        ))
        
        conn = psycopg2.connect(test_url, connect_timeout=15)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"✓ Connection successful with hostname!")
        print(f"  Version: {version[:60]}...")
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print(f"\nError details: {type(e).__name__}")
        if hasattr(e, 'pgcode'):
            print(f"PostgreSQL error code: {e.pgcode}")
        return False

def test_connection_pooler():
    """Test connection pooling mode"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        return False
    
    parsed = urlparse(database_url)
    
    # Change to port 6543
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
    
    query = 'sslmode=require'
    if parsed.query:
        query = f"{parsed.query}&{query}"
    
    pooler_url = urlunparse((
        parsed.scheme,
        new_netloc,
        parsed.path,
        parsed.params,
        query,
        parsed.fragment
    ))
    
    print(f"\nTesting connection pooling (port 6543)...")
    try:
        conn = psycopg2.connect(pooler_url, connect_timeout=15)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"✓ Connection pooling successful!")
        print(f"  Version: {version[:60]}...")
        return True
    except Exception as e:
        print(f"✗ Connection pooling failed: {e}")
        return False

def main():
    print("=" * 70)
    print("Supabase Connection Test with IP Handling")
    print("=" * 70)
    print()
    
    # Test 1: Direct connection
    success1 = test_connection_with_ip()
    
    # Test 2: Connection pooling
    success2 = test_connection_pooler()
    
    print("\n" + "=" * 70)
    if success1 or success2:
        print("✓ Connection successful!")
        if success2:
            print("\nRecommendation: Use connection pooling (port 6543)")
            print("Update your DATABASE_URL to use port 6543")
    else:
        print("✗ All connection attempts failed")
        print("\nPossible issues:")
        print("1. Network firewall blocking connections")
        print("2. Supabase project settings (IP allowlist)")
        print("3. VPN or proxy interfering")
        print("4. Check Supabase dashboard for connection string")
    print("=" * 70)
    
    return 0 if (success1 or success2) else 1

if __name__ == '__main__':
    sys.exit(main())
