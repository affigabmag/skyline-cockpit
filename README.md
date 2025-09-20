# Skyline Cockpit - Crane Operations Dashboard


<img width="1350" height="1015" alt="skyline-cockpit onrender com_dashboard" src="https://github.com/user-attachments/assets/f4ba63e1-ec5b-4c42-9183-9cdd6915dfa3" />

## 🚀 **[Live Demo - Experience it here!](https://skyline-cockpit.onrender.com/dashboard)**

Hosted on Render.com free tier.

> [!WARNING]
> **It might take few minutes for the app to wake up due to using a free hosting plan on render.com.**

## Table of Contents

- [Overview](#overview)
- [Directory Structure](#directory-structure)
- [Technologies Used](#technologies-used)
  - [Backend Framework](#backend-framework)
  - [Database](#database)
  - [Frontend](#frontend)
- [Database Schema](#database-schema)
- [API Documentation](#api-documentation)
  - [Base URL](#base-url)
  - [Endpoints](#endpoints)
- [Installation and Setup](#installation-and-setup)
  - [Prerequisites](#prerequisites)
  - [Step-by-Step Installation](#step-by-step-installation)
- [Accessing the Dashboard](#accessing-the-dashboard)
  - [Main Dashboard](#main-dashboard)
  - [Dashboard Components](#dashboard-components)
- [API Usage Examples](#api-usage-examples)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Overview

Skyline Cockpit is an interactive web dashboard for monitoring and managing crane operations. The system provides real-time visualization of operational data, utilization metrics, and detailed statistics.

## Directory Structure

```
skyline-cockpit/
+-- acc/
|   +-- doc_consolidated.ps1 (25.16 KB)
+-- db/
|   +-- crane_data.db (7660 KB)
|   |       Table: crane_data
|   |           Rows: 35429
|   |           datetime_str : TEXT
|   |           utc_time : TEXT
|   |           date_str : TEXT
|   |           time_str : TEXT
|   |           position_x : REAL
|   |           position_y : REAL
|   |           position_z : REAL
|   |           slew : REAL
|   |           jib : REAL
|   |           hoist : REAL
|   |           weight : REAL
|   |           wind : REAL
|   |           cable_weight : REAL
|   |           seconds : INTEGER
|   |           controller_is_moving : INTEGER
|   |           controller_direction : INTEGER
|   |           controller_g2 : INTEGER
|   |           controller_g3 : INTEGER
|   |           is_prev : TEXT
|   |           weight_rounded : REAL
|   |           weight_fixed : REAL
|   |           weight_smooth : REAL
|   |           weight_by_controller_direction : REAL
|   |           is_moving : INTEGER
|   |           is_loaded : INTEGER
|   |           state : TEXT
|   |           state_grouping : REAL
|   |           grouping_lifting_events : REAL
|   |           grouping_moving_events : REAL
|   +-- create_db.sql (0.68 KB)
|   +-- sample_data.csv (9808.97 KB)
+-- static/
|   +-- dashboard.css (4.73 KB)
|   +-- dashboard.js (6.57 KB)
+-- templates/
|   +-- dashboard.html (3.74 KB)
+-- .gitignore (4.78 KB)
+-- database.py (7.75 KB)
|           import sqlite3
|           import os
|           from typing import List, Dict, Any
|           from datetime import datetime, timedelta
|   
|           def get_db_connection()
|               '''Get a connection to the SQLite database.'''
|           # Constants:
|           DATABASE_PATH
+-- LICENSE (1.07 KB)
+-- main.py (5.74 KB)
|           from fastapi import FastAPI, Query
|           from fastapi.responses import HTMLResponse, Response
|           from fastapi.staticfiles import StaticFiles
|           from database import get_database_info, get_available_dates, get_daily_report_data
|           from datetime import datetime
|           import json
|   
|           def read_root()
|           def get_report()
|           def get_dashboard()
|           def health_check()
|           def get_available_dates_endpoint()
|           def read_user()
|           def create_user()
|           def custom_docs()
+-- README.md (9.74 KB)
+-- requirements.txt (0.06 KB)
            # Python Dependencies:
            fastapi==0.116.2
            uvicorn[standard]==0.35.0
            sqlalchemy==2.0.43
```

## Technologies Used

### Backend Framework
- **FastAPI** - Modern, high-performance web framework for Python
  - Chosen for automatic API documentation generation (Swagger/OpenAPI)
  - Built-in request/response validation with type hints
  - High performance comparable to Node.js and Go
  - Native async/await support

### Database
- **SQLite** - Lightweight, serverless database
  - No separate database server required
  - Perfect for single-application deployment
  - ACID-compliant with excellent performance for read-heavy workloads
  - Easy backup and portability

### Frontend
- **HTML5** - Modern semantic markup
- **CSS3** - Custom styling with flexbox and grid layouts
- **JavaScript (ES6+)** - Modern JavaScript with async/await
- **Chart.js** - Professional chart library for data visualization

## Database Schema

### Table: `crane_data`

| Column | Type | Description |
|--------|------|-------------|
| `datetime_str` | TEXT | Full datetime string |
| `utc_time` | TEXT | UTC timestamp |
| `date_str` | TEXT | Date in DD/MM/YYYY format |
| `time_str` | TEXT | Time in HH:MM:SS format |
| `position_x` | REAL | X coordinate position |
| `position_y` | REAL | Y coordinate position |
| `position_z` | REAL | Z coordinate position |
| `slew` | REAL | Slew angle |
| `jib` | REAL | Jib position |
| `hoist` | REAL | Hoist position |
| `weight` | REAL | Current weight reading |
| `wind` | REAL | Wind speed |
| `cable_weight` | REAL | Cable weight |
| `seconds` | INTEGER | Seconds counter |
| `controller_is_moving` | INTEGER | Controller movement flag |
| `controller_direction` | INTEGER | Movement direction |
| `controller_g2` | INTEGER | Controller G2 state |
| `controller_g3` | INTEGER | Controller G3 state |
| `is_prev` | TEXT | Previous state flag |
| `weight_rounded` | REAL | Rounded weight value |
| `weight_fixed` | REAL | Fixed weight calculation |
| `weight_smooth` | REAL | Smoothed weight value |
| `weight_by_controller_direction` | REAL | Weight by direction |
| `is_moving` | INTEGER | Movement status (0/1) |
| `is_loaded` | INTEGER | Load status (0/1) |
| `state` | TEXT | Current operational state |
| `state_grouping` | REAL | State grouping value |
| `grouping_lifting_events` | REAL | Lifting event grouping |
| `grouping_moving_events` | REAL | Moving event grouping |

**Sample Data**: ~35,000 records with timestamps from crane operations

## API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Health Check
```http
GET /health
```
**Response:**
```json
{
    "status": "healthy",
    "database": {
        "connected": true,
        "database_path": "db/crane_data.db",
        "tables": {
            "crane_data": 35429
        },
        "total_tables": 1
    }
}
```

#### 2. Available Dates
```http
GET /api/available-dates
```
**Description:** Get all unique dates with crane data
**Response:**
```json
{
    "dates": ["04/02/2025", "30/05/2025"]
}
```

#### 3. Daily Report
```http
GET /api/daily-report?date=YYYY-MM-DD
```
**Parameters:**
- `date` (required): Date in YYYY-MM-DD format

**Response:**
```json
{
    "date": "2025-05-30",
    "total_records": 28800,
    "daily_stats": {
        "start_time": "05:57",
        "end_time": "15:54",
        "working_hours": "9:56",
        "utilized_hours": "7:42",
        "utilization_percent": 78
    },
    "breakdown": {
        "moving_with_load": {
            "duration": "02:33",
            "records": 9180,
            "avg_weight": 15.6
        },
        "moving_without_load": {
            "duration": "01:07", 
            "records": 4020,
            "avg_weight": 0.0
        },
        "idle_with_load": {
            "duration": "05:08",
            "records": 18480,
            "avg_weight": 12.8
        },
        "idle_without_load": {
            "duration": "01:00",
            "records": 3600,
            "avg_weight": 0.0
        }
    }
}
```

#### 4. Dashboard
```http
GET /dashboard
```
**Description:** Main dashboard interface
**Response:** HTML dashboard page

#### 5. Interactive API Documentation
```http
GET /docs          # Swagger UI
GET /redoc         # ReDoc documentation
```

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd skyline-cockpit
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Verify Database
Ensure the database file exists:
```bash
ls db/crane_data.db
```

### Step 5: Run Application
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 6: Verify Installation
Open browser and navigate to:
- Dashboard: http://localhost:8000/dashboard
- API Health: http://localhost:8000/health
- API Documentation: http://localhost:8000/docs

## Accessing the Dashboard

### Main Dashboard
**URL:** `http://localhost:8000/dashboard`

**Features:**
- Real-time crane utilization gauge
- Daily operational statistics (start time, end time, working hours)
- Utilization breakdown by operation type
- Date selector for historical data
- API menu for direct endpoint access

<img width="1334" height="852" alt="image" src="https://github.com/user-attachments/assets/a184f597-1b26-44f5-9137-19b6690925bd" />

### Dashboard Components

1. **Logo and Navigation**
   - Skyline Cockpit branding (top-left)
   - API hamburger menu (top-right)

2. **Date Selection**
   - Dropdown populated from available dates API
   - Automatic loading of latest date on page load

3. **Statistics Cards**
   - Start Time, End Time, Working Hours, Utilized Hours
   - Real-time updates based on selected date

4. **Utilization Gauge**
   - Interactive semicircle chart using Chart.js
   - Visual representation of crane utilization percentage

5. **Operation Breakdown**
   - Moving with Load, Moving without Load
   - Idle with Load, Idle without Load
   - Duration and average weight for each category

## API Usage Examples

### Get Available Dates
```bash
curl http://localhost:8000/api/available-dates
```

### Get Daily Report
```bash
curl "http://localhost:8000/api/daily-report?date=2025-05-30"
```

### Health Check
```bash
curl http://localhost:8000/health
```

## Development

### Adding New Features
1. API endpoints: Add to `main.py`
2. Database queries: Add to `database.py`
3. Frontend: Modify `templates/dashboard.html` and `static/` files

### Database Queries
The application uses raw SQL queries for optimal performance:
- Date filtering with proper format conversion
- Aggregation functions for statistics
- Time-based calculations for durations

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify `db/crane_data.db` exists
   - Check file permissions

2. **Chart Not Displaying**
   - Ensure Chart.js CDN is accessible
   - Check browser console for JavaScript errors

3. **API Endpoints Not Working**
   - Verify server is running on correct port
   - Check FastAPI logs for errors

### Logs
Server logs are displayed in the terminal where you run the uvicorn command.

## License

This project is licensed under the MIT License.
