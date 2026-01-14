"""
Verify Supabase connection string and provide troubleshooting steps
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

def analyze_connection_string():
    """Analyze the connection string and provide recommendations"""
    print("=" * 70)
    print("Supabase Connection String Analysis")
    print("=" * 70)
    print()
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("✗ DATABASE_URL not found in .env file")
        return
    
    # Mask password for display
    parsed = urlparse(database_url)
    if '@' in parsed.netloc:
        auth, host = parsed.netloc.rsplit('@', 1)
        if ':' in auth:
            user, _ = auth.split(':', 1)
            display_netloc = f"{user}:***@{host}"
        else:
            display_netloc = f"***@{host}"
    else:
        display_netloc = parsed.netloc
    
    display_url = f"{parsed.scheme}://{display_netloc}{parsed.path}"
    if parsed.query:
        display_url += f"?{parsed.query}"
    
    print(f"Connection String Format: {display_url}")
    print()
    
    # Analyze components
    print("Connection Details:")
    print(f"  Protocol: {parsed.scheme}")
    print(f"  Host: {parsed.hostname}")
    print(f"  Port: {parsed.port or '5432 (default)'}")
    print(f"  Database: {parsed.path.lstrip('/')}")
    print(f"  Has SSL: {'sslmode' in parsed.query}")
    print()
    
    # Check if it's a Supabase URL
    if 'supabase.co' in parsed.hostname:
        print("✓ This appears to be a Supabase connection string")
    else:
        print("⚠ This doesn't look like a Supabase connection string")
        print("  Supabase URLs typically end with .supabase.co")
    
    # Check port
    port = parsed.port or 5432
    if port == 5432:
        print("\n⚠ Using direct connection (port 5432)")
        print("  This requires IP allowlist configuration in Supabase")
    elif port == 6543:
        print("\n✓ Using connection pooling (port 6543)")
        print("  This doesn't require IP allowlist")
    else:
        print(f"\n⚠ Using custom port: {port}")
    
    # Recommendations
    print("\n" + "=" * 70)
    print("TROUBLESHOOTING STEPS")
    print("=" * 70)
    print()
    print("Since your project is active but connection times out:")
    print()
    print("1. CHECK IP ALLOWLIST (Most Common Issue):")
    print("   - Go to Supabase Dashboard → Settings → Database")
    print("   - Scroll to 'Connection Pooling' or 'Network Restrictions'")
    print("   - Check if IP allowlist is enabled")
    print("   - If enabled, add your current IP address")
    print("   - OR disable IP restrictions temporarily to test")
    print()
    print("2. USE CONNECTION POOLING (Recommended Solution):")
    print("   - Go to Supabase Dashboard → Settings → Database")
    print("   - Find 'Connection Pooling' section")
    print("   - Copy the connection string for 'Session mode' or 'Transaction mode'")
    print("   - This uses port 6543 and doesn't require IP allowlist")
    print("   - Update your .env file with this connection string")
    print()
    print("3. VERIFY CONNECTION STRING:")
    print("   - In Supabase Dashboard → Settings → Database")
    print("   - Copy the 'Connection string' (URI format)")
    print("   - Make sure it matches your .env file exactly")
    print("   - Check for any typos or extra characters")
    print()
    print("4. TEST FROM SUPABASE DASHBOARD:")
    print("   - In Supabase Dashboard → SQL Editor")
    print("   - Try running a simple query: SELECT version();")
    print("   - If this works, the issue is with your local connection")
    print()
    print("5. CHECK NETWORK/FIREWALL:")
    print("   - Try from a different network (mobile hotspot)")
    print("   - Check if VPN is interfering")
    print("   - Check corporate firewall settings")
    print()
    
    # Show what the connection pooling URL should look like
    if port == 5432:
        print("=" * 70)
        print("QUICK FIX: Update to Connection Pooling")
        print("=" * 70)
        print()
        print("Change your DATABASE_URL from:")
        print(f"  postgresql://...@{parsed.hostname}:5432/...")
        print()
        print("To (port 6543):")
        print(f"  postgresql://...@{parsed.hostname}:6543/...")
        print()
        print("You can get the exact connection string from:")
        print("  Supabase Dashboard → Settings → Database → Connection Pooling")

if __name__ == '__main__':
    analyze_connection_string()
