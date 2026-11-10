import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'eventsphere.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        role TEXT NOT NULL DEFAULT 'student', -- 'student', 'organizer', 'admin'
        department TEXT NOT NULL,
        year INTEGER NOT NULL DEFAULT 3,
        section TEXT NOT NULL DEFAULT 'B',
        avatar_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Events Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        description TEXT NOT NULL,
        category TEXT NOT NULL, -- 'Technical', 'Cultural', 'Sports', 'Workshop', 'Seminar'
        banner_url TEXT,
        venue TEXT NOT NULL,
        start_time TIMESTAMP NOT NULL,
        end_time TIMESTAMP NOT NULL,
        capacity INTEGER NOT NULL CHECK (capacity > 0),
        organizer_id INTEGER NOT NULL,
        club_name TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'published', -- 'published', 'draft', 'cancelled', 'completed'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (organizer_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')

    # Registrations Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        registration_code TEXT UNIQUE NOT NULL,
        event_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'confirmed', -- 'confirmed', 'waitlisted', 'cancelled', 'attended'
        qr_token TEXT UNIQUE NOT NULL,
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        cancelled_at TIMESTAMP,
        attended_at TIMESTAMP,
        checkin_by INTEGER,
        FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (checkin_by) REFERENCES users (id),
        UNIQUE(event_id, user_id, status) -- Prevents active duplicates
    )
    ''')

    # Waitlist Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS waitlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT NOT NULL DEFAULT 'waiting', -- 'waiting', 'offered', 'claimed', 'expired'
        offer_expires_at TIMESTAMP,
        FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        UNIQUE(event_id, user_id)
    )
    ''')

    # Attendance Logs Table (Auditable check-in trail)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        registration_id INTEGER,
        user_id INTEGER,
        scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        scanned_by INTEGER,
        verification_status TEXT NOT NULL, -- 'valid', 'duplicate_rejected', 'invalid', 'cancelled'
        message TEXT NOT NULL,
        FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE CASCADE,
        FOREIGN KEY (registration_id) REFERENCES registrations (id) ON DELETE SET NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL,
        FOREIGN KEY (scanned_by) REFERENCES users (id)
    )
    ''')

    # Event Passport Stamps Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS passport_stamps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        event_id INTEGER NOT NULL,
        stamp_title TEXT NOT NULL,
        stamp_category TEXT NOT NULL,
        club_name TEXT NOT NULL,
        venue TEXT NOT NULL,
        event_date TIMESTAMP NOT NULL,
        badge_level TEXT NOT NULL DEFAULT 'Standard', -- 'Standard', 'Silver', 'Gold', 'Distinction'
        awarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE CASCADE,
        UNIQUE(user_id, event_id)
    )
    ''')

    conn.commit()
    conn.close()
    print(f"EventSphere database initialized at: {DB_PATH}")

if __name__ == '__main__':
    init_db()

