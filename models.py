import uuid
from datetime import datetime, timedelta
import json
from database import get_db
from qr_service import generate_qr_token, generate_qr_image_base64, parse_and_verify_qr_token

def get_event_seat_pulse(event_id, db=None):
    """
    Computes Live Seat Pulse metrics for a specific event.
    """
    close_db = False
    if db is None:
        db = get_db()
        close_db = True

    event = db.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    if not event:
        if close_db:
            db.close()
        return None

    capacity = event['capacity']
    
    # Active confirmed or attended registrations
    confirmed_row = db.execute("""
        SELECT COUNT(*) as cnt FROM registrations 
        WHERE event_id = ? AND status IN ('confirmed', 'attended')
    """, (event_id,)).fetchone()
    confirmed_count = confirmed_row['cnt'] if confirmed_row else 0

    # Waitlist count
    waitlist_row = db.execute("""
        SELECT COUNT(*) as cnt FROM waitlist 
        WHERE event_id = ? AND status IN ('waiting', 'offered')
    """, (event_id,)).fetchone()
    waitlist_count = waitlist_row['cnt'] if waitlist_row else 0

    # Cancelled count
    cancelled_row = db.execute("""
        SELECT COUNT(*) as cnt FROM registrations 
        WHERE event_id = ? AND status = 'cancelled'
    """, (event_id,)).fetchone()
    cancelled_count = cancelled_row['cnt'] if cancelled_row else 0

    # Attended count
    attended_row = db.execute("""
        SELECT COUNT(*) as cnt FROM registrations 
        WHERE event_id = ? AND status = 'attended'
    """, (event_id,)).fetchone()
    attended_count = attended_row['cnt'] if attended_row else 0

    remaining_seats = max(0, capacity - confirmed_count)
    is_full = remaining_seats <= 0
    percent_filled = min(100, round((confirmed_count / capacity) * 100, 1)) if capacity > 0 else 0

    pulse_state = "open"
    if is_full:
        pulse_state = "full"
    elif percent_filled >= 80:
        pulse_state = "filling_fast"
    
    result = {
        "event_id": event_id,
        "capacity": capacity,
        "confirmed_count": confirmed_count,
        "remaining_seats": remaining_seats,
        "waitlist_count": waitlist_count,
        "cancelled_count": cancelled_count,
        "attended_count": attended_count,
        "is_full": is_full,
        "percent_filled": percent_filled,
        "pulse_state": pulse_state
    }

    if close_db:
        db.close()
    return result

def get_all_events(category=None, search=None, user_id=None):
    """
    Retrieves all published events with Live Seat Pulse and optional user registration state.
    """
    db = get_db()
    query = "SELECT e.*, u.name as organizer_name FROM events e JOIN users u ON e.organizer_id = u.id WHERE e.status != 'draft'"
    params = []

    if category and category.lower() != 'all':
        query += " AND LOWER(e.category) = LOWER(?)"
        params.append(category)

    if search:
        query += " AND (LOWER(e.title) LIKE ? OR LOWER(e.description) LIKE ? OR LOWER(e.venue) LIKE ? OR LOWER(e.club_name) LIKE ?)"
        term = f"%{search.lower()}%"
        params.extend([term, term, term, term])

    query += " ORDER BY e.start_time ASC"
    rows = db.execute(query, params).fetchall()

    events = []
    for row in rows:
        evt = dict(row)
        pulse = get_event_seat_pulse(evt['id'], db)
        evt['seat_pulse'] = pulse

        # Check if user is already registered / waitlisted
        user_status = None
        user_reg_id = None
        if user_id:
            reg = db.execute("""
                SELECT id, status FROM registrations 
                WHERE event_id = ? AND user_id = ? AND status != 'cancelled'
            """, (evt['id'], user_id)).fetchone()
            if reg:
                user_status = reg['status']
                user_reg_id = reg['id']
            else:
                wl = db.execute("""
                    SELECT id, status FROM waitlist 
                    WHERE event_id = ? AND user_id = ? AND status IN ('waiting', 'offered')
                """, (evt['id'], user_id)).fetchone()
                if wl:
                    user_status = f"waitlist_{wl['status']}"
        
        evt['user_registration_status'] = user_status
        evt['user_registration_id'] = user_reg_id
        events.append(evt)

    db.close()
    return events

def get_event_by_id(event_id, user_id=None):
    """
    Retrieves detailed event data with full seat pulse & user context.
    """
    db = get_db()
    row = db.execute("""
        SELECT e.*, u.name as organizer_name, u.email as organizer_email 
        FROM events e 
        JOIN users u ON e.organizer_id = u.id 
        WHERE e.id = ?
    """, (event_id,)).fetchone()

    if not row:
        db.close()
        return None

    evt = dict(row)
    evt['seat_pulse'] = get_event_seat_pulse(event_id, db)

    # Check user registration status
    user_status = None
    user_reg = None
    if user_id:
        reg = db.execute("""
            SELECT * FROM registrations 
            WHERE event_id = ? AND user_id = ? AND status != 'cancelled'
        """, (event_id, user_id)).fetchone()
        if reg:
            user_status = reg['status']
            user_reg = dict(reg)
            if reg['status'] in ('confirmed', 'attended'):
                user_reg['qr_image'] = generate_qr_image_base64(reg['qr_token'])
        else:
            wl = db.execute("""
                SELECT * FROM waitlist 
                WHERE event_id = ? AND user_id = ? AND status IN ('waiting', 'offered')
            """, (event_id, user_id)).fetchone()
            if wl:
                user_status = f"waitlist_{wl['status']}"
                user_reg = dict(wl)

    evt['user_status'] = user_status
    evt['user_registration'] = user_reg
    db.close()
    return evt

def check_schedule_clash(user_id, event_id):
    """
    Checks if registering for event_id will clash with any of the user's
    existing confirmed/attended events.
    """
    db = get_db()
    target_event = db.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    if not target_event:
        db.close()
        return False, None

    # Find active registrations of user
    clashes = db.execute("""
        SELECT e.* FROM registrations r
        JOIN events e ON r.event_id = e.id
        WHERE r.user_id = ? 
          AND r.status IN ('confirmed', 'attended')
          AND e.id != ?
          AND (
            (e.start_time <= ? AND e.end_time > ?) OR
            (e.start_time < ? AND e.end_time >= ?) OR
            (e.start_time >= ? AND e.end_time <= ?)
          )
    """, (
        user_id, event_id,
        target_event['start_time'], target_event['start_time'],
        target_event['end_time'], target_event['end_time'],
        target_event['start_time'], target_event['end_time']
    )).fetchall()

    db.close()
    if clashes:
        colliding_events = [dict(c) for c in clashes]
        return True, colliding_events
    return False, None

def register_user_for_event(user_id, event_id, override_conflict=False):
    """
    Capacity-aware event registration with schedule clash check and atomic transaction.
    """
    db = get_db()
    cursor = db.cursor()

    try:
        user = cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        event = cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
        if not user or not event:
            return False, "User or Event not found", None

        # 1. Check duplicate active registration
        existing = cursor.execute("""
            SELECT * FROM registrations 
            WHERE event_id = ? AND user_id = ? AND status != 'cancelled'
        """, (event_id, user_id)).fetchone()
        if existing:
            return False, f"You are already registered for this event with status: {existing['status']}", None

        # 2. Check duplicate waitlist
        in_wl = cursor.execute("""
            SELECT * FROM waitlist 
            WHERE event_id = ? AND user_id = ? AND status IN ('waiting', 'offered')
        """, (event_id, user_id)).fetchone()
        if in_wl:
            return False, "You are already on the waitlist for this event", None

        # 3. Check Schedule Clash unless overridden
        has_clash, colliding = check_schedule_clash(user_id, event_id)
        if has_clash and not override_conflict:
            return False, "Schedule conflict detected with another registered event", {
                "has_conflict": True,
                "colliding_events": colliding
            }

        # 4. Check Capacity
        pulse = get_event_seat_pulse(event_id, db)
        if pulse['is_full']:
            return False, "Event is currently full. Would you like to join the waitlist?", {
                "is_full": True,
                "can_waitlist": True
            }

        # 5. Create Confirmed Registration
        reg_code = f"ES-{datetime.now().strftime('%y%m')}-{uuid.uuid4().hex[:6].upper()}"
        qr_token = generate_qr_token(reg_code, user['roll_no'], event_id)
        
        cursor.execute("""
            INSERT INTO registrations (registration_code, event_id, user_id, status, qr_token, registered_at)
            VALUES (?, ?, ?, 'confirmed', ?, ?)
        """, (reg_code, event_id, user_id, qr_token, datetime.now().isoformat()))

        reg_id = cursor.lastrowid
        db.commit()

        qr_image = generate_qr_image_base64(qr_token)
        return True, "Registration successful!", {
            "registration_id": reg_id,
            "registration_code": reg_code,
            "status": "confirmed",
            "qr_token": qr_token,
            "qr_image": qr_image,
            "event_title": event['title']
        }

    except Exception as e:
        db.rollback()
        return False, f"Error processing registration: {str(e)}", None
    finally:
        db.close()

def join_waitlist(user_id, event_id):
    """
    Places user on chronological waitlist when event is full.
    """
    db = get_db()
    cursor = db.cursor()
    try:
        user = cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        event = cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
        if not user or not event:
            return False, "User or Event not found"

        # Check existing registration or waitlist
        existing = cursor.execute("""
            SELECT * FROM registrations 
            WHERE event_id = ? AND user_id = ? AND status != 'cancelled'
        """, (event_id, user_id)).fetchone()
        if existing:
            return False, f"Already registered for this event (status: {existing['status']})"

        in_wl = cursor.execute("""
            SELECT * FROM waitlist 
            WHERE event_id = ? AND user_id = ? AND status IN ('waiting', 'offered')
        """, (event_id, user_id)).fetchone()
        if in_wl:
            return False, "Already on the waitlist for this event"

        cursor.execute("""
            INSERT INTO waitlist (event_id, user_id, joined_at, status)
            VALUES (?, ?, ?, 'waiting')
        """, (event_id, user_id, datetime.now().isoformat()))

        # Get position in waitlist
        pos = cursor.execute("""
            SELECT COUNT(*) as pos FROM waitlist 
            WHERE event_id = ? AND status IN ('waiting', 'offered')
        """, (event_id,)).fetchone()['pos']

        db.commit()
        return True, f"Successfully joined waitlist! You are #{pos} in queue."
    except Exception as e:
        db.rollback()
        return False, f"Error joining waitlist: {str(e)}"
    finally:
        db.close()

def cancel_registration(registration_id, user_id):
    """
    Cancels a confirmed registration and triggers Smart Seat Release
    to the next eligible waitlisted student.
    """
    db = get_db()
    cursor = db.cursor()
    try:
        reg = cursor.execute("""
            SELECT * FROM registrations WHERE id = ? AND user_id = ?
        """, (registration_id, user_id)).fetchone()

        if not reg:
            return False, "Registration not found or access denied"

        if reg['status'] == 'cancelled':
            return False, "Registration is already cancelled"

        event_id = reg['event_id']

        # Update registration status to cancelled
        cursor.execute("""
            UPDATE registrations 
            SET status = 'cancelled', cancelled_at = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), registration_id))

        # Smart Seat Release: Offer seat to next waitlisted student
        next_waitlisted = cursor.execute("""
            SELECT * FROM waitlist 
            WHERE event_id = ? AND status = 'waiting'
            ORDER BY joined_at ASC LIMIT 1
        """, (event_id,)).fetchone()

        offered_to = None
        if next_waitlisted:
            # 15 minutes claim window
            expires_at = (datetime.now() + timedelta(minutes=15)).isoformat()
            cursor.execute("""
                UPDATE waitlist 
                SET status = 'offered', offer_expires_at = ?
                WHERE id = ?
            """, (expires_at, next_waitlisted['id']))
            offered_to = next_waitlisted['user_id']

        db.commit()
        msg = "Registration successfully cancelled."
        if offered_to:
            msg += " Smart Seat Release triggered: Released seat offered to the next waitlisted student!"

        return True, msg
    except Exception as e:
        db.rollback()
        return False, f"Cancellation failed: {str(e)}"
    finally:
        db.close()

def claim_waitlist_offer(waitlist_id, user_id):
    """
    Waitlisted user claims their offered seat within the time limit.
    """
    db = get_db()
    cursor = db.cursor()
    try:
        wl = cursor.execute("""
            SELECT w.*, e.title, u.roll_no 
            FROM waitlist w 
            JOIN events e ON w.event_id = e.id 
            JOIN users u ON w.user_id = u.id
            WHERE w.id = ? AND w.user_id = ?
        """, (waitlist_id, user_id)).fetchone()

        if not wl:
            return False, "Waitlist record not found"

        if wl['status'] != 'offered':
            return False, f"Waitlist offer is not in 'offered' state (current: {wl['status']})"

        # Check expiration
        if wl['offer_expires_at']:
            exp = datetime.fromisoformat(wl['offer_expires_at'])
            if datetime.now() > exp:
                cursor.execute("UPDATE waitlist SET status = 'expired' WHERE id = ?", (waitlist_id,))
                db.commit()
                return False, "The claim window for this seat offer has expired."

        # Convert to confirmed registration
        reg_code = f"ES-{datetime.now().strftime('%y%m')}-{uuid.uuid4().hex[:6].upper()}"
        qr_token = generate_qr_token(reg_code, wl['roll_no'], wl['event_id'])

        cursor.execute("""
            INSERT INTO registrations (registration_code, event_id, user_id, status, qr_token, registered_at)
            VALUES (?, ?, ?, 'confirmed', ?, ?)
        """, (reg_code, wl['event_id'], user_id, qr_token, datetime.now().isoformat()))

        # Mark waitlist as claimed
        cursor.execute("UPDATE waitlist SET status = 'claimed' WHERE id = ?", (waitlist_id,))
        db.commit()

        qr_image = generate_qr_image_base64(qr_token)
        return True, {
            "message": "Congratulations! Your seat is confirmed.",
            "registration_code": reg_code,
            "qr_token": qr_token,
            "qr_image": qr_image
        }
    except Exception as e:
        db.rollback()
        return False, f"Claim failed: {str(e)}"
    finally:
        db.close()

def verify_and_checkin_pass(token_str, scanned_by_user_id, event_id_filter=None):
    """
    Core QuickCheck Attendance Verification:
    - Parses and cryptographically verifies QR token
    - Ensures single entry per registration (blocks duplicates)
    - Records audit log
    - Awards Event Passport stamp upon successful check-in
    """
    db = get_db()
    cursor = db.cursor()

    is_valid_format, data, err_msg = parse_and_verify_qr_token(token_str)
    if not is_valid_format:
        return {
            "status": "invalid",
            "title": "Invalid QR Pass",
            "message": err_msg or "Unrecognized QR code data format.",
            "attendee": None
        }

    reg_code = data['registration_code']
    
    # Query registration with user and event details
    reg = cursor.execute("""
        SELECT r.*, u.name as student_name, u.roll_no, u.department, u.section,
               e.id as event_id, e.title as event_title, e.category as event_category, 
               e.club_name, e.venue, e.start_time
        FROM registrations r
        JOIN users u ON r.user_id = u.id
        JOIN events e ON r.event_id = e.id
        WHERE r.registration_code = ?
    """, (reg_code,)).fetchone()

    if not reg:
        cursor.execute("""
            INSERT INTO attendance_logs (event_id, verification_status, message, scanned_by)
            VALUES (?, 'invalid', ?, ?)
        """, (event_id_filter or 0, f"No registration matching code: {reg_code}", scanned_by_user_id))
        db.commit()
        db.close()
        return {
            "status": "invalid",
            "title": "Pass Not Found",
            "message": f"No active registration record found for pass code '{reg_code}'.",
            "attendee": None
        }

    attendee_info = {
        "registration_code": reg['registration_code'],
        "student_name": reg['student_name'],
        "roll_no": reg['roll_no'],
        "department": f"{reg['department']} - {reg['section']}",
        "event_title": reg['event_title'],
        "event_category": reg['event_category'],
        "venue": reg['venue']
    }

    # Verify event ID matches if event_id_filter supplied
    if event_id_filter and int(reg['event_id']) != int(event_id_filter):
        db.close()
        return {
            "status": "wrong_event",
            "title": "Wrong Event Pass",
            "message": f"This pass is for '{reg['event_title']}', not the currently selected event.",
            "attendee": attendee_info
        }

    # Check Registration Status
    if reg['status'] == 'cancelled':
        cursor.execute("""
            INSERT INTO attendance_logs (event_id, registration_id, user_id, verification_status, message, scanned_by)
            VALUES (?, ?, ?, 'cancelled', 'Attempted check-in with cancelled ticket', ?)
        """, (reg['event_id'], reg['id'], reg['user_id'], scanned_by_user_id))
        db.commit()
        db.close()
        return {
            "status": "cancelled",
            "title": "Pass Cancelled",
            "message": f"This registration was cancelled on {reg['cancelled_at'] or 'earlier'}. Entry denied.",
            "attendee": attendee_info
        }

    if reg['status'] == 'attended':
        cursor.execute("""
            INSERT INTO attendance_logs (event_id, registration_id, user_id, verification_status, message, scanned_by)
            VALUES (?, ?, ?, 'duplicate_rejected', 'Duplicate check-in blocked', ?)
        """, (reg['event_id'], reg['id'], reg['user_id'], scanned_by_user_id))
        db.commit()
        db.close()
        return {
            "status": "duplicate",
            "title": "Duplicate Check-in Blocked",
            "message": f"Attendee already checked in at {reg['attended_at']}! Duplicate scan rejected.",
            "attendee": attendee_info,
            "attended_at": reg['attended_at']
        }

    # VALID PASS -> MARK ATTENDED
    checkin_time = datetime.now().isoformat()
    cursor.execute("""
        UPDATE registrations 
        SET status = 'attended', attended_at = ?, checkin_by = ?
        WHERE id = ?
    """, (checkin_time, scanned_by_user_id, reg['id']))

    # Log attendance
    cursor.execute("""
        INSERT INTO attendance_logs (event_id, registration_id, user_id, verification_status, message, scanned_by)
        VALUES (?, ?, ?, 'valid', 'Attendance successfully verified', ?)
    """, (reg['event_id'], reg['id'], reg['user_id'], scanned_by_user_id))

    # Award Event Passport Stamp
    stamp_level = 'Gold' if reg['event_category'] in ('Technical', 'Workshop') else 'Standard'
    cursor.execute("""
        INSERT OR IGNORE INTO passport_stamps 
        (user_id, event_id, stamp_title, stamp_category, club_name, venue, event_date, badge_level, awarded_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        reg['user_id'], reg['event_id'], reg['event_title'], 
        reg['event_category'], reg['club_name'], reg['venue'], 
        reg['start_time'], stamp_level, checkin_time
    ))

    db.commit()
    db.close()

    attendee_info['attended_at'] = checkin_time
    return {
        "status": "verified",
        "title": "Entry Verified & Checked In!",
        "message": f"Welcome, {reg['student_name']}! QuickCheck verification successful.",
        "attendee": attendee_info
    }

def get_user_passport(user_id):
    """
    Returns student Event Passport stamps and participation metrics.
    """
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        db.close()
        return None

    stamps = db.execute("""
        SELECT * FROM passport_stamps 
        WHERE user_id = ? 
        ORDER BY awarded_at DESC
    """, (user_id,)).fetchall()

    stamps_list = [dict(s) for s in stamps]
    total_attended = len(stamps_list)

    # Category breakdown
    cat_counts = {}
    for s in stamps_list:
        c = s['stamp_category']
        cat_counts[c] = cat_counts.get(c, 0) + 1

    # Gamified badge calculation
    tier = "Campus Explorer"
    if total_attended >= 5:
        tier = "Gold Campus Ambassador"
    elif total_attended >= 3:
        tier = "Silver Campus Achiever"
    elif total_attended >= 1:
        tier = "Bronze Campus Participant"

    db.close()
    return {
        "user": dict(user),
        "total_attended": total_attended,
        "passport_tier": tier,
        "category_breakdown": cat_counts,
        "stamps": stamps_list
    }

def get_user_registrations(user_id):
    """
    Retrieves all registrations and waitlist items for a user.
    """
    db = get_db()
    regs = db.execute("""
        SELECT r.*, e.title as event_title, e.category as event_category, 
               e.start_time, e.end_time, e.venue, e.club_name, e.banner_url
        FROM registrations r
        JOIN events e ON r.event_id = e.id
        WHERE r.user_id = ?
        ORDER BY r.registered_at DESC
    """, (user_id,)).fetchall()

    result = []
    for r in regs:
        item = dict(r)
        if item['status'] in ('confirmed', 'attended'):
            item['qr_image'] = generate_qr_image_base64(item['qr_token'])
        result.append(item)

    # Also fetch waitlist items
    waitlisted = db.execute("""
        SELECT w.*, e.title as event_title, e.category as event_category,
               e.start_time, e.end_time, e.venue, e.club_name, e.banner_url
        FROM waitlist w
        JOIN events e ON w.event_id = e.id
        WHERE w.user_id = ? AND w.status IN ('waiting', 'offered')
        ORDER BY w.joined_at DESC
    """, (user_id,)).fetchall()

    wl_result = []
    for w in waitlisted:
        wl_item = dict(w)
        # Check position
        pos = db.execute("""
            SELECT COUNT(*) as pos FROM waitlist 
            WHERE event_id = ? AND status IN ('waiting', 'offered') AND joined_at <= ?
        """, (w['event_id'], w['joined_at'])).fetchone()['pos']
        wl_item['queue_position'] = pos
        wl_result.append(wl_item)

    db.close()
    return {
        "registrations": result,
        "waitlist": wl_result
    }

def get_organizer_analytics():
    """
    Computes analytics across events: registration rates, attendance rates,
    seat utilization %, cancellations, and category breakdown.
    """
    db = get_db()
    
    events_count = db.execute("SELECT COUNT(*) as cnt FROM events WHERE status != 'draft'").fetchone()['cnt']
    total_capacity = db.execute("SELECT SUM(capacity) as total FROM events WHERE status != 'draft'").fetchone()['total'] or 0

    total_regs = db.execute("SELECT COUNT(*) as cnt FROM registrations").fetchone()['cnt']
    confirmed_count = db.execute("SELECT COUNT(*) as cnt FROM registrations WHERE status = 'confirmed'").fetchone()['cnt']
    attended_count = db.execute("SELECT COUNT(*) as cnt FROM registrations WHERE status = 'attended'").fetchone()['cnt']
    cancelled_count = db.execute("SELECT COUNT(*) as cnt FROM registrations WHERE status = 'cancelled'").fetchone()['cnt']
    waitlist_count = db.execute("SELECT COUNT(*) as cnt FROM waitlist WHERE status IN ('waiting', 'offered')").fetchone()['cnt']

    active_registrations = confirmed_count + attended_count
    seat_utilization = round((active_registrations / total_capacity * 100), 1) if total_capacity > 0 else 0
    attendance_rate = round((attended_count / active_registrations * 100), 1) if active_registrations > 0 else 0
    cancellation_rate = round((cancelled_count / total_regs * 100), 1) if total_regs > 0 else 0

    # Category breakdown
    cat_rows = db.execute("""
        SELECT category, COUNT(*) as count 
        FROM events 
        GROUP BY category
    """).fetchall()
    categories = {row['category']: row['count'] for row in cat_rows}

    # Event summaries
    event_rows = db.execute("""
        SELECT e.id, e.title, e.category, e.capacity, e.venue, e.start_time, e.club_name
        FROM events e 
        ORDER BY e.start_time ASC
    """).fetchall()

    event_summaries = []
    for ev in event_rows:
        p = get_event_seat_pulse(ev['id'], db)
        att_rate = round((p['attended_count'] / p['confirmed_count'] * 100), 1) if p['confirmed_count'] > 0 else 0
        event_summaries.append({
            "id": ev['id'],
            "title": ev['title'],
            "category": ev['category'],
            "capacity": ev['capacity'],
            "confirmed_count": p['confirmed_count'],
            "attended_count": p['attended_count'],
            "waitlist_count": p['waitlist_count'],
            "cancelled_count": p['cancelled_count'],
            "seat_utilization": p['percent_filled'],
            "attendance_rate": att_rate,
            "venue": ev['venue'],
            "start_time": ev['start_time'],
            "club_name": ev['club_name']
        })

    db.close()
    return {
        "metrics": {
            "total_events": events_count,
            "total_capacity": total_capacity,
            "total_registrations": total_regs,
            "active_registrations": active_registrations,
            "attended_count": attended_count,
            "cancelled_count": cancelled_count,
            "waitlist_count": waitlist_count,
            "seat_utilization_percent": seat_utilization,
            "attendance_rate_percent": attendance_rate,
            "cancellation_rate_percent": cancellation_rate
        },
        "category_distribution": categories,
        "events": event_summaries
    }

def get_event_attendees(event_id, status_filter=None, search=None):
    """
    Roster of attendees for an event with QuickCheck status.
    """
    db = get_db()
    query = """
        SELECT r.id as registration_id, r.registration_code, r.status, r.registered_at, 
               r.attended_at, r.cancelled_at, r.qr_token,
               u.id as user_id, u.name, u.roll_no, u.email, u.department, u.section, u.year
        FROM registrations r
        JOIN users u ON r.user_id = u.id
        WHERE r.event_id = ?
    """
    params = [event_id]

    if status_filter and status_filter.lower() != 'all':
        query += " AND r.status = ?"
        params.append(status_filter.lower())

    if search:
        query += " AND (LOWER(u.name) LIKE ? OR LOWER(u.roll_no) LIKE ? OR LOWER(r.registration_code) LIKE ?)"
        term = f"%{search.lower()}%"
        params.extend([term, term, term])

    query += " ORDER BY r.registered_at DESC"
    rows = db.execute(query, params).fetchall()

    attendees = [dict(row) for row in rows]
    db.close()
    return attendees

