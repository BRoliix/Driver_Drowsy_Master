from dao import connect
from datetime import datetime

def setup_pocketbase_collections():
    """
    Setup PocketBase collections by creating sample records.
    In PocketBase, collections are auto-created when first record is inserted.
    """
    pb = connect()
    print("Setting up PocketBase collections...")
    
    try:
        # 1. Create SOS collection with a test record
        print("\n1. Setting up SOS collection...")
        test_sos = {
            'taxiid': 'TAXI001',
            'driverid': 'DRIVER001', 
            'details': 'Test SOS alert - Driver drowsiness detected',
            'status': 'NEW',
            'createdtime': datetime.now().isoformat(),
            'actionedtime': datetime.now().isoformat(),
            'latitude': 25.0772,
            'longitude': 55.3093,
            'address': 'Test Location, Dubai, UAE'
        }
        
        sos_result = pb.collection('sos').create(test_sos)
        print(f"✅ SOS collection created with record ID: {sos_result.id}")
        
    except Exception as e:
        print(f"❌ Error creating SOS collection: {e}")
    
    try:
        # 2. Create Users collection
        print("\n2. Setting up Users collection...")
        test_user = {
            'firstname': 'John',
            'lastname': 'Driver',
            'type': 'Driver',
            'status': 'Active',
            'code': 'DRV001',
            'password': 'test123',
            'email': 'john.driver@example.com'
        }
        
        user_result = pb.collection('users').create(test_user)
        print(f"✅ Users collection created with record ID: {user_result.id}")
        
    except Exception as e:
        print(f"❌ Error creating Users collection: {e}")
    
    try:
        # 3. Create Taxis collection
        print("\n3. Setting up Taxis collection...")
        test_taxi = {
            'number': 'TX001',
            'model': 'Toyota Camry',
            'year': '2022',
            'status': 'Active'
        }
        
        taxi_result = pb.collection('taxis').create(test_taxi)
        print(f"✅ Taxis collection created with record ID: {taxi_result.id}")
        
    except Exception as e:
        print(f"❌ Error creating Taxis collection: {e}")
    
    try:
        # 4. Create Sessions collection
        print("\n4. Setting up Sessions collection...")
        test_session = {
            'taxiid': 'TX001',  # Reference to taxi
            'userid': 'DRV001',  # Reference to user
            'starttime': datetime.now().isoformat(),
            'endtime': datetime.now().isoformat(),
            'status': 'Active'
        }
        
        session_result = pb.collection('sessions').create(test_session)
        print(f"✅ Sessions collection created with record ID: {session_result.id}")
        
    except Exception as e:
        print(f"❌ Error creating Sessions collection: {e}")
    
    print("\n🎉 Database setup completed!")
    print("\nCollections created:")
    print("- sos: Store SOS alerts from drowsiness detection")
    print("- users: Store driver and admin information")  
    print("- taxis: Store taxi/vehicle information")
    print("- sessions: Store active driving sessions")

if __name__ == "__main__":
    setup_pocketbase_collections()