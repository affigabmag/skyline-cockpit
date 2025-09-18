from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from database import get_database_info, get_available_dates, get_daily_report_data
from datetime import datetime

app = FastAPI(title="My FastAPI App", version="1.0.1")


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


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
        return report_data

    except ValueError:
        return {
            "error": "Invalid date format. Please use YYYY-MM-DD format",
            "parameter_received": date
        }
    except Exception as e:
        return {
            "error": f"Failed to generate daily report: {str(e)}",
            "parameter_received": date
        }


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