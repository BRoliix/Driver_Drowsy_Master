from dao import connect
import os

def check_pocketbase_status():
    """
    Check PocketBase connection and see what we can access
    """
    pb = connect()
    print(f"Connected to PocketBase at: {os.getenv('POCKETBASE_URL')}")
    
    # Try to get admin info (this will tell us about authentication)
    try:
        # Try a simple health check first
        print("Testing basic connectivity...")
        
        # Let's try to authenticate as admin first
        print("Attempting admin authentication (if credentials are available)...")
        
        # For now, let's try creating collections with minimal data
        collections_to_test = ['sos_alerts', 'driver_sessions', 'vehicle_info', 'user_data']
        
        for collection_name in collections_to_test:
            try:
                print(f"\nTesting collection: {collection_name}")
                # Try to get the collection first
                result = pb.collection(collection_name).get_list(1, 1)
                print(f"✅ Collection '{collection_name}' exists and accessible")
                
            except Exception as e:
                if "404" in str(e):
                    print(f"❌ Collection '{collection_name}' does not exist")
                    # Try to create it with a simple record
                    try:
                        simple_record = {
                            'test_field': 'test_value',
                            'created_at': '2024-10-15T20:00:00Z'
                        }
                        create_result = pb.collection(collection_name).create(simple_record)
                        print(f"✅ Created collection '{collection_name}' with record: {create_result.id}")
                    except Exception as create_error:
                        print(f"❌ Failed to create collection '{collection_name}': {create_error}")
                else:
                    print(f"❌ Error accessing collection '{collection_name}': {e}")
    
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    check_pocketbase_status()