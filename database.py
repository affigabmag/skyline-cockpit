import sqlite3
import os
from typing import List, Dict, Any

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