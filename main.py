from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from database import get_database_info, get_available_dates, get_daily_report_data
from datetime import datetime
import json

app = FastAPI(title="My FastAPI App", version="1.0.1")


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Skyline Cockpit - Crane Operations Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #1a1a1a;
            color: #ffffff;
            overflow-x: hidden;
        }

        .header {
            background-color: #000000;
            padding: 1rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 2px solid #333;
        }

        .logo-container {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .company-name {
            font-size: 1.5rem;
            font-weight: bold;
            color: #00a8ff;
        }

        .date-time {
            font-size: 1rem;
            color: #cccccc;
        }

        .menu-container {
            position: relative;
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .burger-menu {
            background: #333;
            border: 2px solid #555;
            color: #cccccc;
            font-size: 1.8rem;
            cursor: pointer;
            padding: 0.75rem;
            border-radius: 6px;
            transition: all 0.3s ease;
            min-width: 50px;
            text-align: center;
        }

        .burger-menu:hover {
            background-color: #333;
            color: #00a8ff;
        }

        .dropdown-menu {
            position: absolute;
            top: 100%;
            right: 0;
            background: #2d2d2d;
            border: 1px solid #333;
            border-radius: 8px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            min-width: 200px;
            z-index: 1000;
            display: none;
        }

        .dropdown-menu.show {
            display: block;
        }

        .dropdown-item {
            display: block;
            padding: 0.75rem 1rem;
            color: #cccccc;
            text-decoration: none;
            border-bottom: 1px solid #333;
            transition: background-color 0.3s ease;
        }

        .dropdown-item:last-child {
            border-bottom: none;
        }

        .dropdown-item:hover {
            background-color: #333;
            color: #00a8ff;
        }

        .dashboard {
            padding: 2rem;
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            grid-template-rows: auto auto auto;
            gap: 2rem;
            min-height: calc(100vh - 100px);
        }

        .card {
            background: linear-gradient(145deg, #2d2d2d, #252525);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            border: 1px solid #333;
        }

        .card-title {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: #00a8ff;
            text-align: center;
        }

        .stats-grid {
            grid-column: span 3;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }

        .stat-card {
            background: linear-gradient(145deg, #1e3a8a, #1e40af);
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        }

        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: #ffffff;
        }

        .stat-label {
            font-size: 0.9rem;
            color: #cbd5e1;
            margin-top: 0.5rem;
        }

        .breakdown-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem;
            margin: 0.5rem 0;
            background: #333;
            border-radius: 6px;
            border-left: 4px solid #00a8ff;
        }

        .breakdown-label {
            font-weight: 500;
        }

        .breakdown-value {
            font-weight: bold;
            color: #00a8ff;
        }

        .utilization-bar {
            width: 100%;
            height: 20px;
            background: #333;
            border-radius: 10px;
            overflow: hidden;
            margin: 1rem 0;
        }

        .utilization-fill {
            height: 100%;
            background: linear-gradient(90deg, #00a8ff, #0078d4);
            border-radius: 10px;
            width: 78%;
            transition: width 0.5s ease;
        }

        .utilization-text {
            text-align: center;
            font-size: 1.5rem;
            font-weight: bold;
            color: #00a8ff;
            margin-top: 1rem;
        }

        @media (max-width: 768px) {
            .dashboard {
                grid-template-columns: 1fr;
                padding: 1rem;
            }

            .stats-grid {
                grid-column: span 1;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="logo-container">
            <span class="company-name">🏗️ Skyline Cockpit</span>
        </div>
        <div class="menu-container">
            <div class="date-time" id="dateTime">
                Loading...
            </div>
            <button class="burger-menu" id="burgerMenu">☰</button>
            <div class="dropdown-menu" id="dropdownMenu">
                <a href="/docs" target="_blank" class="dropdown-item">📖 API Documentation (Swagger)</a>
                <a href="/redoc" target="_blank" class="dropdown-item">📚 API Documentation (ReDoc)</a>
                <a href="/health" target="_blank" class="dropdown-item">🏥 Health Check</a>
                <a href="/api/available-dates" target="_blank" class="dropdown-item">📅 Available Dates</a>
            </div>
        </div>
    </header>

    <main class="dashboard">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">35,428</div>
                <div class="stat-label">Total Records</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">9:56</div>
                <div class="stat-label">Working Hours</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">7:42</div>
                <div class="stat-label">Utilized Hours</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">78%</div>
                <div class="stat-label">Utilization</div>
            </div>
        </div>

        <div class="card">
            <h3 class="card-title">Daily Utilization</h3>
            <div class="utilization-bar">
                <div class="utilization-fill"></div>
            </div>
            <div class="utilization-text">78%</div>
        </div>

        <div class="card">
            <h3 class="card-title">Weight Distribution</h3>
            <div style="height: 200px; display: flex; align-items: center; justify-content: center; color: #666;">
                Weight Chart Placeholder
            </div>
        </div>

        <div class="card">
            <h3 class="card-title">Time Analysis</h3>
            <div style="height: 200px; display: flex; align-items: center; justify-content: center; color: #666;">
                Time Chart Placeholder
            </div>
        </div>

        <div class="card">
            <h3 class="card-title">Operations Breakdown</h3>
            <div class="breakdown-item">
                <span class="breakdown-label">Moving with Load</span>
                <span class="breakdown-value">02:33 (9,184)</span>
            </div>
            <div class="breakdown-item">
                <span class="breakdown-label">Idle with Load</span>
                <span class="breakdown-value">05:08 (18,536)</span>
            </div>
            <div class="breakdown-item">
                <span class="breakdown-label">Moving without Load</span>
                <span class="breakdown-value">01:07 (4,053)</span>
            </div>
            <div class="breakdown-item">
                <span class="breakdown-label">Idle without Load</span>
                <span class="breakdown-value">01:00 (3,655)</span>
            </div>
        </div>

        <div class="card">
            <h3 class="card-title">Performance Metrics</h3>
            <div class="breakdown-item">
                <span class="breakdown-label">Average Load Weight</span>
                <span class="breakdown-value">790.8 kg</span>
            </div>
            <div class="breakdown-item">
                <span class="breakdown-label">Peak Usage Hour</span>
                <span class="breakdown-value">14:00 - 15:00</span>
            </div>
            <div class="breakdown-item">
                <span class="breakdown-label">Efficiency Score</span>
                <span class="breakdown-value">8.7/10</span>
            </div>
        </div>

        <div class="card">
            <h3 class="card-title">Current Status</h3>
            <div class="breakdown-item">
                <span class="breakdown-label">Crane Status</span>
                <span class="breakdown-value" style="color: #10b981;">Operational</span>
            </div>
            <div class="breakdown-item">
                <span class="breakdown-label">Current Load</span>
                <span class="breakdown-value">1,250 kg</span>
            </div>
            <div class="breakdown-item">
                <span class="breakdown-label">Wind Speed</span>
                <span class="breakdown-value">12 km/h</span>
            </div>
        </div>
    </main>

    <script>
        // Update date and time
        function updateDateTime() {
            const now = new Date();
            const options = {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            };
            document.getElementById('dateTime').textContent = now.toLocaleDateString('en-US', options);
        }

        // Fetch and update dashboard data
        async function fetchDashboardData() {
            try {
                // Get available dates first
                const datesResponse = await fetch('/api/available-dates');
                const datesData = await datesResponse.json();

                if (datesData.dates && datesData.dates.length > 0) {
                    // Use the latest date
                    const latestDate = datesData.dates[datesData.dates.length - 1];

                    // Convert DD/MM/YYYY to YYYY-MM-DD
                    const [day, month, year] = latestDate.split('/');
                    const apiDate = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;

                    // Fetch daily report data
                    const reportResponse = await fetch(`/api/daily-report?date=${apiDate}`);
                    const reportData = await reportResponse.json();

                    // Update dashboard with real data
                    updateDashboard(reportData);
                }
            } catch (error) {
                console.error('Error fetching dashboard data:', error);
            }
        }

        function updateDashboard(data) {
            // Update stats cards
            document.getElementById('totalRecords').textContent = data.total_records?.toLocaleString() || '0';
            document.getElementById('workingHours').textContent = data.daily_stats?.working_hours || '0:00';
            document.getElementById('utilizedHours').textContent = data.daily_stats?.utilized_hours || '0:00';
            document.getElementById('utilizationPercent').textContent = data.daily_stats?.utilization_percent + '%' || '0%';

            // Update utilization bar and display
            const utilization = data.daily_stats?.utilization_percent || 0;
            document.getElementById('utilizationBar').style.width = utilization + '%';
            document.getElementById('utilizationDisplay').textContent = utilization + '%';

            // Update breakdown data
            if (data.breakdown) {
                const breakdownContainer = document.getElementById('breakdownContainer');
                breakdownContainer.innerHTML = `
                    <div class="breakdown-item">
                        <span class="breakdown-label">Moving with Load</span>
                        <span class="breakdown-value">${data.breakdown.moving_with_load.duration} (${data.breakdown.moving_with_load.records.toLocaleString()})</span>
                    </div>
                    <div class="breakdown-item">
                        <span class="breakdown-label">Idle with Load</span>
                        <span class="breakdown-value">${data.breakdown.idle_with_load.duration} (${data.breakdown.idle_with_load.records.toLocaleString()})</span>
                    </div>
                    <div class="breakdown-item">
                        <span class="breakdown-label">Moving without Load</span>
                        <span class="breakdown-value">${data.breakdown.moving_without_load.duration} (${data.breakdown.moving_without_load.records.toLocaleString()})</span>
                    </div>
                    <div class="breakdown-item">
                        <span class="breakdown-label">Idle without Load</span>
                        <span class="breakdown-value">${data.breakdown.idle_without_load.duration} (${data.breakdown.idle_without_load.records.toLocaleString()})</span>
                    </div>
                `;
            }
        }

        // Simulate real-time data updates
        function updateMetrics() {
            // Only do minor variations if we have real data
            fetchDashboardData();
        }

        // Burger menu functionality
        function initBurgerMenu() {
            const burgerMenu = document.getElementById('burgerMenu');
            const dropdownMenu = document.getElementById('dropdownMenu');

            burgerMenu.addEventListener('click', function(e) {
                e.stopPropagation();
                dropdownMenu.classList.toggle('show');
            });

            // Close dropdown when clicking outside
            document.addEventListener('click', function(e) {
                if (!burgerMenu.contains(e.target) && !dropdownMenu.contains(e.target)) {
                    dropdownMenu.classList.remove('show');
                }
            });

            // Close dropdown when pressing Escape
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    dropdownMenu.classList.remove('show');
                }
            });
        }

        // Initialize the dashboard
        function initDashboard() {
            updateDateTime();
            fetchDashboardData();
            initBurgerMenu();
            setInterval(updateDateTime, 1000);
            setInterval(updateMetrics, 30000); // Update every 30 seconds
        }

        // Load dashboard when page is ready
        document.addEventListener('DOMContentLoaded', initDashboard);
    </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)


@app.get("/health")
def health_check():
    db_info = get_database_info()
    return {
        "status": "healthy",
        "database": db_info
    }


@app.get("/api/available-dates")
def get_available_dates_endpoint():
    dates = get_available_dates()
    return {"dates": dates}


@app.get("/api/daily-report")
def get_daily_report(date: str = Query(..., description="Date in YYYY-MM-DD format")):
    try:
        # Validate date format
        datetime.strptime(date, "%Y-%m-%d")

        # Get daily report data
        report_data = get_daily_report_data(date)

        # Return pretty formatted JSON
        return Response(
            content=json.dumps(report_data, indent=4),
            media_type="application/json"
        )

    except ValueError:
        error_data = {
            "error": "Invalid date format. Please use YYYY-MM-DD format",
            "parameter_received": date
        }
        return Response(
            content=json.dumps(error_data, indent=4),
            media_type="application/json"
        )
    except Exception as e:
        error_data = {
            "error": f"Failed to generate daily report: {str(e)}",
            "parameter_received": date
        }
        return Response(
            content=json.dumps(error_data, indent=4),
            media_type="application/json"
        )


@app.get("/users/{user_id}")
def read_user(user_id: int):
    return {"user_id": user_id, "name": f"User {user_id}"}


@app.post("/users")
def create_user(name: str, email: str):
    return {"message": "User created", "name": name, "email": email}


@app.get("/docs-html", response_class=HTMLResponse)
def custom_docs():
    return """
    <html>
        <head>
            <title>FastAPI Docs</title>
        </head>
        <body>
            <h1>Welcome to FastAPI!</h1>
            <p>Visit <a href="/docs">/docs</a> for interactive API documentation</p>
            <p>Visit <a href="/redoc">/redoc</a> for alternative documentation</p>
        </body>
    </html>
    """