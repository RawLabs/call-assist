import os
import sqlite3
import json
from datetime import datetime
from state.call_state import CallState

class CallDatabase:
    def __init__(self, db_path: str = "calls.db"):
        self.db_path = db_path
        self._conn = None
        if db_path == ":memory:":
            # Keep a persistent connection so in-memory DB is not destroyed
            self._conn = sqlite3.connect(db_path)
        self._init_db()

    def _connect(self):
        if self._conn:
            return self._conn
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initializes the SQLite database and creates the calls table if it doesn't exist."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                caller_name TEXT,
                callback_number TEXT,
                intent TEXT,
                final_route TEXT,
                state_json TEXT,
                transcript TEXT,
                summary TEXT
            )
        """)
        conn.commit()
        if self.db_path != ":memory:":
            conn.close()

    def save_call(self, state: CallState, transcript: list, summary: str):
        """
        Saves a completed call session.
        transcript is a list of dicts: [{"sender": "caller"|"assistant", "text": "..."}]
        """
        conn = self._connect()
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        state_json = json.dumps(state.model_dump())
        transcript_json = json.dumps(transcript)

        cursor.execute("""
            INSERT INTO calls (
                timestamp, caller_name, callback_number, intent, final_route, state_json, transcript, summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            state.caller_name,
            state.callback_number,
            state.intent,
            state.department,
            state_json,
            transcript_json,
            summary
        ))
        
        # Don't close connection for in-memory database
        if self.db_path != ":memory:":
            conn.commit()
            conn.close()
        else:
            conn.commit()

    def get_all_calls(self) -> list:
        """Retrieves all logged calls."""
        conn = self._connect()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM calls ORDER BY id DESC")
        rows = cursor.fetchall()
        
        calls = []
        for row in rows:
            calls.append({
                "id": row["id"],
                "timestamp": row["timestamp"],
                "caller_name": row["caller_name"],
                "callback_number": row["callback_number"],
                "intent": row["intent"],
                "final_route": row["final_route"],
                "state_json": json.loads(row["state_json"]),
                "transcript": json.loads(row["transcript"]),
                "summary": row["summary"]
            })
        if self.db_path != ":memory:":
            conn.close()
        return calls
