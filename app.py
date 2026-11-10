import os
import sys

# Ensure current working directory is backend directory
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BACKEND_DIR)
sys.path.insert(0, BACKEND_DIR)

import re
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import get_db, init_db
from models import (
    get_all_events, get_event_by_id, register_user_for_event,
    join_waitlist, cancel_registration, claim_waitlist_offer,
    verify_and_checkin_pass, get_user_passport, get_user_registrations,
    get_organizer_analytics, get_event_attendees, get_event_seat_pulse,
    check_schedule_clash
)
from seed_data import seed_database
from qr_service import generate_qr_image_base64

FRONTEND_DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'dist')

app = Flask(__name__, static_folder=FRONTEND_DIST if os.path.exists(FRONTEND_DIST) else None)
CORS(app)

# ----------------- System & Health -----------------

@app.route('/api/docs', methods=['GET'])
def api_docs():
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    return send_from_directory(templates_dir, 'api_docs.html')

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "EventSphere API Server",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.route('/api/reset-demo', methods=['POST'])
def reset_demo():
    seed_database()
    return jsonify({"success": True, "message": "EventSphere database reset and seeded with initial demo data!"})

# ----------------- User Profiles -----------------

@app.route('/api/users', methods=['GET'])
def list_users():
    db = get_db()
    users = db.execute("SELECT id, roll_no, name, email, role, department, section, avatar_url FROM users ORDER BY role DESC, id ASC").fetchall()
    db.close()
    return jsonify([dict(u) for u in users])

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    db.close()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(dict(user))

@app.route('/api/users/<int:user_id>/registrations', methods=['GET'])
def user_registrations(user_id):
    data = get_user_registrations(user_id)
    return jsonify(data)

@app.route('/api/users/<int:user_id>/passport', methods=['GET'])
def user_passport(user_id):
    passport = get_user_passport(user_id)
    if not passport:
        return jsonify({"error": "User not found"}), 404
    return jsonify(passport)

# ----------------- Events & Live Seat Pulse -----------------

@app.route('/api/events', methods=['GET'])
def list_events():
    category = request.args.get('category')
    search = request.args.get('search')
    user_id = request.args.get('user_id', type=int)
    events = get_all_events(category=category, search=search, user_id=user_id)
    return jsonify(events)

@app.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    user_id = request.args.get('user_id', type=int)
    event = get_event_by_id(event_id, user_id=user_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404
    return jsonify(event)

@app.route('/api/events/<int:event_id>/seat-pulse', methods=['GET'])
def event_seat_pulse(event_id):
    pulse = get_event_seat_pulse(event_id)
    if not pulse:
        return jsonify({"error": "Event not found"}), 404
    return jsonify(pulse)

@app.route('/api/events', methods=['POST'])
def create_event():
    data = request.get_json() or {}
    title = data.get('title')
    description = data.get('description')
    category = data.get('category', 'Technical')
    venue = data.get('venue')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    capacity = int(data.get('capacity', 50))
    club_name = data.get('club_name', 'Campus Event Club')
    banner_url = data.get('banner_url') or 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800'
    organizer_id = int(data.get('organizer_id', 1))

    if not title or not description or not venue or not start_time or not end_time or capacity <= 0:
        return jsonify({"error": "Missing required fields or invalid capacity"}), 400

    slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-') + f"-{int(datetime.now().timestamp()) % 10000}"

    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO events (title, slug, description, category, banner_url, venue, start_time, end_time, capacity, organizer_id, club_name, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'published')
    """, (title, slug, description, category, banner_url, venue, start_time, end_time, capacity, organizer_id, club_name))
    
    event_id = cursor.lastrowid
    db.commit()
    db.close()

    created_event = get_event_by_id(event_id)
    return jsonify(created_event), 201

@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    data = request.get_json() or {}
    db = get_db()
    cursor = db.cursor()

    existing = cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    if not existing:
        db.close()
        return jsonify({"error": "Event not found"}), 404

    title = data.get('title', existing['title'])
    description = data.get('description', existing['description'])
    category = data.get('category', existing['category'])
    venue = data.get('venue', existing['venue'])
    start_time = data.get('start_time', existing['start_time'])
    end_time = data.get('end_time', existing['end_time'])
    capacity = int(data.get('capacity', existing['capacity']))
    club_name = data.get('club_name', existing['club_name'])
    banner_url = data.get('banner_url', existing['banner_url'])
    status = data.get('status', existing['status'])

    cursor.execute("""
        UPDATE events 
        SET title = ?, description = ?, category = ?, venue = ?, 
            start_time = ?, end_time = ?, capacity = ?, club_name = ?, 
            banner_url = ?, status = ?
        WHERE id = ?
    """, (title, description, category, venue, start_time, end_time, capacity, club_name, banner_url, status, event_id))

    db.commit()
    db.close()

    updated = get_event_by_id(event_id)
    return jsonify(updated)

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
    db.commit()
    db.close()
    return jsonify({"success": True, "message": "Event deleted successfully"})

# ----------------- Registration, Waitlist & Seat Release -----------------

@app.route('/api/events/<int:event_id>/check-clash', methods=['POST'])
def check_clash_route(event_id):
    data = request.get_json() or {}
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    has_clash, colliding = check_schedule_clash(user_id, event_id)
    return jsonify({
        "has_clash": has_clash,
        "colliding_events": colliding
    })

@app.route('/api/events/<int:event_id>/register', methods=['POST'])
def register_for_event(event_id):
    data = request.get_json() or {}
    user_id = data.get('user_id')
    override_conflict = data.get('override_conflict', False)

    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    success, message, extra = register_user_for_event(user_id, event_id, override_conflict=override_conflict)
    if not success:
        return jsonify({
            "success": False,
            "message": message,
            "details": extra
        }), 400 if not (extra and extra.get('has_conflict')) else 409

    return jsonify({
        "success": True,
        "message": message,
        "data": extra
    }), 201

@app.route('/api/events/<int:event_id>/waitlist', methods=['POST'])
def waitlist_route(event_id):
    data = request.get_json() or {}
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    success, message = join_waitlist(user_id, event_id)
    if not success:
        return jsonify({"success": False, "message": message}), 400

    return jsonify({"success": True, "message": message}), 200

@app.route('/api/registrations/<int:reg_id>/cancel', methods=['POST'])
def cancel_registration_route(reg_id):
    data = request.get_json() or {}
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    success, message = cancel_registration(reg_id, user_id)
    if not success:
        return jsonify({"success": False, "message": message}), 400

    return jsonify({"success": True, "message": message})

@app.route('/api/waitlist/<int:waitlist_id>/claim', methods=['POST'])
def claim_offer_route(waitlist_id):
    data = request.get_json() or {}
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    success, result = claim_waitlist_offer(waitlist_id, user_id)
    if not success:
        return jsonify({"success": False, "message": result}), 400

    return jsonify({"success": True, "data": result})

@app.route('/api/registrations/<int:reg_id>/pass', methods=['GET'])
def get_pass_details(reg_id):
    db = get_db()
    reg = db.execute("""
        SELECT r.*, u.name as student_name, u.roll_no, u.department, u.section,
               e.title as event_title, e.category as event_category, e.venue, e.start_time, e.end_time, e.club_name
        FROM registrations r
        JOIN users u ON r.user_id = u.id
        JOIN events e ON r.event_id = e.id
        WHERE r.id = ?
    """, (reg_id,)).fetchone()
    db.close()

    if not reg:
        return jsonify({"error": "Registration pass not found"}), 404

    item = dict(reg)
    item['qr_image'] = generate_qr_image_base64(item['qr_token'])
    return jsonify(item)

# ----------------- QuickCheck QR Attendance Verification -----------------

@app.route('/api/checkin/verify', methods=['POST'])
def verify_checkin():
    data = request.get_json() or {}
    token = data.get('token')
    scanned_by = data.get('organizer_id', 1)
    event_id = data.get('event_id')

    if not token:
        return jsonify({"error": "QR token or pass code required"}), 400

    result = verify_and_checkin_pass(token, scanned_by, event_id_filter=event_id)
    return jsonify(result)

@app.route('/api/checkin/manual-toggle', methods=['POST'])
def manual_checkin_toggle():
    data = request.get_json() or {}
    reg_id = data.get('registration_id')
    scanned_by = data.get('organizer_id', 1)

    if not reg_id:
        return jsonify({"error": "registration_id required"}), 400

    db = get_db()
    cursor = db.cursor()
    reg = cursor.execute("""
        SELECT r.*, e.title, e.category, e.club_name, e.venue, e.start_time, u.name as student_name
        FROM registrations r
        JOIN events e ON r.event_id = e.id
        JOIN users u ON r.user_id = u.id
        WHERE r.id = ?
    """, (reg_id,)).fetchone()

    if not reg:
        db.close()
        return jsonify({"error": "Registration not found"}), 404

    now_str = datetime.now().isoformat()
    if reg['status'] == 'attended':
        # Revert back to confirmed
        cursor.execute("UPDATE registrations SET status = 'confirmed', attended_at = NULL, checkin_by = NULL WHERE id = ?", (reg_id,))
        cursor.execute("DELETE FROM passport_stamps WHERE user_id = ? AND event_id = ?", (reg['user_id'], reg['event_id']))
        cursor.execute("""
            INSERT INTO attendance_logs (event_id, registration_id, user_id, verification_status, message, scanned_by)
            VALUES (?, ?, ?, 'manual_revert', 'Organizer reverted attendance', ?)
        """, (reg['event_id'], reg_id, reg['user_id'], scanned_by))
        new_status = 'confirmed'
        msg = f"Check-in revoked for {reg['student_name']}"
    else:
        # Mark as attended
        cursor.execute("UPDATE registrations SET status = 'attended', attended_at = ?, checkin_by = ? WHERE id = ?", (now_str, scanned_by, reg_id))
        cursor.execute("""
            INSERT OR IGNORE INTO passport_stamps 
            (user_id, event_id, stamp_title, stamp_category, club_name, venue, event_date, badge_level, awarded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Standard', ?)
        """, (reg['user_id'], reg['event_id'], reg['title'], reg['category'], reg['club_name'], reg['venue'], reg['start_time'], now_str))
        cursor.execute("""
            INSERT INTO attendance_logs (event_id, registration_id, user_id, verification_status, message, scanned_by)
            VALUES (?, ?, ?, 'valid', 'Manual check-in confirmed by organizer', ?)
        """, (reg['event_id'], reg_id, reg['user_id'], scanned_by))
        new_status = 'attended'
        msg = f"Attendance marked for {reg['student_name']}"

    db.commit()
    db.close()
    return jsonify({"success": True, "status": new_status, "message": msg})

# ----------------- Organizer Dashboard & Analytics -----------------

@app.route('/api/organizer/analytics', methods=['GET'])
def organizer_analytics():
    analytics = get_organizer_analytics()
    return jsonify(analytics)

@app.route('/api/organizer/events/<int:event_id>/attendees', methods=['GET'])
def event_attendees(event_id):
    status_filter = request.args.get('status')
    search = request.args.get('search')
    attendees = get_event_attendees(event_id, status_filter=status_filter, search=search)
    return jsonify(attendees)

# ----------------- Frontend Static Serving -----------------

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if FRONTEND_DIST and os.path.exists(FRONTEND_DIST):
        file_path = os.path.join(FRONTEND_DIST, path)
        if path != "" and os.path.exists(file_path):
            return send_from_directory(FRONTEND_DIST, path)
        else:
            return send_from_directory(FRONTEND_DIST, 'index.html')
    return jsonify({
        "name": "EventSphere API Server",
        "message": "Frontend build not yet generated. API is running on /api/...",
        "endpoints": [
            "/api/health", "/api/events", "/api/users", "/api/organizer/analytics"
        ]
    })

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5050))
    print(f"Starting EventSphere Flask Backend on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
