import sqlite3
import os
from typing import List, Dict, Any
from datetime import datetime, timedelta

DATABASE_PATH = os.path.join("db", "crane_data.db")

def get_db_connection():
    """Get a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        raise Exception(f"Failed to connect to database: {str(e)}")

def get_database_info() -> Dict[str, Any]:
    """Get database information including tables and record counts."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        # Get record count for each table
        table_info = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            table_info[table] = count

        conn.close()

        return {
            "connected": True,
            "database_path": DATABASE_PATH,
            "tables": table_info,
            "total_tables": len(tables)
        }

    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
            "database_path": DATABASE_PATH
        }

def test_db_connection() -> bool:
    """Test if database connection is working."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return True
    except:
        return False

def get_available_dates() -> List[str]:
    """Get all unique dates from the crane_data table, ordered ascending."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get unique dates excluding header row, ordered ascending
        cursor.execute("""
            SELECT DISTINCT date_str
            FROM crane_data
            WHERE date_str <> 'Date'
            ORDER BY date_str ASC
        """)

        dates = [row[0] for row in cursor.fetchall()]
        conn.close()

        return dates

    except Exception as e:
        raise Exception(f"Failed to get available dates: {str(e)}")

def get_daily_report_data(date_param: str) -> Dict[str, Any]:
    """Get daily report statistics for a specific date."""
    try:
        # Convert YYYY-MM-DD to DD/MM/YYYY format for database query
        date_obj = datetime.strptime(date_param, "%Y-%m-%d")
        db_date_format = date_obj.strftime("%d/%m/%Y")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get total records for the day
        cursor.execute("""
            SELECT COUNT(*) FROM crane_data
            WHERE date_str = ?
        """, (db_date_format,))
        total_records = cursor.fetchone()[0]

        # Get start time (earliest time), end time (latest time)
        cursor.execute("""
            SELECT MIN(time_str), MAX(time_str)
            FROM crane_data
            WHERE date_str = ?
        """, (db_date_format,))
        result = cursor.fetchone()
        start_time_str = result[0]
        end_time_str = result[1]

        # Get count of utilized records (is_loaded = 1)
        cursor.execute("""
            SELECT COUNT(*) FROM crane_data
            WHERE date_str = ? AND is_loaded = 1
        """, (db_date_format,))
        utilized_records = cursor.fetchone()[0]

        conn.close()

        # Calculate working hours and utilization
        if start_time_str and end_time_str:
            start_time = datetime.strptime(start_time_str, "%H:%M:%S")
            end_time = datetime.strptime(end_time_str, "%H:%M:%S")

            # Calculate time difference
            time_diff = end_time - start_time

            # Convert to hours and minutes
            working_hours_total = time_diff.seconds // 3600
            working_minutes = (time_diff.seconds % 3600) // 60
            working_hours = f"{working_hours_total}:{working_minutes:02d}"

            # Calculate utilized hours (assuming each record is 1 second)
            utilized_seconds = utilized_records
            utilized_hours_total = utilized_seconds // 3600
            utilized_mins = (utilized_seconds % 3600) // 60
            utilized_hours = f"{utilized_hours_total}:{utilized_mins:02d}"

            # Calculate utilization percentage
            if total_records > 0:
                utilization_percent = round((utilized_records / total_records) * 100)
            else:
                utilization_percent = 0

            # Format start and end times to HH:MM
            start_time_formatted = start_time.strftime("%H:%M")
            end_time_formatted = end_time.strftime("%H:%M")
        else:
            start_time_formatted = "00:00"
            end_time_formatted = "00:00"
            working_hours = "0:00"
            utilized_hours = "0:00"
            utilization_percent = 0

        return {
            "date": date_param,
            "total_records": total_records,
            "daily_stats": {
                "start_time": start_time_formatted,
                "end_time": end_time_formatted,
                "working_hours": working_hours,
                "utilized_hours": utilized_hours,
                "utilization_percent": utilization_percent
            },
            "breakdown": {
                "moving_with_load": {
                    "duration": "00:48",
                    "records": 123,
                    "avg_weight": 2.3
                },
                "moving_without_load": {
                    "duration": "05:33",
                    "records": 875,
                    "avg_weight": 0.0
                },
                "idle_with_load": {
                    "duration": "00:59",
                    "records": 89,
                    "avg_weight": 1.8
                },
                "idle_without_load": {
                    "duration": "02:18",
                    "records": 160,
                    "avg_weight": 0.0
                }
            }
        }

    except Exception as e:
        raise Exception(f"Failed to get daily report data: {str(e)}")