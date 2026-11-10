from datetime import datetime, timedelta
import uuid
from database import get_db, init_db
from qr_service import generate_qr_token

def seed_database():
    init_db()
    db = get_db()
    cursor = db.cursor()

    # Clear existing data for fresh seed
    cursor.execute("DELETE FROM passport_stamps")
    cursor.execute("DELETE FROM attendance_logs")
    cursor.execute("DELETE FROM waitlist")
    cursor.execute("DELETE FROM registrations")
    cursor.execute("DELETE FROM events")
    cursor.execute("DELETE FROM users")
    try:
        cursor.execute("DELETE FROM sqlite_sequence")
    except Exception:
        pass

    print("Seeding Users...")
    users_data = [
        # Team Members
        ("1602-24-733-117", "G Srija Santoshini", "srija.117@vasavi.ac.in", "student", "CSE", 3, "B", "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150"),
        ("1602-24-733-114", "Siddheeshwar CH", "siddheeshwar.114@vasavi.ac.in", "student", "CSE", 3, "B", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150"),
        ("1602-24-733-081", "E Keerthi Teja", "keerthi.081@vasavi.ac.in", "student", "CSE", 3, "B", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150"),
        # Other Students
        ("1602-24-733-045", "Aarav Sharma", "aarav.045@vasavi.ac.in", "student", "CSE", 3, "B", "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150"),
        ("1602-24-733-092", "Ananya Verma", "ananya.092@vasavi.ac.in", "student", "IT", 3, "A", "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150"),
        ("1602-24-733-033", "Rohan Patel", "rohan.033@vasavi.ac.in", "student", "ECE", 2, "A", "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150"),
        ("1602-24-733-105", "Priya Reddy", "priya.105@vasavi.ac.in", "student", "CSE", 3, "B", "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=150"),
        # Organizers & Faculty
        ("FAC-CSE-001", "Dr. K. Srinivas (Faculty Coordinator)", "k.srinivas@vasavi.ac.in", "organizer", "CSE", 0, "Staff", "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150"),
        ("ORG-ACM-002", "ACM Student Chapter Lead", "acm.lead@vasavi.ac.in", "organizer", "CSE", 4, "A", "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150"),
        ("ORG-CULT-003", "Cultural Club Convener", "cultural@vasavi.ac.in", "organizer", "Campus", 4, "B", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150"),
        ("ADMIN-001", "College Admin Office", "admin.events@vasavi.ac.in", "admin", "Admin", 0, "Staff", "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=150")
    ]

    cursor.executemany("""
        INSERT INTO users (roll_no, name, email, role, department, year, section, avatar_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, users_data)
    db.commit()

    # User map
    users = {row['roll_no']: row['id'] for row in cursor.execute("SELECT id, roll_no FROM users").fetchall()}
    org_acm_id = users["ORG-ACM-002"]
    org_cult_id = users["ORG-CULT-003"]
    fac_id = users["FAC-CSE-001"]

    print("Seeding Events...")
    base_time = datetime.now()
    today = base_time.date()
    events_data = [
        (
            "HackVasavi 2026: 24-Hour Campus Hackathon",
            "hackvasavi-2026",
            "Join the premier annual campus hackathon! Build impactful web, AI, and mobile solutions in 24 hours. Mentorship from alumni and exciting cash prizes, certificates, and direct recruitment tracks.",
            "Technical",
            "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800",
            "Ramanujan IT Block - Seminar Hall 1 & Labs",
            (today + timedelta(days=2)).strftime('%Y-%m-%d 10:00:00'),
            (today + timedelta(days=3)).strftime('%Y-%m-%d 10:00:00'),
            50, # Capacity
            org_acm_id,
            "Vasavi ACM Chapter",
            "published"
        ),
        (
            "Hands-on Generative AI & Agentic Systems Workshop",
            "gen-ai-agents-workshop",
            "Deep dive into Large Language Models, Multi-Agent architectures, Prompt Engineering, and RAG pipelines. Hands-on coding using Python, LangChain, and modern APIs. Bring your laptops!",
            "Workshop",
            "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800",
            "CSE Department Lab 3",
            (today + timedelta(days=4)).strftime('%Y-%m-%d 14:00:00'),
            (today + timedelta(days=4)).strftime('%Y-%m-%d 17:00:00'),
            25, # Capacity
            fac_id,
            "CSE Department & AI Club",
            "published"
        ),
        (
            "Euphoria 2026: Annual Inter-College Cultural Fest",
            "euphoria-2026-cultural-fest",
            "The grand celebration of dance, music, theater, and creative arts. Multiple stages, guest celebrity performers, food stalls, and battle of the bands. Open to all registered students.",
            "Cultural",
            "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=800",
            "Open Air Auditorium & Main Grounds",
            (today + timedelta(days=7)).strftime('%Y-%m-%d 16:00:00'),
            (today + timedelta(days=7)).strftime('%Y-%m-%d 22:00:00'),
            120, # Capacity
            org_cult_id,
            "Spandana Cultural Committee",
            "published"
        ),
        (
            "Inter-Department Badminton Championship",
            "badminton-championship-2026",
            "Annual doubles and singles knockout tournament between college departments. Medals, certificates and trophies for top 3 finishers in Men's and Women's categories.",
            "Sports",
            "https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?w=800",
            "Indoor Sports Complex - Court 1 & 2",
            (today + timedelta(days=5)).strftime('%Y-%m-%d 09:00:00'),
            (today + timedelta(days=5)).strftime('%Y-%m-%d 13:00:00'),
            16, # Capacity
            fac_id,
            "Physical Education & Sports Council",
            "published"
        ),
        (
            "Industry Tech Talk: Scaling Cloud Architectures",
            "scaling-cloud-architectures-seminar",
            "Distinguished guest keynote by Senior Staff Engineer on building resilient microservices, distributed caching, and zero-downtime deployment pipelines at global scale.",
            "Seminar",
            "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800",
            "Visvesvaraya Auditorium",
            (today + timedelta(days=8)).strftime('%Y-%m-%d 11:00:00'),
            (today + timedelta(days=8)).strftime('%Y-%m-%d 13:00:00'),
            60, # Capacity
            org_acm_id,
            "ACM & IEEE Student Branch",
            "published"
        ),
        (
            "Full-Stack Web Dev Speed Prototyping (Past / Check-in Sample)",
            "fswd-speed-prototyping-demo",
            "Hands-on project sprint showcasing React, Flask, and SQLite modern application architectures.",
            "Technical",
            "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800",
            "CSE Seminar Hall",
            (base_time - timedelta(days=1)).strftime('%Y-%m-%d 14:00:00'),
            (base_time - timedelta(days=1, hours=-3)).strftime('%Y-%m-%d 17:00:00'),
            30,
            fac_id,
            "CSE Department",
            "completed"
        )
    ]

    cursor.executemany("""
        INSERT INTO events (title, slug, description, category, banner_url, venue, start_time, end_time, capacity, organizer_id, club_name, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, events_data)
    db.commit()

    events_dict = {row['slug']: row['id'] for row in cursor.execute("SELECT id, slug FROM events").fetchall()}
    
    # 1. Register Srija for HackVasavi (Confirmed)
    srija_id = users["1602-24-733-117"]
    srija_roll = "1602-24-733-117"
    hack_id = events_dict["hackvasavi-2026"]
    
    reg_code_1 = "ES-2611-HACK01"
    qr_token_1 = generate_qr_token(reg_code_1, srija_roll, hack_id)
    cursor.execute("""
        INSERT INTO registrations (registration_code, event_id, user_id, status, qr_token, registered_at)
        VALUES (?, ?, ?, 'confirmed', ?, ?)
    """, (reg_code_1, hack_id, srija_id, qr_token_1, (base_time - timedelta(days=2)).isoformat()))

    # 2. Register Srija for Past Event (Attended) + Award Passport Stamp
    past_id = events_dict["fswd-speed-prototyping-demo"]
    reg_code_past = "ES-2611-FSWD99"
    qr_token_past = generate_qr_token(reg_code_past, srija_roll, past_id)
    cursor.execute("""
        INSERT INTO registrations (registration_code, event_id, user_id, status, qr_token, registered_at, attended_at, checkin_by)
        VALUES (?, ?, ?, 'attended', ?, ?, ?, ?)
    """, (reg_code_past, past_id, srija_id, qr_token_past, 
          (base_time - timedelta(days=3)).isoformat(), 
          (base_time - timedelta(days=1, hours=-1)).isoformat(), 
          fac_id))

    cursor.execute("""
        INSERT INTO passport_stamps (user_id, event_id, stamp_title, stamp_category, club_name, venue, event_date, badge_level, awarded_at)
        VALUES (?, ?, 'Full-Stack Web Dev Speed Prototyping', 'Technical', 'CSE Department', 'CSE Seminar Hall', ?, 'Gold', ?)
    """, (srija_id, past_id, (base_time - timedelta(days=1)).isoformat(), (base_time - timedelta(days=1, hours=-1)).isoformat()))

    # 3. Register Keerthi Teja for Euphoria (Confirmed)
    keerthi_id = users["1602-24-733-081"]
    keerthi_roll = "1602-24-733-081"
    cult_id = events_dict["euphoria-2026-cultural-fest"]
    reg_code_2 = "ES-2611-CULT02"
    qr_token_2 = generate_qr_token(reg_code_2, keerthi_roll, cult_id)
    cursor.execute("""
        INSERT INTO registrations (registration_code, event_id, user_id, status, qr_token, registered_at)
        VALUES (?, ?, ?, 'confirmed', ?, ?)
    """, (reg_code_2, cult_id, keerthi_id, qr_token_2, (base_time - timedelta(days=1)).isoformat()))

    # 4. Register Siddheeshwar for AI Workshop (Confirmed)
    sidd_id = users["1602-24-733-114"]
    sidd_roll = "1602-24-733-114"
    ai_id = events_dict["gen-ai-agents-workshop"]
    reg_code_3 = "ES-2611-AIWK03"
    qr_token_3 = generate_qr_token(reg_code_3, sidd_roll, ai_id)
    cursor.execute("""
        INSERT INTO registrations (registration_code, event_id, user_id, status, qr_token, registered_at)
        VALUES (?, ?, ?, 'confirmed', ?, ?)
    """, (reg_code_3, ai_id, sidd_id, qr_token_3, (base_time - timedelta(days=1)).isoformat()))

    # 5. Fill badminton championship to 16/16 capacity to demonstrate Waitlist
    badminton_id = events_dict["badminton-championship-2026"]
    sample_students = [
        users["1602-24-733-045"], users["1602-24-733-092"], users["1602-24-733-033"], users["1602-24-733-105"]
    ]
    for idx, st_id in enumerate(sample_students):
        b_code = f"ES-2611-BADM{idx+1:02d}"
        b_token = generate_qr_token(b_code, f"ROLL-{st_id}", badminton_id)
        cursor.execute("""
            INSERT INTO registrations (registration_code, event_id, user_id, status, qr_token, registered_at)
            VALUES (?, ?, ?, 'confirmed', ?, ?)
        """, (b_code, badminton_id, st_id, b_token, (base_time - timedelta(hours=idx+2)).isoformat()))

    # Put Srija on waitlist for badminton to showcase waitlist status & smart seat release
    cursor.execute("""
        INSERT INTO waitlist (event_id, user_id, joined_at, status)
        VALUES (?, ?, ?, 'waiting')
    """, (badminton_id, srija_id, (base_time - timedelta(minutes=45)).isoformat()))

    db.commit()
    db.close()
    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed_database()
