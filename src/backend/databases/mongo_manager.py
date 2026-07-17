from pymongo import MongoClient
import datetime
from typing import List, Dict, Any
import os
import sys

# Add parent directory to path so we can import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.db_manager import TicketDBManager

class MongoDBManager(TicketDBManager):
    def __init__(self, uri: str = "mongodb://localhost:27017/", db_name: str = "ticketmaster_db", app_id: str = "ticketmaster"):
        super().__init__()
        self.app_id = app_id
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.seats_col = self.db["seats"]
        self.oplog_col = self.db["oplog"]
        
        # Check for schema migration
        first_seat = self.seats_col.find_one()
        if first_seat and "origin_app" not in first_seat:
            self.seats_col.delete_many({})
            self.oplog_col.delete_many({})
            
        if self.seats_col.count_documents({}) == 0:
            self.initialize_seats()

    def get_seats(self) -> List[Dict[str, Any]]:
        seats = list(self.seats_col.find({}, {"_id": 0}))
        # Handle legacy documents without origin_app just in case
        for s in seats:
            if "origin_app" not in s:
                s["origin_app"] = "unknown"
        return sorted(seats, key=lambda x: x["seat_id"])

    def get_seat(self, seat_id: str) -> Dict[str, Any]:
        seat = self.seats_col.find_one({"seat_id": seat_id}, {"_id": 0})
        if seat and "origin_app" not in seat:
            seat["origin_app"] = "unknown"
        return seat

    def update_seat(self, seat_id: str, status: str, updated_at: float = None, origin_app: str = None) -> bool:
        if updated_at is None:
            updated_at = datetime.datetime.now().timestamp()
        if origin_app is None:
            origin_app = self.app_id
            
        self.seats_col.update_one(
            {"seat_id": seat_id},
            {"$set": {"status": status, "updated_at": updated_at, "origin_app": origin_app}},
            upsert=True
        )
        
        self.oplog_col.insert_one({
            "seat_id": seat_id,
            "status": status,
            "updated_at": updated_at,
            "origin_app": origin_app
        })
        
        return True

    def get_oplog(self) -> List[Dict[str, Any]]:
        ops = list(self.oplog_col.find({}, {"_id": 0}).sort("updated_at", 1))
        for op in ops:
            if "origin_app" not in op:
                op["origin_app"] = "unknown"
        return ops
