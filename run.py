#!/usr/bin/env python3
"""
EventSphere - Full Stack Web Application Launcher
Team 19 | CSE-B
G Srija Santoshini (1602-24-733-117)
Siddheeshwar CH (1602-24-733-114)
E Keerthi Teja (1602-24-733-081)
"""

import os
import sys

# Automatically set working directory to project folder
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)

backend_dir = os.path.join(PROJECT_ROOT, 'backend')
sys.path.insert(0, backend_dir)

from database import init_db
from seed_data import seed_database
from app import app

if __name__ == '__main__':
    db_file = os.path.join(backend_dir, 'eventsphere.db')
    if not os.path.exists(db_file):
        print("Database not found. Initializing and seeding initial demo data...")
        seed_database()
    else:
        init_db()

    port = int(os.environ.get('PORT', 5050))
    print("=" * 65)
    print("  🚀 EventSphere - Discover. Register. Connect.")
    print("  Team 19 | CSE-B | FSWD Course-Based Project")
    print(f"  Access Full Stack Web Portal at: http://127.0.0.1:{port}")
    print("=" * 65)
    app.run(host='0.0.0.0', port=port, debug=True)
