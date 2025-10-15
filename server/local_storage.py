import json
import os
from datetime import datetime
from typing import List, Dict, Any

class LocalDataStore:
    """
    Local JSON file-based data storage as fallback when PocketBase collections aren't available
    """
    
    def __init__(self, data_dir: str = "local_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize data files
        self.collections = {
            'sos_alerts': 'sos_alerts.json',
            'users': 'users.json', 
            'taxis': 'taxis.json',
            'sessions': 'sessions.json'
        }
        
        # Create empty files if they don't exist
        for collection, filename in self.collections.items():
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    json.dump([], f)
    
    def _load_collection(self, collection_name: str) -> List[Dict]:
        """Load data from JSON file"""
        filepath = os.path.join(self.data_dir, self.collections[collection_name])
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_collection(self, collection_name: str, data: List[Dict]):
        """Save data to JSON file"""
        filepath = os.path.join(self.data_dir, self.collections[collection_name])
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def create_record(self, collection_name: str, record_data: Dict) -> Dict:
        """Create a new record in collection"""
        data = self._load_collection(collection_name)
        
        # Generate simple ID
        new_id = f"{collection_name}_{len(data) + 1}_{int(datetime.now().timestamp())}"
        record_data['id'] = new_id
        record_data['created'] = datetime.now().isoformat()
        record_data['updated'] = datetime.now().isoformat()
        
        data.append(record_data)
        self._save_collection(collection_name, data)
        
        return record_data
    
    def get_records(self, collection_name: str, filter_func=None) -> List[Dict]:
        """Get all records from collection with optional filter"""
        data = self._load_collection(collection_name)
        
        if filter_func:
            return [record for record in data if filter_func(record)]
        
        return data
    
    def get_record(self, collection_name: str, record_id: str) -> Dict:
        """Get single record by ID"""
        data = self._load_collection(collection_name)
        
        for record in data:
            if record.get('id') == record_id:
                return record
        
        raise Exception(f"Record {record_id} not found in {collection_name}")
    
    def update_record(self, collection_name: str, record_id: str, update_data: Dict) -> Dict:
        """Update existing record"""
        data = self._load_collection(collection_name)
        
        for i, record in enumerate(data):
            if record.get('id') == record_id:
                record.update(update_data)
                record['updated'] = datetime.now().isoformat()
                data[i] = record
                self._save_collection(collection_name, data)
                return record
        
        raise Exception(f"Record {record_id} not found in {collection_name}")

# Global instance
local_store = LocalDataStore()