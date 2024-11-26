from dao import connect

def init_database():
    db = connect()  
    
    collections = {
        'user': {
            'validator': {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['firstname', 'lastname', 'type', 'status', 'code', 'password'],
                    'properties': {
                        'firstname': {'bsonType': 'string'},
                        'lastname': {'bsonType': 'string'},
                        'type': {'enum': ['Driver', 'Admin']},
                        'status': {'enum': ['Active', 'Inactive']},
                        'code': {'bsonType': 'string'},
                        'password': {'bsonType': 'string'}
                    }
                }
            }
        },
        'taxi': {
            'validator': {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['number'],
                    'properties': {
                        'number': {'bsonType': 'string'}
                    }
                }
            }
        },
        'session': {
            'validator': {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['taxiid', 'userid', 'starttime', 'endtime'],
                    'properties': {
                        'taxiid': {'bsonType': 'objectId'},
                        'userid': {'bsonType': 'objectId'},
                        'starttime': {'bsonType': 'date'},
                        'endtime': {'bsonType': 'date'}
                    }
                }
            }
        },
        'sos': {
            'validator': {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['taxiid', 'driverid', 'details', 'status', 'createdtime'],
                    'properties': {
                        'taxiid': {'bsonType': 'objectId'},
                        'driverid': {'bsonType': 'objectId'},
                        'details': {'bsonType': 'string'},
                        'status': {'enum': ['NEW', 'ACTIONED']},
                        'createdtime': {'bsonType': 'date'},
                        'actionedtime': {'bsonType': 'date'},
                        'sessionId': {'bsonType': 'objectId'}
                    }
                }
            }
        }
    }

    for name, config in collections.items():
        if name not in db.list_collection_names():
            db.create_collection(name, validator=config['validator'])

    db.user.create_index([("type", 1), ("status", 1)])
    db.taxi.create_index([("number", 1)], unique=True)
    db.sos.create_index([("actionedtime", 1)])
    
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_database()