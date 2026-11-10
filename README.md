# EventSphere — Discover. Register. Connect.

> **Full Stack Web Development (FSWD) Course-Based Project**  
> **Team No:** 19 | **Section:** CSE-B | **Review Phase:** Comprehensive Implementation (Review 1, 2 & 3)

---

## 👥 Team Members & Responsibilities

| S.No | Name | Roll Number | Role & Primary Deliverables |
|:---:|:---|:---:|:---|
| **1** | **G Srija Santoshini** | `1602-24-733-117` | **Front-End Lead** — React.js application structure, responsive UI, Event Discovery, Event Details, Live Seat Pulse, My Registrations, Event Passport, Figma-aligned component design. |
| **2** | **Siddheeshwar CH** | `1602-24-733-114` | **Back-End Lead** — Flask REST API design, SQLite schema, capacity & duplicate-registration validation, Smart Seat Release logic, waitlist queue, Postman collection & endpoint tests. |
| **3** | **E Keerthi Teja** | `1602-24-733-081` | **Features & Quality Lead** — QuickCheck QR pass cryptographic generation & scanning verification workflow, attendance logs, integration testing, project documentation & deployment. |

---

## 📌 Problem Statement & Motivation

On college campuses, event announcements are scattered across messaging groups, printed posters, notice boards, and club social media pages. Students often discover events after seats are already filled or register for events that clash with their schedules. Furthermore:
- **Registration fragmentation:** Clubs collect registrations using disconnected Google Forms or spreadsheets, leading to duplicate entries and overbooking.
- **Invisible seat capacity:** Students cannot tell whether an event is full before registering.
- **Seat wastage on cancellation:** When a confirmed participant cancels, the freed seat is lost because there is no automated waitlist queue.
- **Paper / Manual Attendance:** Verification at venue entrances relies on manual name-checking on printed sheets, which is slow, error-prone, and susceptible to duplicate entry.
- **Lost Participation History:** Students have no consolidated record or credential verifying their campus activities.

**EventSphere** solves this end-to-end through a centralized student-focused web portal backed by a verified, capacity-aware Flask API and SQLite database.

---

## 🏛️ System Architecture

EventSphere follows a modular 3-tier Full-Stack Web Development architecture:

```
+-----------------------------------------------------------------------------------------+
|                                    PRESENTATION LAYER                                   |
|                      React.js SPA (Vite, React Router, Tailwind CSS)                     |
|                                                                                         |
|  [Discovery Hub]    [Live Seat Pulse]    [Schedule Clash Warning]    [My Registrations]  |
|  [QR Pass Viewer]   [Event Passport]     [Organizer Analytics]       [Camera Scanner]   |
+-----------------------------------------------------------------------------------------+
                                             │  ▲  HTTP REST / JSON APIs
                                             ▼  │  (Axios Client)
+-----------------------------------------------------------------------------------------+
|                                    APPLICATION LAYER                                    |
|                               Flask REST API (Python 3.13)                              |
|                                                                                         |
|  • /api/events            • /api/events/:id/register       • /api/checkin/verify        |
|  • /api/events/:id/pulse  • /api/registrations/:id/cancel  • /api/users/:id/passport    |
|  • /api/waitlist/:id/claim• /api/events/:id/check-clash    • /api/organizer/analytics   |
|                                                                                         |
|  [Capacity Validator]  [Conflict Detector]  [Smart Seat Engine]  [QR Crypto Verifier]  |
+-----------------------------------------------------------------------------------------+
                                             │  ▲  SQL Queries / Integrity Constraints
                                             ▼  │  (Foreign Keys, Unique Indices)
+-----------------------------------------------------------------------------------------+
|                                      DATA LAYER                                         |
|                               SQLite Relational Database                                |
|                                                                                         |
|   • users             • events             • registrations                              |
|   • waitlist          • attendance_logs    • passport_stamps                            |
+-----------------------------------------------------------------------------------------+
```

---

## 🚀 Key Features Implemented

### 1. 🔍 Centralized Event Discovery & Category Filtering (MVP Must-Have)
- Browse every published campus event in one responsive portal.
- Search by keywords, event title, club name, or campus venue.
- Category filters: **Technical**, **Cultural**, **Sports**, **Workshop**, and **Seminar**.
- Instant visual status badges for each event.

### 2. ⚡ Live Seat Pulse (MVP Must-Have)
- Real-time indicator displaying:
  - Total seating capacity.
  - Confirmed and attended student count.
  - Remaining available seats.
  - Waitlist queue count.
  - Progress bar dynamically changing states: **Open** (Emerald) ➔ **Filling Fast** (Amber) ➔ **Full - Waitlist Open** (Rose).

### 3. 🛡️ Capacity-Aware Registration & Schedule Clash Detection (MVP Must-Have)
- **Server-Side Validation:** Rejects overbooking and prevents duplicate registrations by the same student for the same event.
- **Schedule Clash Warning:** If a student attempts to register for an event that overlaps in date and time with another active registration, the system detects the conflict, presents a warning modal with details of the colliding event, and allows the student to either cancel or explicitly override.

### 4. 🔄 Smart Seat Release & Waitlist Automation (MVP Must-Have)
- When an event reaches 100% capacity, registration switches to **Join Waitlist**.
- Students are queued chronologically (FIFO).
- When a confirmed participant cancels their registration, the seat is **immediately released** and offered to the top waitlisted student with an active time-limited claim window.
- The waitlisted student receives an alert and can claim the seat with one click to confirm their admission and generate their pass.

### 5. 📱 QuickCheck QR Pass & Single-Entry Attendance Verification (MVP Must-Have)
- Generates a cryptographically signed QR code pass (`ESPASS:REG_CODE:ROLL_NO:EVENT_ID:SIG`) for each confirmed registration.
- Accessible directly under **My Registrations** with print and ticket download capabilities.
- **Organizer Verification Station:**
  - **Live Camera Scanner:** Scans passes directly using webcam / phone camera via `html5-qrcode`.
  - **Image Upload:** Decodes saved QR tickets or screenshots.
  - **Manual Entry Fallback:** Look up attendee by pass ID or roll number.
  - **Anti-Duplicate Check-in:** Marks attendee present *once* upon entry. Subsequent scans of the same pass are immediately rejected with an explicit warning: `Already checked in at [Time]! Duplicate scan blocked.`
  - Cancelled and invalid passes are flagged with clear refusal notices.

### 6. 🏆 Student Event Passport (Good-to-Have / Enhancement)
- Permanent digital credential tracking campus participation.
- Displays official digital passport stamps for every event attended, including event name, date, category, and organizing club seal.
- Gamified engagement tiers:
  - 🥉 **Bronze Campus Participant** (1–2 events)
  - 🥈 **Silver Campus Achiever** (3–4 events)
  - 🥇 **Gold Campus Ambassador** (5+ events)
- Printable official extracurricular participation transcript.

### 7. 📊 Organizer Dashboard & Insights (Good-to-Have / Enhancement)
- Centralized analytics dashboard reporting:
  - Total campus events & capacity.
  - Confirmed participants & attendance conversion rate.
  - Campus-wide seat utilization percentage.
  - Cancellation rate and waitlist queue volume.
  - Category breakdown visualization.
- Event management: Publish new events with capacity, venue, schedules, and club tags.
- Live Attendee Roster with manual attendance toggles and printable gate lists.

---

## 🛠️ Technology Stack Chosen

| Component | Technology | Rationale |
|:---|:---|:---|
| **Front End** | React.js 18 + Vite | Component-based SPA architecture, reactive state for filters and seat pulses, fast development server. |
| **Routing** | React Router v6 | Client-side routing between Discovery, Registrations, Passport, Organizer Dashboard, and Scanner. |
| **Styling** | Tailwind CSS | Modern, responsive design system matching Review 1 Figma UI wireframes. |
| **Back End** | Flask (Python 3.13) | Lightweight REST API framework with native JSON serialization and modular route architecture. |
| **Database** | SQLite 3 | Relational database with foreign key constraints, unique indices, and ACID transaction safety. |
| **QR Handling** | `qrcode` (Python) + `html5-qrcode` (React) | Open-source QR code generation and real-time webcam camera scanning. |
| **Testing** | `unittest` + Postman | Automated backend test suite validating capacity, waitlist claims, clashes, and check-in integrity. |

---

## 📂 Project Directory Structure

```
eventsphere/
├── backend/
│   ├── app.py                 # Flask server with REST APIs & static SPA serving
│   ├── database.py            # SQLite database schema, foreign keys, connection pool
│   ├── models.py              # Business logic (seat pulse, clash detector, waitlist)
│   ├── qr_service.py          # Cryptographic QR pass generator & verification
│   ├── seed_data.py           # College campus demo data (Vasavi CSE events & students)
│   ├── requirements.txt       # Python dependencies (Flask, flask-cors, qrcode, pillow)
│   ├── eventsphere.db         # SQLite database file
│   └── tests/
│       └── test_api.py        # Automated test suite (6 passing verification tests)
├── frontend/
│   ├── package.json           # Frontend package manifest
│   ├── vite.config.js         # Vite configuration with backend proxy
│   ├── tailwind.config.js     # Tailwind CSS theme & typography
│   ├── index.html             # HTML entry point
│   ├── src/
│   │   ├── api/client.js      # Axios API client functions
│   │   ├── context/AuthContext.jsx # Persona & role switcher state
│   │   ├── components/
│   │   │   ├── Navbar.jsx     # Header with role switcher & demo reset
│   │   │   ├── LiveSeatPulse.jsx # Real-time capacity progress indicator
│   │   │   ├── EventCard.jsx  # Event discovery card
│   │   │   ├── QRPassModal.jsx # QuickCheck QR Pass modal & printable ticket
│   │   │   └── ConflictWarningModal.jsx # Schedule clash alert modal
│   │   ├── pages/
│   │   │   ├── DiscoveryPage.jsx # Event browsing & category filter
│   │   │   ├── EventDetailsPage.jsx # Event info, registration & waitlist
│   │   │   ├── MyRegistrationsPage.jsx # My tickets, QR passes, cancel seat
│   │   │   ├── EventPassportPage.jsx # Gamified stamps & participation stats
│   │   │   ├── OrganizerDashboardPage.jsx # Analytics & event creator
│   │   │   ├── QuickCheckScannerPage.jsx # QR camera scanner & verify station
│   │   │   └── AttendeeListPage.jsx # Gate roster & manual check-in
│   │   ├── App.jsx            # Router and notification toast
│   │   ├── main.jsx           # React DOM root
│   │   └── index.css          # Tailwind directives & custom CSS
│   └── dist/                  # Production-optimized React bundle
├── postman_collection.json    # Ready-to-import Postman REST API collection
├── run.py                     # Single-command full-stack launcher
├── start.sh                   # Startup shell script with pre-run test check
└── README.md                  # Comprehensive project report & documentation
```

---

## ⚡ Quick Start & Execution Instructions

### Option 1: One-Command Full Stack Launcher (Recommended)
This runs the production-ready React application and Flask REST API unified on a single port (`http://127.0.0.1:5050`):

```bash
# 1. Run the test suite and launch server
./start.sh
```

Or directly using Python:
```bash
python3 run.py
```
Open **`http://127.0.0.1:5050`** in your browser.

---

### Option 2: Running with Separate Vite Development Server
If you want to run the front-end in active hot-reloading development mode:

1. **Terminal 1 — Start Flask Backend:**
   ```bash
   cd backend
   python3 app.py
   ```
   *Backend runs on `http://127.0.0.1:5050`.*

2. **Terminal 2 — Start Vite React Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```
   *Frontend dev server runs on `http://localhost:3000` (automatically proxies API requests to port 5050).*

---

### Option 3: Running the Automated Test Suite
To verify server-side validation, capacity enforcement, schedule clash warnings, QR duplicate prevention, and Smart Seat Release:

```bash
python3 backend/tests/test_api.py
```

Expected output:
```
EventSphere database initialized at: .../backend/eventsphere.db
Seeding Users...
Seeding Events...
Database seeding completed successfully!
......
----------------------------------------------------------------------
Ran 6 tests in 0.075s

OK
```

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|:---:|:---|:---|
| `GET` | `/api/health` | Service status and version check |
| `GET` | `/api/events` | List events with Live Seat Pulse (supports `?category=` and `?search=`) |
| `GET` | `/api/events/<id>` | Full event details with user registration status |
| `POST` | `/api/events` | Create a new campus event (Organizer) |
| `POST` | `/api/events/<id>/check-clash` | Check for overlapping registrations for a student |
| `POST` | `/api/events/<id>/register` | Capacity-aware registration with duplicate prevention |
| `POST` | `/api/events/<id>/waitlist` | Join FIFO waitlist queue when event capacity is full |
| `POST` | `/api/registrations/<id>/cancel` | Cancel registration & trigger Smart Seat Release |
| `POST` | `/api/waitlist/<id>/claim` | Claim offered seat during the time-limited claim window |
| `GET` | `/api/registrations/<id>/pass` | Retrieve QuickCheck QR pass details and Base64 image |
| `POST` | `/api/checkin/verify` | Verify QR pass at entrance (marks present, blocks duplicates) |
| `POST` | `/api/checkin/manual-toggle` | Organizer manual check-in toggle fallback |
| `GET` | `/api/users/<id>/passport` | Student Event Passport stamps & participation tier |
| `GET` | `/api/organizer/analytics` | Overall campus events metrics, attendance rates & utilization |
| `GET` | `/api/organizer/events/<id>/attendees` | Live attendee roster with filter by status |
| `POST` | `/api/reset-demo` | Reseed demo database to pristine state |

---

## 🎯 Review & Demonstration Guide

1. **Role Switcher (Top Banner):**
   - Click the persona switcher in the top banner to toggle between **Team 19 students** (`Srija`, `Siddheeshwar`, `Keerthi`), other students (`Aarav`, `Ananya`), and **Organizers** (`Dr. Srinivas`, `ACM Lead`).
2. **Testing Live Seat Pulse & Registration:**
   - On the **Discovery** page, view the live capacity progress bar for each event.
   - Register for an open event (e.g., *HackVasavi 2026*) to instantly receive a QuickCheck QR pass.
3. **Testing Schedule Clash Detection:**
   - Try to register for two events running in overlapping time slots. The system triggers a Schedule Clash warning modal showing the colliding event and requires user confirmation.
4. **Testing Smart Seat Release:**
   - Look at the *Inter-Department Badminton Championship* (full capacity).
   - In *My Registrations*, cancel a ticket. The backend automatically triggers Smart Seat Release and offers the seat to the next waitlisted student with an active claim countdown!
5. **Testing QuickCheck QR Scanner:**
   - Go to **QuickCheck Scanner** (Organizer role).
   - Test by scanning a pass with the webcam, uploading a ticket image, or entering the Pass ID (`ES-2611-HACK01`).
   - The first scan confirms entry and issues an official **Event Passport Stamp**.
   - Scanning the *same pass again* rejects entry with `DUPLICATE SCAN BLOCKED! Already checked in at [Time]`.
6. **Testing Event Passport:**
   - Open **Event Passport** to inspect verified attendance stamps, participation level, and category badges.
7. **Testing Organizer Dashboard & Insights:**
   - Open **Dashboard & Insights** to view total capacity, active registrations, attendance rate %, and seat utilization charts.
   - View the live Attendee Roster with one-click manual check-in controls.
8. **Resetting Demo Data:**
   - Click the **Reset Demo** button in the top navigation bar at any time to reseed the database to its clean state.

---

*Submitted for Full Stack Web Development (FSWD) Course Project Evaluation — Team 19 (CSE-B).*

