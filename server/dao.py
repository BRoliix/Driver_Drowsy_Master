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
    g = geocoder.ip('me')
    geolocator = Nominatim(user_agent="my_agent")
    location = geolocator.reverse(f"{g.latlng[0]}, {g.latlng[1]}")
    return {
        'latitude': g.latlng[0],
        'longitude': g.latlng[1],
        'address': location.address if location else 'Unknown'
    }

load_dotenv()

def connect():
    pb = PocketBase(os.getenv('POCKETBASE_URL'))
    
    # Authenticate as admin if credentials are available
    admin_email = os.getenv('POCKETBASE_ADMIN_EMAIL')
    admin_password = os.getenv('POCKETBASE_ADMIN_PASSWORD')
    
    if admin_email and admin_password:
        try:
            pb.admins.auth_with_password(admin_email, admin_password)
            print("✅ Admin authenticated successfully")
        except Exception as e:
            print(f"⚠️  Admin authentication failed: {e}")
    
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
        print("💾 Creating SOS record...")
        result = pb.collection('sos_alerts').create(sos_data)
        print(f"✅ SOS alert saved to PocketBase successfully with ID: {result.id}")
        return True
            
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