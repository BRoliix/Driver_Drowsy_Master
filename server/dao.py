from pocketbase import PocketBase
from datetime import datetime
import pandas as pd
import json
from dotenv import load_dotenv
import os
from geopy.geocoders import Nominatim
import geocoder
from local_storage import local_store

def get_current_location():
    try:
        print("🌍 Getting location via IP...")
        g = geocoder.ip('me')
        print(f"📍 IP Location: {g.latlng}")
        
        if g.latlng and len(g.latlng) >= 2:
            try:
                geolocator = Nominatim(user_agent="drowsiness_detector")
                location = geolocator.reverse(f"{g.latlng[0]}, {g.latlng[1]}")
                address = location.address if location else 'Unknown location'
            except Exception as e:
                print(f"⚠️ Geocoding failed: {e}")
                address = 'Unknown location'
            
            return {
                'latitude': g.latlng[0],
                'longitude': g.latlng[1],
                'address': address
            }
        else:
            # Fallback to default location if IP location fails
            print("⚠️ IP location failed, using default location")
            return {
                'latitude': 40.7128,  # NYC coordinates as fallback
                'longitude': -74.0060,
                'address': 'Location unavailable'
            }
    except Exception as e:
        print(f"❌ Location service error: {e}")
        return {
            'latitude': 40.7128,  # NYC coordinates as fallback
            'longitude': -74.0060,
            'address': 'Location unavailable'
        }

load_dotenv()

def connect():
    pb_url = os.getenv('POCKETBASE_URL')
    print(f"🔗 Connecting to PocketBase: {pb_url}")
    pb = PocketBase(pb_url)
    
    # Try admin authentication first
    admin_email = os.getenv('POCKETBASE_ADMIN_EMAIL')
    admin_password = os.getenv('POCKETBASE_ADMIN_PASSWORD')
    
    if admin_email and admin_password:
        try:
            pb.admins.auth_with_password(admin_email, admin_password)
            print("✅ Admin authenticated successfully")
            return pb
        except Exception as e:
            print(f"⚠️  Admin authentication failed: {e}")
    
    # If admin auth fails, try regular user auth (if it's also a regular user)
    if admin_email and admin_password:
        try:
            pb.collection('users').auth_with_password(admin_email, admin_password)
            print("✅ User authenticated successfully")
            return pb
        except Exception as e:
            print(f"⚠️  User authentication failed: {e}")
    
    print("⚠️  No authentication successful, proceeding without auth")
    return pb



def check():
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    var = (datetime.now() + pd.DateOffset(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    print(var)

    pb = connect()
    
    try:
        sos_records = pb.collection('sos').get_full_list()
        print(sos_records)
    except Exception as e:
        print(f"Error fetching SOS records: {e}")

def raise_sos(location_data=None):
    try:
        print("🚨 Raising SOS alert...")
        
        # If no location data is provided, get current location
        if location_data is None:
            print("Getting current location...")
            location_data = get_current_location()
        
        print(f"📍 Location data: {location_data}")
        sos_data = {
            'taxiid': '',  # Will be set when user logs in
            'driverid': '',  # Will be set when user logs in
            'details': 'Driver detected sleeping/drowsy. Immediate attention required.',
            'status': 'NEW',
            'actionedtime': datetime.now().isoformat(),
            'latitude': location_data['latitude'],
            'longitude': location_data['longitude'],
            'address': location_data['address']
        }
        
        # For local storage, include createdtime
        local_sos_data = sos_data.copy()
        local_sos_data['createdtime'] = datetime.now().isoformat()
        
        print(f"📝 SOS data to save: {sos_data}")
        
        # Save to PocketBase - try once quickly, then fallback
        print("🔗 Connecting to PocketBase...")
        pb = connect()
        
        # Try to get collection info for debugging
        try:
            collection_info = pb.send("/api/collections/sos_alerts", "GET")
            print(f"📋 Collection schema: {collection_info}")
        except Exception as schema_error:
            print(f"⚠️ Could not get collection schema: {schema_error}")
        
        try:
            # Try the main collection first
            print(f"📤 Sending data to PocketBase: {sos_data}")
            result = pb.collection('sos_alerts').create(sos_data)
            print(f"✅ SOS alert saved to PocketBase successfully with ID: {result.id}")
            return True
        except Exception as create_error:
            print(f"❌ PocketBase save failed: {create_error}")
            print(f"📤 Failed data was: {sos_data}")
            
            # Try to get more detailed error info
            if hasattr(create_error, 'data'):
                print(f"🔍 Error details: {create_error.data}")
            if hasattr(create_error, 'response'):
                print(f"🔍 Error response: {create_error.response}")
            
            # Let's also try creating a minimal record to test
            print("🧪 Testing with minimal data...")
            try:
                minimal_data = {
                    'details': 'Test SOS',
                    'status': 'NEW'
                }
                test_result = pb.collection('sos_alerts').create(minimal_data)
                print(f"✅ Minimal record created successfully: {test_result.id}")
                
                # If minimal works, try adding fields one by one
                print("🧪 Testing with location data...")
                location_data = {
                    'details': 'Test SOS with location',
                    'status': 'NEW',
                    'latitude': 1.2959,
                    'longitude': 103.7907
                }
                test_result2 = pb.collection('sos_alerts').create(location_data)
                print(f"✅ Location record created successfully: {test_result2.id}")
                
            except Exception as test_error:
                print(f"❌ Even minimal record failed: {test_error}")
                if hasattr(test_error, 'data'):
                    print(f"🔍 Test error details: {test_error.data}")
            
            # Quick fallback to local storage
            print("💾 Saving SOS locally as fallback...")
            from local_storage import local_store
            
            try:
                local_record = local_store.create_record('sos_alerts', local_sos_data)
                print(f"✅ SOS alert saved locally with ID: {local_record['id']}")
                return True
            except Exception as local_error:
                print(f"❌ Local save also failed: {local_error}")
                return False
            
    except Exception as e:
        print(f"❌ Error raising SOS: {e}")
        import traceback
        traceback.print_exc()
        return False

def sos_details(sid=None):
    try:
        pb = connect()
        if sid:
            sos_records = [pb.collection('sos_alerts').get_one(sid)]
        else:
            sos_records = pb.collection('sos_alerts').get_full_list()
        
        print(f"✅ SOS details fetched from PocketBase ({len(sos_records)} records)")
        return sos_records
        
    except Exception as e:
        print(f"❌ Error fetching SOS details from PocketBase: {e}")
        
        # Fallback to local storage
        try:
            from local_storage import local_store
            if sid:
                local_records = [local_store.get_record('sos_alerts', sid)]
            else:
                local_records = local_store.get_records('sos_alerts')
            
            print(f"✅ SOS details fetched from local storage ({len(local_records)} records)")
            return local_records
        except Exception as local_error:
            print(f"❌ Error fetching from local storage: {local_error}")
            return []

def session_details():
    pb = connect()
    
    try:
        # Get sessions with expanded relations
        sessions = pb.collection('sessions').get_full_list(expand='taxiid,userid')
        formatted_sessions = []
        
        for session in sessions:
            if hasattr(session, 'expand') and session.expand:
                taxi = session.expand.get('taxiid', {})
                user = session.expand.get('userid', {})
                
                if user.get('type') == 'Driver' and user.get('status') == 'Active':
                    formatted_session = {
                        'TaxiNumber': taxi.get('number', ''),
                        'FirstName': user.get('firstname', ''),
                        'LastName': user.get('lastname', ''),
                        'Code': user.get('code', ''),
                        'StartTime': session.get('starttime', ''),
                        'EndTime': session.get('endtime', ''),
                        'Status': 'Active'  # Simplified for now
                    }
                    formatted_sessions.append(formatted_session)
        
        return formatted_sessions
    except Exception as e:
        print(f"Error fetching session details: {e}")
        return []

def action_sos(sid):
    pb = connect()
    try:
        pb.collection('sos').update(sid, {'actionedtime': datetime.now().isoformat()})
    except Exception as e:
        print(f"Error updating SOS: {e}")

def login(pid, taxi, password):
    pb = connect()
    try:
        # Find user by ID and password
        user = pb.collection('users').get_one(pid)
        if user and user.password == password:
            # Find taxi by number
            taxi_list = pb.collection('taxis').get_list(1, 1, {'filter': f'number="{taxi}"'})
            if taxi_list.items:
                taxi_doc = taxi_list.items[0]
                session_data = {
                    'taxiid': taxi_doc.id,
                    'userid': pid,
                    'starttime': datetime.now().isoformat(),
                    'endtime': (datetime.now() + pd.DateOffset(hours=8)).isoformat()
                }
                pb.collection('sessions').create(session_data)
                return True
        return False
    except Exception as e:
        print(f"Error during login: {e}")
        return False

def admlogin(pid, password):
    pb = connect()
    try:
        user = pb.collection('users').get_one(pid)
        if user and user.password == password and user.type == 'Admin':
            return [{'status': user.status}]
        return []
    except Exception as e:
        print(f"Error during admin login: {e}")
        return []


def create_user(user_data):
    try:
        pb = connect()
        result = pb.collection('users').create(user_data)
        return result.id
    except Exception as e:
        print(f"Error creating user: {e}")
        return None
    
    
class DAO:
    if __name__ == "__main__":
        check()