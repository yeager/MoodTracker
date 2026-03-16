"""SQLite-databas för emotionell data."""

import sqlite3
import os
import csv
from datetime import datetime, timedelta
from pathlib import Path


def get_db_path():
    """Returnera sökväg till databasen."""
    data_dir = Path(os.environ.get(
        "XDG_DATA_HOME", Path.home() / ".local" / "share"
    )) / "moodtracker"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "moods.db"


class MoodDatabase:
    """Hanterar all databasinteraktion för stämningsdata."""

    MOODS = {
        "happy": {"emoji": "😊", "label_sv": "Glad", "label_en": "Happy", "value": 5},
        "good": {"emoji": "🙂", "label_sv": "Bra", "label_en": "Good", "value": 4},
        "neutral": {"emoji": "😐", "label_sv": "Neutral", "label_en": "Neutral", "value": 3},
        "sad": {"emoji": "😢", "label_sv": "Ledsen", "label_en": "Sad", "value": 2},
        "angry": {"emoji": "😠", "label_sv": "Arg", "label_en": "Angry", "value": 1},
        "anxious": {"emoji": "😰", "label_sv": "Orolig", "label_en": "Anxious", "value": 2},
        "tired": {"emoji": "😴", "label_sv": "Trött", "label_en": "Tired", "value": 2},
        "loved": {"emoji": "🥰", "label_sv": "Älskad", "label_en": "Loved", "value": 5},
    }

    def __init__(self, db_path=None):
        self.db_path = db_path or get_db_path()
        self._init_db()

    def _init_db(self):
        """Skapa tabeller om de inte finns."""
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mood_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    date TEXT NOT NULL,
                    mood_key TEXT NOT NULL,
                    emoji TEXT NOT NULL,
                    mood_value INTEGER NOT NULL,
                    note TEXT DEFAULT ''
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_date ON mood_entries(date)
            """)

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def add_entry(self, mood_key, note=""):
        """Lägg till en stämningsregistrering."""
        mood = self.MOODS[mood_key]
        now = datetime.now()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO mood_entries (timestamp, date, mood_key, emoji, mood_value, note) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    now.isoformat(),
                    now.strftime("%Y-%m-%d"),
                    mood_key,
                    mood["emoji"],
                    mood["value"],
                    note,
                ),
            )

    def get_today_entries(self):
        """Hämta dagens registreringar."""
        today = datetime.now().strftime("%Y-%m-%d")
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            return conn.execute(
                "SELECT * FROM mood_entries WHERE date = ? ORDER BY timestamp DESC",
                (today,),
            ).fetchall()

    def get_entries_range(self, days=30):
        """Hämta registreringar för ett antal dagar bakåt."""
        start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            return conn.execute(
                "SELECT * FROM mood_entries WHERE date >= ? ORDER BY date, timestamp",
                (start,),
            ).fetchall()

    def get_all_entries(self):
        """Hämta alla registreringar."""
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            return conn.execute(
                "SELECT * FROM mood_entries ORDER BY date, timestamp"
            ).fetchall()

    def get_daily_averages(self, days=30):
        """Beräkna dagliga medelvärden."""
        start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            return conn.execute(
                "SELECT date, AVG(mood_value) as avg_mood, COUNT(*) as count "
                "FROM mood_entries WHERE date >= ? GROUP BY date ORDER BY date",
                (start,),
            ).fetchall()

    def export_csv(self, filepath):
        """Exportera all data till CSV för psykolog/BUP."""
        entries = self.get_all_entries()
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Datum", "Tid", "Känsla", "Emoji", "Värde (1-5)", "Anteckning"
            ])
            for entry in entries:
                ts = datetime.fromisoformat(entry["timestamp"])
                writer.writerow([
                    entry["date"],
                    ts.strftime("%H:%M"),
                    entry["mood_key"],
                    entry["emoji"],
                    entry["mood_value"],
                    entry["note"],
                ])
        return filepath

    def delete_entry(self, entry_id):
        """Ta bort en registrering."""
        with self._connect() as conn:
            conn.execute("DELETE FROM mood_entries WHERE id = ?", (entry_id,))
