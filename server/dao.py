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

def setup_sos_collection():
    """Try to create the sos_alerts collection if admin auth works"""
    try:
        pb = PocketBase(os.getenv('POCKETBASE_URL'))
        admin_email = os.getenv('POCKETBASE_ADMIN_EMAIL')
        admin_password = os.getenv('POCKETBASE_ADMIN_PASSWORD')
        
        if admin_email and admin_password:
            pb.admins.auth_with_password(admin_email, admin_password)
            
            # Create collection schema
            collection_data = {
                "name": "sos_alerts",
                "type": "base",
                "schema": [
                    {"name": "taxiid", "type": "text"},
                    {"name": "driverid", "type": "text"},
                    {"name": "details", "type": "text"},
                    {"name": "status", "type": "text"},
                    {"name": "createdtime", "type": "text"},
                    {"name": "actionedtime", "type": "text"},
                    {"name": "latitude", "type": "number"},
                    {"name": "longitude", "type": "number"},
                    {"name": "address", "type": "text"}
                ],
                "listRule": "",  # Anyone can list
                "viewRule": "",  # Anyone can view
                "createRule": "",  # Anyone can create
                "updateRule": "",  # Anyone can update
                "deleteRule": ""   # Anyone can delete
            }
            
            result = pb.send("/api/collections", "POST", collection_data)
            print(f"✅ Created sos_alerts collection: {result}")
            return True
    except Exception as e:
        print(f"❌ Failed to create collection: {e}")
        return False

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
            'createdtime': datetime.now().isoformat(),
            'actionedtime': datetime.now().isoformat(),
            'latitude': location_data['latitude'],
            'longitude': location_data['longitude'],
            'address': location_data['address']
        }
        
        print(f"📝 SOS data to save: {sos_data}")
        
        # Save to PocketBase
        print("🔗 Connecting to PocketBase...")
        pb = connect()
        
        # Try different collection names and approaches
        collection_names = ['sos_alerts', 'sos', 'alerts']
        
        for collection_name in collection_names:
            print(f"💾 Trying to create SOS record in '{collection_name}' collection...")
            
            try:
                result = pb.collection(collection_name).create(sos_data)
                print(f"✅ SOS alert saved to PocketBase successfully in '{collection_name}' with ID: {result.id}")
                return True
            except Exception as create_error:
                print(f"❌ Create in '{collection_name}' failed: {create_error}")
                
                # Try without authentication for this collection
                print(f"🔄 Trying '{collection_name}' without authentication...")
                pb_public = PocketBase(os.getenv('POCKETBASE_URL'))
                try:
                    result = pb_public.collection(collection_name).create(sos_data)
                    print(f"✅ SOS alert saved to PocketBase (public) in '{collection_name}' with ID: {result.id}")
                    return True
                except Exception as public_error:
                    print(f"❌ Public create in '{collection_name}' also failed: {public_error}")
                    continue
        
        # Try to setup the collection if all attempts failed
        print("🔧 Attempting to create sos_alerts collection...")
        if setup_sos_collection():
            print("✅ Collection created, retrying SOS save...")
            try:
                result = pb.collection('sos_alerts').create(sos_data)
                print(f"✅ SOS alert saved after collection creation with ID: {result.id}")
                return True
            except Exception as retry_error:
                print(f"❌ Retry after collection creation failed: {retry_error}")
        
        # If all PocketBase attempts fail, save locally as fallback
        print("💾 All PocketBase attempts failed, saving SOS locally as fallback...")
        from local_storage import local_store
        
        try:
            local_sos_id = local_store.add_sos_alert(
                taxiid='',
                driverid='', 
                details=sos_data['details'],
                status=sos_data['status'],
                latitude=sos_data['latitude'],
                longitude=sos_data['longitude'],
                address=sos_data['address']
            )
            print(f"✅ SOS alert saved locally with ID: {local_sos_id}")
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