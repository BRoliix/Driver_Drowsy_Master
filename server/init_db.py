from dao import connect

def init_database():
    """
    Initialize PocketBase collections.
    Note: In PocketBase, collections are created automatically when first used.
    This function can be used to create sample data or verify connection.
    """
    pb = connect()
    
    print("Connected to PocketBase successfully!")
    print("Collections will be auto-created when first used.")
    print("Required collections:")
    print("- users: Store user information (drivers and admins)")
    print("- taxis: Store taxi information") 
    print("- sessions: Store active driving sessions")
    print("- sos: Store SOS alerts")
    
    # Example: Create a test user (optional)
    try:
        test_user = {
            'firstname': 'Test',
            'lastname': 'Driver',
            'type': 'Driver',
            'status': 'Active',
            'code': 'TD001',
            'password': 'test123'
        }
        # Uncomment the line below if you want to create a test user
        # pb.collection('users').create(test_user)
        print("Database initialization completed!")
    except Exception as e:
        print(f"Note: {e}")

if __name__ == "__main__":
    init_database()