from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from databases.sqlite_manager import SQLiteManager
from databases.redis_manager import RedisManager
from databases.mongo_manager import MongoDBManager

app = FastAPI(title="TrinityTix Sync API")

# Setup CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB managers
managers = {
    "district": SQLiteManager(app_id="district"),
    "bookmyshow": RedisManager(app_id="bookmyshow"),
    "ticketmaster": MongoDBManager(app_id="ticketmaster")
}

class SeatUpdateRequest(BaseModel):
    status: str

class MergeRequest(BaseModel):
    source: str
    target: str

@app.get("/api/{app_id}/seats")
def get_seats(app_id: str):
    if app_id not in managers:
        raise HTTPException(status_code=404, detail="App not found")
    
    manager = managers[app_id]
    return manager.get_seats()

@app.post("/api/{app_id}/seats/{seat_id}")
def update_seat(app_id: str, seat_id: str, request: SeatUpdateRequest):
    if app_id not in managers:
        raise HTTPException(status_code=404, detail="App not found")
    
    manager = managers[app_id]
    manager.update_seat(seat_id, request.status)
    return {"message": "Seat updated successfully"}

@app.post("/api/sync")
def sync_databases(request: MergeRequest):
    if request.source not in managers or request.target not in managers:
        raise HTTPException(status_code=400, detail="Invalid source or target app")
    
    source_manager = managers[request.source]
    target_manager = managers[request.target]
    
    # Merge source into target
    target_manager.merge(source_manager)
    return {"message": f"Successfully merged {request.source} into {request.target}"}

@app.post("/api/reset")
def reset_databases():
    for manager in managers.values():
        manager.initialize_seats()
    return {"message": "All databases reset"}
