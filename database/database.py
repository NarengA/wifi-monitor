import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "wifi_monitor.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def create_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT NOT NULL,
                mac TEXT UNIQUE NOT NULL,
                first_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS device_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mac TEXT NOT NULL,
                ip TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS traffic_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interface TEXT NOT NULL,
                received_bytes INTEGER NOT NULL,
                sent_bytes INTEGER NOT NULL,
                recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_traffic_recorded_at "
            "ON traffic_logs(recorded_at)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_event_time "
            "ON device_events(event_time)"
        )


def save_device(ip, mac):
    with get_connection() as connection:
        existing = connection.execute(
            "SELECT ip FROM devices WHERE mac = ?", (mac,)
        ).fetchone()

        if existing is None:
            connection.execute(
                "INSERT INTO devices (ip, mac) VALUES (?, ?)", (ip, mac)
            )
            connection.execute(
                "INSERT INTO device_events (mac, ip, event_type) "
                "VALUES (?, ?, 'first_observed')", (mac, ip)
            )
            return "new"

        if existing["ip"] != ip:
            connection.execute(
                "UPDATE devices SET ip = ?, last_seen = CURRENT_TIMESTAMP "
                "WHERE mac = ?", (ip, mac)
            )
            connection.execute(
                "INSERT INTO device_events (mac, ip, event_type) "
                "VALUES (?, ?, 'ip_changed')", (mac, ip)
            )
            return "ip_changed"

        connection.execute(
            "UPDATE devices SET last_seen = CURRENT_TIMESTAMP WHERE mac = ?",
            (mac,)
        )
        return "seen"


def save_traffic(interface, received_bytes, sent_bytes):
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO traffic_logs "
            "(interface, received_bytes, sent_bytes) VALUES (?, ?, ?)",
            (interface, int(received_bytes), int(sent_bytes))
        )


def get_devices():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, ip, mac, first_seen, last_seen "
            "FROM devices ORDER BY last_seen DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def get_traffic_summary(period="day"):
    date_filter = {
        "day": "-1 day",
        "week": "-7 days",
        "month": "-30 days",
    }.get(period, "-1 day")

    with get_connection() as connection:
        row = connection.execute("""
            SELECT COALESCE(SUM(received_bytes), 0) AS received,
                   COALESCE(SUM(sent_bytes), 0) AS sent,
                   COUNT(*) AS samples
            FROM traffic_logs
            WHERE recorded_at >= datetime('now', ?)
        """, (date_filter,)).fetchone()
        return dict(row)


def get_recent_events(limit=30):
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT mac, ip, event_type, event_time "
            "FROM device_events ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(row) for row in rows]
