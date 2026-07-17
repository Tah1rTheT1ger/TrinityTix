from abc import ABC, abstractmethod
from typing import List, Dict, Any
import datetime

class TicketDBManager(ABC):
    def __init__(self):
        self.app_name = "Unknown"
        self.app_id = "unknown"

    @abstractmethod
    def get_seats(self) -> List[Dict[str, Any]]:
        """
        Return a list of all seats.
        Expected format per seat:
        {
            "seat_id": str,
            "status": str, ("available", "held", "booked")
            "updated_at": float,
            "origin_app": str
        }
        """
        pass

    @abstractmethod
    def get_seat(self, seat_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def update_seat(self, seat_id: str, status: str, updated_at: float = None, origin_app: str = None) -> bool:
        """
        Update the status of a seat.
        If updated_at is None, use current timestamp.
        """
        pass

    @abstractmethod
    def get_oplog(self) -> List[Dict[str, Any]]:
        pass

    def get_priority(self, status: str) -> int:
        if status == "booked":
            return 3
        elif status == "held":
            return 2
        return 1 # available or unknown

    def merge(self, other_db: 'TicketDBManager'):
        """
        Merge state from another database using their oplog.
        Priority logic:
        - booked (3) > held (2) > available (1)
        - If equal priority, the one with the EARLIER updated_at wins (First Come First Served).
        """
        other_oplog = other_db.get_oplog()
        for op in other_oplog:
            seat_id = op["seat_id"]
            other_status = op["status"]
            other_updated = op["updated_at"]
            other_origin = op.get("origin_app", "unknown")
            
            my_seat = self.get_seat(seat_id)
            if my_seat is None:
                # If seat doesn't exist, create it
                self.update_seat(seat_id, other_status, other_updated, other_origin)
                continue

            my_status = my_seat["status"]
            my_updated = my_seat["updated_at"]
            my_origin = my_seat.get("origin_app", "unknown")

            my_priority = self.get_priority(my_status)
            other_priority = self.get_priority(other_status)

            # If target has higher priority (e.g. booked vs held)
            if other_priority > my_priority:
                self.update_seat(seat_id, other_status, other_updated, other_origin)
            
            # If target has lower priority (e.g. held vs booked), do nothing
            elif other_priority < my_priority:
                pass
            
            # If priorities are equal, use First-Come-First-Served (earlier timestamp wins)
            else:
                if other_updated < my_updated:
                    # Target's action happened earlier, so they win the FCFS race
                    self.update_seat(seat_id, other_status, other_updated, other_origin)
                elif other_updated == my_updated:
                    # Extremely rare tie, fallback to tie-breaker logic if origin is different
                    if other_origin != my_origin and other_origin < my_origin:
                         self.update_seat(seat_id, other_status, other_updated, other_origin)

    def initialize_seats(self, rows: int = 5, cols: int = 10):
        """
        Helper to initialize the database with available seats.
        Rows: A, B, C... Cols: 1, 2, 3...
        """
        now = datetime.datetime.now().timestamp()
        for r in range(rows):
            row_letter = chr(ord('A') + r)
            for c in range(1, cols + 1):
                seat_id = f"{row_letter}{c}"
                self.update_seat(seat_id, "available", now, "system")
