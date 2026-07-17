# TrinityTix 🎟️

**🚀 [Live Deployment Demo](https://trinitytixlive.vercel.app/)**


TrinityTix is a full-stack ticket booking system designed to demonstrate **Eventual Consistency** across three heterogeneous database systems: **SQLite**, **Redis**, and **MongoDB**. 

The project simulates three distinct ticketing applications (District, BookMyShow, and Ticketmaster) attempting to synchronize their internal states in a distributed-like architecture.

---

## 🌟 Key Features

- **Triple Database Syncing:** Modifying data in one app seamlessly synchronizes with the others using an Operation Log (Oplog) mechanism.
- **Priority-Based Conflict Resolution:**
  - `Booked` operations override `Held` operations across all databases.
  - Conflicts between identical states (e.g., both systems holding a seat simultaneously) are resolved using strict **First-Come-First-Served (FCFS)** logic via precise timestamping.
- **Global Color Coding:** The frontend dynamically tracks the `origin_app` of a booking. If a seat is booked on BookMyShow, it turns Red across the Ticketmaster and District UI as well.
- **Responsive Premium UI:** Vanilla HTML/CSS/JS frontend styled with a modern glassmorphism aesthetic, sleek black and gold theme, and a completely fluid layout scaling gracefully on small laptops without scrolling or wrapping.
- **Network Logger Drawer:** An integrated frontend dashboard panel visibly logs all REST API operations in real-time, matching backend interactions.
- **Custom Assets & GitHub Integration:** Includes a completely custom-built SVG favicon for branding and an integrated floating GitHub link mirroring the app's aesthetic.

---

## 🏗️ Architecture

### Backend (Python + FastAPI)
- Designed with modularity using an abstract base class (`TicketDBManager`).
- Exposes a REST API for reading states, writing states, and executing database merges.
- Supported Databases:
  1. **SQLite (District):** A lightweight, zero-configuration SQL database.
  2. **Redis (BookMyShow):** An in-memory, blazing fast NoSQL Key-Value store.
  3. **MongoDB (Ticketmaster):** A robust NoSQL Document database.

### Frontend (Vanilla HTML/CSS/JS)
- Zero build steps required—just open `index.html`.
- Implements optimistic UI updates for instant feedback while handling backend fallbacks on failure.
- Uses dynamic `clamp` sizes and Flexbox properties for a perfectly fluid, auto-sizing grid.

---

## 🚀 Getting Started

### Prerequisites
To run this project locally, you need:
- **Python 3.8+**
- **Redis** running on the default port (`6379`)
- **MongoDB** running on the default port (`27017`)

### 1. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd src/backend
   ```
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the FastAPI development server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### 2. Frontend Setup

1. Locate `src/frontend/index.html`.
2. Open it in your web browser. (Alternatively, use an extension like VS Code Live Server).

---

## 🧪 Testing the Sync Logic

1. **Interact:** Click a seat on the *BookMyShow* screen to "Hold" it (Turns Red-Pink). Notice the POST request in the Network Logger.
2. **Double Interact:** Quickly click the *same* seat on the *Ticketmaster* screen to "Hold" it (Turns Light Blue).
3. **Sync:** Click the **Sync Databases** button at the top.
4. **Result:** The system will sync the oplogs across all databases. Since BookMyShow held it *first*, its timestamp wins. The seat will globally turn Red across all three screens!
5. **Priority:** Now, click the seat on Ticketmaster again to fully **Book** it (Turns Dark Blue). Click Sync. Because Booking priority > Holding priority, Ticketmaster will overwrite BookMyShow's hold, and the seat becomes Dark Blue globally.

---

## ☁️ Live Demo & Hosting

If you wish to host this project publicly for free:
1. **Frontend:** Deployed via [Vercel](https://trinitytixlive.vercel.app). 
2. **Backend & Redis:** Create a free Web Service and a free Redis instance on [Render](https://render.com). Point the web service to your `src/backend` folder.
3. **MongoDB:** Sign up for a free M0 Cluster on [MongoDB Atlas](https://mongodb.com/atlas).

---
*Created as a demonstration of NoSQL concepts and eventual consistency data synchronization.*
