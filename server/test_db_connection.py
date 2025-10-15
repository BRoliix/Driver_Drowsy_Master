from dao import raise_sos, sos_details, get_current_location
from datetime import datetime

def test_database_functionality():
    """
    Test database functionality with both PocketBase and local storage fallback
    """
    print("🧪 Testing Database Functionality")
    print("=" * 50)
    
    # Test 1: Raise SOS Alert
    print("\n1️⃣  Testing SOS Alert Creation...")
    test_location = {
        'latitude': 25.0772,
        'longitude': 55.3093,
        'address': 'Test Location, Dubai, UAE'
    }
    
    result = raise_sos(test_location)
    if result:
        print("✅ SOS alert created successfully!")
    else:
        print("❌ Failed to create SOS alert")
    
    # Test 2: Get SOS Details
    print("\n2️⃣  Testing SOS Details Retrieval...")
    try:
        sos_records = sos_details()
        print(f"✅ Retrieved {len(sos_records)} SOS records")
        
        if sos_records:
            print("\n📋 Latest SOS Record:")
            latest = sos_records[-1] if isinstance(sos_records, list) else sos_records
            for key, value in latest.items():
                if isinstance(value, dict):
                    print(f"   {key}: {value}")
                else:
                    print(f"   {key}: {value}")
        
    except Exception as e:
        print(f"❌ Error retrieving SOS details: {e}")
    
    # Test 3: Location Services
    print("\n3️⃣  Testing Location Services...")
    try:
        location = get_current_location()
        print("✅ Location service working:")
        print(f"   Latitude: {location['latitude']}")
        print(f"   Longitude: {location['longitude']}")
        print(f"   Address: {location['address']}")
    except Exception as e:
        print(f"❌ Location service error: {e}")
    
    # Check local storage files
    print("\n4️⃣  Checking Local Storage...")
    import os
    local_data_dir = "local_data"
    if os.path.exists(local_data_dir):
        files = os.listdir(local_data_dir)
        print(f"✅ Local storage directory exists with {len(files)} files:")
        for file in files:
            file_path = os.path.join(local_data_dir, file)
            size = os.path.getsize(file_path)
            print(f"   📄 {file} ({size} bytes)")
    else:
        print("⚠️  Local storage directory not found")
    
    print("\n🎉 Database Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_database_functionality()