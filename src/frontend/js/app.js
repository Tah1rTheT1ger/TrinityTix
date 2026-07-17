const API_BASE_URL = 'https://trinitytix.onrender.com/api';
const APPS = ['district', 'bookmyshow', 'ticketmaster'];
const ROWS = 5;
const COLS = 10;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initSeats();
    fetchSeats();

    document.getElementById('sync-btn').addEventListener('click', syncDatabases);
    document.getElementById('reset-btn').addEventListener('click', resetDatabases);
    document.getElementById('clear-log').addEventListener('click', clearLog);
});

// Create DOM elements for seats
function initSeats() {
    APPS.forEach(app => {
        const container = document.getElementById(`seats-${app}`);
        container.innerHTML = ''; // Clear
        
        for (let r = 0; r < ROWS; r++) {
            const rowLetter = String.fromCharCode(65 + r); // A, B, C...
            for (let c = 1; c <= COLS; c++) {
                const seatId = `${rowLetter}${c}`;
                const seatDiv = document.createElement('div');
                seatDiv.className = 'seat';
                seatDiv.dataset.id = seatId;
                seatDiv.dataset.app = app;
                seatDiv.innerText = seatId; // For debugging, text color is transparent in CSS
                
                // Add click listener
                seatDiv.addEventListener('click', () => handleSeatClick(app, seatId, seatDiv));
                
                container.appendChild(seatDiv);
            }
        }
    });
}

// Fetch seats from all backends
async function fetchSeats() {
    for (const app of APPS) {
        try {
            logNetwork(`GET /api/${app}/seats`, 'get');
            const response = await fetch(`${API_BASE_URL}/${app}/seats`);
            const seats = await response.json();
            
            seats.forEach(seat => {
                updateSeatUI(app, seat.seat_id, seat.status, seat.origin_app);
            });
        } catch (error) {
            console.error(`Error fetching seats for ${app}:`, error);
            logNetwork(`ERROR: Failed to fetch ${app}`, 'error');
        }
    }
}

// Handle Seat Click (Toggle Available -> Held -> Booked)
async function handleSeatClick(app, seatId, seatDiv) {
    let currentStatus = 'available';
    if (seatDiv.classList.contains('held')) currentStatus = 'held';
    if (seatDiv.classList.contains('booked')) currentStatus = 'booked';
    
    let newStatus = 'available';
    if (currentStatus === 'available') {
        newStatus = 'held'; // Select it
    } else if (currentStatus === 'held') {
        newStatus = 'booked'; // Confirm booking
    } else {
        return; // Already booked, do nothing
    }
    
    // Optimistic UI update - set origin to the current app since we are modifying it
    updateSeatUI(app, seatId, newStatus, app);
    
    // API Call
    try {
        logNetwork(`POST /api/${app}/seats/${seatId} -> ${newStatus}`, 'post');
        await fetch(`${API_BASE_URL}/${app}/seats/${seatId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
    } catch (error) {
        console.error(`Error updating seat ${seatId} on ${app}:`, error);
        logNetwork(`ERROR: Failed to update seat on ${app}`, 'error');
        // Revert UI on failure (optimistic rollback assumes it was available)
        updateSeatUI(app, seatId, currentStatus, 'system');
    }
}

function updateSeatUI(app, seatId, status, origin_app) {
    const seatDiv = document.querySelector(`.seat[data-app="${app}"][data-id="${seatId}"]`);
    if (!seatDiv) return;
    
    seatDiv.className = 'seat'; // Reset
    if (status !== 'available') {
        seatDiv.classList.add(status);
        if (origin_app) {
            seatDiv.dataset.origin = origin_app;
        }
    } else {
        seatDiv.removeAttribute('data-origin');
    }
}

// Sync all databases
async function syncDatabases() {
    const syncBtn = document.getElementById('sync-btn');
    syncBtn.innerText = 'Syncing...';
    syncBtn.disabled = true;
    
    try {
        // Simple Ring Topology Sync for demo: A -> B, B -> C, C -> A
        await performMerge('district', 'bookmyshow');
        await performMerge('bookmyshow', 'ticketmaster');
        await performMerge('ticketmaster', 'district');
        // Do it twice to ensure full propagation across 3 nodes
        await performMerge('district', 'bookmyshow');
        await performMerge('bookmyshow', 'ticketmaster');
        
        // Refresh UI
        await fetchSeats();
        
    } catch (error) {
        console.error("Sync failed:", error);
    } finally {
        syncBtn.innerText = 'Sync Databases';
        syncBtn.disabled = false;
    }
}

async function performMerge(source, target) {
    logNetwork(`POST /api/sync ${source} -> ${target}`, 'sync');
    await fetch(`${API_BASE_URL}/sync`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source, target })
    });
}

// Reset all databases
async function resetDatabases() {
    if (!confirm('Are you sure you want to reset all databases? This will clear all bookings.')) return;
    
    const resetBtn = document.getElementById('reset-btn');
    resetBtn.innerText = 'Resetting...';
    resetBtn.disabled = true;
    
    try {
        logNetwork(`POST /api/reset`, 'post');
        await fetch(`${API_BASE_URL}/reset`, {
            method: 'POST'
        });
        // Refresh UI
        await fetchSeats();
    } catch (error) {
        console.error("Reset failed:", error);
        logNetwork(`ERROR: Failed to reset databases`, 'error');
    } finally {
        resetBtn.innerText = 'Reset All';
        resetBtn.disabled = false;
    }
}

// Network Logger
function logNetwork(message, type = 'default') {
    const logList = document.getElementById('log-list');
    const li = document.createElement('li');
    li.className = `log-entry ${type}`;
    
    const time = new Date().toLocaleTimeString();
    li.innerHTML = `<span class="timestamp">[${time}]</span> ${message}`;
    
    logList.appendChild(li);
    // Auto scroll to bottom
    logList.scrollTop = logList.scrollHeight;
}

function clearLog() {
    document.getElementById('log-list').innerHTML = '';
}
