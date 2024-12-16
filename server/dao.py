from pymongo import MongoClient
from datetime import datetime
import pandas as pd
from bson import ObjectId, json_util
import json
from dotenv import load_dotenv
import os
from geopy.geocoders import Nominatim
import geocoder

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
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

def check():
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    var = (datetime.now() + pd.DateOffset(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    print(var)

    db = connect()
    sos_collection = db.sos
    
    sos_records = list(sos_collection.find({}, {
        'taxiid': 1,
        'driverid': 1,
        'details': 1,
        'status': 1,
        'createdtime': 1,
        'actionedtime': 1,
        'sessionid': 1
    }))
    print(sos_records)

def raise_sos(location_data=None):
    try:
        print("Raising SOS alert...")
        db = connect()
        
        # If no location data is provided, get current location
        if location_data is None:
            location_data = get_current_location()
        
        print(f"Location data: {location_data}")
        sos_data = {
            'taxiid': ObjectId(),
            'driverid': ObjectId(),
            'details': 'Driver detected sleeping/drowsy. Immediate attention required.',
            'status': 'NEW',
            'createdtime': datetime.now(),
            'actionedtime': datetime.now(),
            'location': {
                'latitude': location_data['latitude'],
                'longitude': location_data['longitude'],
                'address': location_data['address']
            }
        }
        
        result = db.sos.insert_one(sos_data)
        if result.inserted_id:
            print("SOS alert raised successfully")
            return True
        return False
    except Exception as e:
        print(f"Error raising SOS: {e}")
        return False

def sos_details(sid=None):
    db = connect()
    sos_collection = db.sos
    
    sos_records = list(sos_collection.find({}, {
        'taxiid': 1,
        'driverid': 1,
        'details': 1,
        'status': 1,
        'createdtime': 1,
        'actionedtime': 1,
        'sessionid': 1,
        'location': 1  # Added location field to the projection
    }))
    
    return json.loads(json_util.dumps(sos_records))

def session_details():
    db = connect()
    pipeline = [
        {
            '$lookup': {
                'from': 'taxi',
                'localField': 'taxiid',
                'foreignField': '_id',
                'as': 'taxi'
            }
        },
        {
            '$lookup': {
                'from': 'user',
                'localField': 'userid',
                'foreignField': '_id',
                'as': 'user'
            }
        },
        {
            '$lookup': {
                'from': 'sos',
                'localField': '_id',
                'foreignField': 'sessionId',
                'as': 'sos'
            }
        },
        {
            '$match': {
                'user.type': 'Driver',
                'user.status': 'Active'
            }
        }
    ]
    
    sessions = list(db.session.aggregate(pipeline))
    formatted_sessions = []
    
    for session in sessions:
        formatted_session = {
            'TaxiNumber': session['taxi'][0]['number'],
            'FirstName': session['user'][0]['firstname'],
            'LastName': session['user'][0]['lastname'],
            'Code': session['user'][0]['code'],
            'StartTime': session['starttime'].strftime('%Y-%m-%d %H:%M:%S'),
            'EndTime': session['endtime'].strftime('%Y-%m-%d %H:%M:%S'),
            'Status': 'SOS Actioned' if session.get('sos') else 'Active'
        }
        formatted_sessions.append(formatted_session)
    
    return formatted_sessions

def action_sos(sid):
    db = connect()
    db.sos.update_one(
        {'_id': ObjectId(sid)},
        {'$set': {'actionedtime': datetime.now()}}
    )

def login(pid, taxi, password):
    db = connect()
    user = db.user.find_one({
        '_id': ObjectId(pid),
        'password': password
    })
    
    taxi_doc = db.taxi.find_one({'number': taxi})
    
    if user and taxi_doc:
        session_data = {
            'taxiid': taxi_doc['_id'],
            'userid': ObjectId(pid),
            'starttime': datetime.now(),
            'endtime': datetime.now() + pd.DateOffset(hours=8)
        }
        db.session.insert_one(session_data)

def admlogin(pid, password):
    db = connect()
    user = db.user.find_one({
        '_id': ObjectId(pid),
        'password': password
    }, {'status': 1})
    return [user] if user else []


def create_user(user_data):
    try:
        db = connect()
        result = db.user.insert_one(user_data)
        return str(result.inserted_id)
    except Exception as e:
        print(f"Error creating user: {e}")
        return None
    
    
class DAO:
    if __name__ == "__main__":
        check()