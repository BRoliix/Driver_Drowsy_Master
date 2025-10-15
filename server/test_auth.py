from pocketbase import PocketBase
import os
from dotenv import load_dotenv

load_dotenv()

def test_pocketbase_auth():
    """
    Test different authentication methods for PocketBase
    """
    pb = PocketBase(os.getenv('POCKETBASE_URL'))
    print(f"Connecting to: {os.getenv('POCKETBASE_URL')}")
    
    # Method 1: Try admin authentication
    print("\n1. Testing admin authentication...")
    try:
        # Try common admin credentials (you'll need to provide the actual ones)
        admin_email = input("Enter admin email (or press Enter to skip): ").strip()
        if admin_email:
            admin_password = input("Enter admin password: ").strip()
            if admin_password:
                admin_data = pb.admins.auth_with_password(admin_email, admin_password)
                print("✅ Admin authentication successful!")
                print(f"Admin token: {pb.auth_store.token[:20]}...")
                return pb
    except Exception as e:
        print(f"❌ Admin auth failed: {e}")
    
    # Method 2: Try creating collections without auth (public access)
    print("\n2. Testing public collection access...")
    try:
        # Try to create a simple test record
        test_data = {
            'test': 'value',
            'timestamp': '2024-10-15T20:00:00Z'
        }
        result = pb.collection('test_public').create(test_data)
        print("✅ Public collection access works!")
        print(f"Created record: {result.id}")
        return pb
    except Exception as e:
        print(f"❌ Public access failed: {e}")
    
    # Method 3: Check if we need to create an app user first
    print("\n3. Testing app user authentication...")
    try:
        # This would require creating a user first through the admin interface
        print("ℹ️  App user auth requires existing user records")
    except Exception as e:
        print(f"❌ App user auth failed: {e}")
    
    return None

if __name__ == "__main__":
    authenticated_pb = test_pocketbase_auth()
    if authenticated_pb:
        print("\n🎉 Authentication successful! PocketBase is ready for use.")
    else:
        print("\n⚠️  Authentication required. Please check PocketBase admin settings.")