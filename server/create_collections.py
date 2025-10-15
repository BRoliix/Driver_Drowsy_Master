from dao import connect
from datetime import datetime

def create_pocketbase_collections():
    """
    Create PocketBase collections using admin authentication
    """
    pb = connect()
    
    print("🔧 Setting up PocketBase collections with admin access...")
    
    collections_created = []
    
    # 1. Create SOS alerts collection
    try:
        print("\n📋 Creating sos_alerts collection...")
        sos_data = {
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
        
        result = pb.collection('sos_alerts').create(sos_data)
        print(f"✅ sos_alerts collection created with record: {result.id}")
        collections_created.append('sos_alerts')
        
    except Exception as e:
        print(f"❌ Error creating sos_alerts: {e}")
    
    # 2. Create users collection
    try:
        print("\n👤 Creating users collection...")
        user_data = {
            'firstname': 'John',
            'lastname': 'Driver',
            'type': 'Driver',
            'status': 'Active',
            'code': 'DRV001',
            'email': 'john.driver@example.com'
        }
        
        result = pb.collection('users').create(user_data)
        print(f"✅ users collection created with record: {result.id}")
        collections_created.append('users')
        
    except Exception as e:
        print(f"❌ Error creating users: {e}")
    
    # 3. Create taxis collection
    try:
        print("\n🚗 Creating taxis collection...")
        taxi_data = {
            'number': 'TX001',
            'model': 'Toyota Camry',
            'year': '2022',
            'status': 'Active'
        }
        
        result = pb.collection('taxis').create(taxi_data)
        print(f"✅ taxis collection created with record: {result.id}")
        collections_created.append('taxis')
        
    except Exception as e:
        print(f"❌ Error creating taxis: {e}")
    
    # 4. Create sessions collection
    try:
        print("\n📅 Creating sessions collection...")
        session_data = {
            'taxiid': 'TX001',
            'userid': 'DRV001',
            'starttime': datetime.now().isoformat(),
            'endtime': datetime.now().isoformat(),
            'status': 'Active'
        }
        
        result = pb.collection('sessions').create(session_data)
        print(f"✅ sessions collection created with record: {result.id}")
        collections_created.append('sessions')
        
    except Exception as e:
        print(f"❌ Error creating sessions: {e}")
    
    print(f"\n🎉 Collection setup complete!")
    print(f"✅ Successfully created {len(collections_created)} collections: {', '.join(collections_created)}")
    
    return collections_created

if __name__ == "__main__":
    created = create_pocketbase_collections()
    if 'sos_alerts' in created:
        print("\n🚨 SOS alerts will now be stored in PocketBase!")
    else:
        print("\n⚠️  SOS alerts collection not created - check errors above")