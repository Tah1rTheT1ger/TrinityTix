import redis
import json
import datetime
from typing import List, Dict, Any
import os
import sys

# Add parent directory to path so we can import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.db_manager import TicketDBManager

class RedisManager(TicketDBManager):
    def __init__(self, host: str = None, port: int = None, db: int = 0, app_id: str = "bookmyshow"):
        super().__init__()
        self.app_id = app_id
        
        if host is None:
            host = os.getenv("REDIS_HOST", "localhost")
        if port is None:
            port = int(os.getenv("REDIS_PORT", 6379))
            
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        
        # Check if we need to reset/migrate data (for demo purposes)
        first_seat = self.client.hgetall("seat:A1")
        if first_seat and "origin_app" not in first_seat:
            self.client.flushdb() # Clear DB to apply new schema
            
        if not self.get_seats():
            self.initialize_seats()

    def get_seats(self) -> List[Dict[str, Any]]:
        seats = []
        keys = self.client.keys("seat:*")
        for key in keys:
            data = self.client.hgetall(key)
            if data:
                seats.append({
                    "seat_id": data.get("seat_id"),
                    "status": data.get("status"),
                    "updated_at": float(data.get("updated_at", 0)),
                    "origin_app": data.get("origin_app", "unknown")
                })
        return sorted(seats, key=lambda x: x["seat_id"])

    def get_seat(self, seat_id: str) -> Dict[str, Any]:
        data = self.client.hgetall(f"seat:{seat_id}")
        if data and "seat_id" in data:
            return {
                "seat_id": data.get("seat_id"),
                "status": data.get("status"),
                "updated_at": float(data.get("updated_at", 0)),
                "origin_app": data.get("origin_app", "unknown")
            }
        return None

    def update_seat(self, seat_id: str, status: str, updated_at: float = None, origin_app: str = None) -> bool:
        if updated_at is None:
            updated_at = datetime.datetime.now().timestamp()
        if origin_app is None:
            origin_app = self.app_id
            
        self.client.hset(f"seat:{seat_id}", mapping={
            "seat_id": seat_id,
            "status": status,
            "updated_at": str(updated_at),
            "origin_app": origin_app
        })
        
        oplog_entry = {
            "seat_id": seat_id,
            "status": status,
            "updated_at": updated_at,
            "origin_app": origin_app
        }
        self.client.rpush("oplog", json.dumps(oplog_entry))
        
        return True

    def get_oplog(self) -> List[Dict[str, Any]]:
        oplog_entries = self.client.lrange("oplog", 0, -1)
        return [json.loads(entry) for entry in oplog_entries]
