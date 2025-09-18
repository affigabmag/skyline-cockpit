from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from database import get_database_info, get_available_dates, get_daily_report_data
from datetime import datetime
import json

app = FastAPI(title="My FastAPI App", version="1.0.1")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/report", response_class=HTMLResponse)
def get_report():
    dates = get_available_dates()

    report_html = ""
    if dates:
        day, month, year = dates[0].split('/')
        api_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        report_data = get_daily_report_data(api_date)

        report_html = f"""
        <h2>Report for {dates[0]}</h2>
        <p><strong>Total Records:</strong> {report_data['total_records']:,}</p>
        <p><strong>Working Hours:</strong> {report_data['daily_stats']['working_hours']}</p>
        <p><strong>Utilized Hours:</strong> {report_data['daily_stats']['utilized_hours']}</p>
        <p><strong>Utilization:</strong> {report_data['daily_stats']['utilization_percent']}%</p>
        <h3>Operations Breakdown:</h3>
        <p><strong>Moving with Load:</strong> {report_data['breakdown']['moving_with_load']['duration']} ({report_data['breakdown']['moving_with_load']['records']:,} records)</p>
        <p><strong>Idle with Load:</strong> {report_data['breakdown']['idle_with_load']['duration']} ({report_data['breakdown']['idle_with_load']['records']:,} records)</p>
        <p><strong>Moving without Load:</strong> {report_data['breakdown']['moving_without_load']['duration']} ({report_data['breakdown']['moving_without_load']['records']:,} records)</p>
        <p><strong>Idle without Load:</strong> {report_data['breakdown']['idle_without_load']['duration']} ({report_data['breakdown']['idle_without_load']['records']:,} records)</p>
        """

    options_html = ""
    for date in dates:
        options_html += f'<option value="{date}">{date}</option>'

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Skyline Cockpit</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background: #1a1a1a; color: white; }}
        .header {{ background: #000; padding: 1rem 2rem; border-bottom: 2px solid #333; text-align: center; position: relative; }}
        .company-name {{ font-size: 1.5rem; font-weight: bold; color: #00a8ff; position: absolute; left: 2rem; top: 50%; transform: translateY(-50%); }}
        .header-center {{ display: inline-block; }}
        .report-title {{ font-size: 1.2rem; font-weight: bold; }}
        .date-dropdown {{ background: #333; border: 1px solid #555; color: white; padding: 0.5rem 1rem; border-radius: 4px; }}
        .main-content {{ padding: 2rem; }}
        .report-results {{ background: #2d2d2d; padding: 2rem; border-radius: 8px; }}
        h2 {{ color: #00a8ff; margin-bottom: 1rem; }}
        h3 {{ color: #00a8ff; margin: 1rem 0 0.5rem 0; }}
        p {{ margin-bottom: 0.5rem; }}
    </style>
</head>
<body>
    <header class="header">
        <span class="company-name">🏗️ Skyline Cockpit</span>
        <div class="header-center">
            <span class="report-title">Daily Crane Report</span>
            <select class="date-dropdown">{options_html}</select>
        </div>
    </header>
    <main class="main-content">
        <div class="report-results">{report_html}</div>
    </main>
</body>
</html>"""
    return HTMLResponse(content=html)

@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    try:
        with open("templates/dashboard.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error loading dashboard</h1><p>{str(e)}</p>", status_code=500)

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
        datetime.strptime(date, "%Y-%m-%d")
        report_data = get_daily_report_data(date)
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