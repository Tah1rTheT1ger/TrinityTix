import sqlite3
import datetime
from typing import List, Dict, Any
import os
import sys

# Add parent directory to path so we can import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.db_manager import TicketDBManager

class SQLiteManager(TicketDBManager):
    def __init__(self, db_path: str = "sqlite_app.db", app_id: str = "district"):
        super().__init__()
        self.app_id = app_id
        self.db_path = db_path
        self._init_db()
        
        # Initialize if empty
        if not self.get_seats():
            self.initialize_seats()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Drop old schema if this is a fresh run with new requirements
            try:
                cursor.execute("SELECT origin_app FROM seats LIMIT 1")
            except sqlite3.OperationalError:
                # Column doesn't exist, drop tables
                cursor.execute("DROP TABLE IF EXISTS seats")
                cursor.execute("DROP TABLE IF EXISTS oplog")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS seats (
                    seat_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    updated_at REAL NOT NULL,
                    origin_app TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS oplog (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    seat_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    updated_at REAL NOT NULL,
                    origin_app TEXT NOT NULL
                )
            """)
            conn.commit()

    def get_seats(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT seat_id, status, updated_at, origin_app FROM seats")
            rows = cursor.fetchall()
            return [{"seat_id": r[0], "status": r[1], "updated_at": r[2], "origin_app": r[3]} for r in rows]

    def get_seat(self, seat_id: str) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT seat_id, status, updated_at, origin_app FROM seats WHERE seat_id = ?", (seat_id,))
            row = cursor.fetchone()
            if row:
                return {"seat_id": row[0], "status": row[1], "updated_at": row[2], "origin_app": row[3]}
            return None

    def update_seat(self, seat_id: str, status: str, updated_at: float = None, origin_app: str = None) -> bool:
        if updated_at is None:
            updated_at = datetime.datetime.now().timestamp()
        if origin_app is None:
            origin_app = self.app_id
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO seats (seat_id, status, updated_at, origin_app)
                VALUES (?, ?, ?, ?)
            """, (seat_id, status, updated_at, origin_app))
            
            cursor.execute("""
                INSERT INTO oplog (seat_id, status, updated_at, origin_app)
                VALUES (?, ?, ?, ?)
            """, (seat_id, status, updated_at, origin_app))
            conn.commit()
        return True

    def get_oplog(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT seat_id, status, updated_at, origin_app FROM oplog ORDER BY updated_at ASC")
            rows = cursor.fetchall()
            return [{"seat_id": r[0], "status": r[1], "updated_at": r[2], "origin_app": r[3]} for r in rows]
