import os
os.environ['MPLCONFIGDIR'] = '/tmp'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs('docs/images', exist_ok=True)

# ----------------- 1. User Journey Diagram -----------------
fig, ax = plt.subplots(figsize=(10, 5), dpi=200)
ax.set_facecolor('#F8FAFC')
fig.patch.set_facecolor('#F8FAFC')

# Nodes
steps = [
    ("1. Browse Catalog", "Filter by Category\n& Keyword Search", "#EA580C"),
    ("2. Inspect Event", "View Live Seat Pulse\n& Capacity Meter", "#D97706"),
    ("3. Register / Check", "Capacity Validation\n& Clash Warning", "#2563EB"),
    ("4. Get QR Pass", "Cryptographic Pass\nSaved in Registrations", "#059669"),
    ("5. Entrance Scan", "Organizer Scans Pass\nDuplicate Scan Blocked", "#7C3AED"),
    ("6. Event Passport", "Verified Stamp Awarded\nEngagement Tier Badge", "#DB2777")
]

for i, (title, desc, color) in enumerate(steps):
    x = i * 1.55 + 0.2
    y = 0.5
    # Box
    rect = patches.FancyBboxPatch((x, y), 1.35, 1.4, boxstyle="round,pad=0.1",
                                  facecolor='white', edgecolor=color, linewidth=2, zorder=2)
    ax.add_patch(rect)
    # Header bar
    header_rect = patches.FancyBboxPatch((x, y + 0.95), 1.35, 0.45, boxstyle="round,pad=0.05",
                                         facecolor=color, edgecolor=color, linewidth=1, zorder=3)
    ax.add_patch(header_rect)
    ax.text(x + 0.675, y + 1.15, title, ha='center', va='center', color='white',
            fontweight='bold', fontsize=8, zorder=4)
    ax.text(x + 0.675, y + 0.5, desc, ha='center', va='center', color='#334155',
            fontsize=7, zorder=4)

    # Arrow to next step
    if i < len(steps) - 1:
        ax.annotate('', xy=(x + 1.55, y + 0.7), xytext=(x + 1.35, y + 0.7),
                    arrowprops=dict(arrowstyle="-|>", color='#94A3B8', lw=2, mutation_scale=12))

# Alt loop for Smart Seat Release
ax.annotate('Cancellation', xy=(3.8, 0.2), xytext=(4.8, 0.2),
            arrowprops=dict(arrowstyle="<-", color='#E11D48', lw=1.5, linestyle='--'))
ax.text(4.3, 0.05, "Smart Seat Release (Waitlist Claim Window)", ha='center', color='#E11D48', fontsize=7, fontweight='bold')

ax.set_xlim(0, 9.6)
ax.set_ylim(-0.2, 2.3)
ax.axis('off')
plt.title("EventSphere: End-to-End Student Participation Journey", fontsize=11, fontweight='bold', pad=10, color='#0F172A')
plt.tight_layout()
plt.savefig('docs/images/user_journey_flow.png', dpi=200, bbox_inches='tight')
plt.close()

# ----------------- 2. Wireframe Sketches Composite -----------------
fig, axes = plt.subplots(2, 2, figsize=(10, 7), dpi=200)
fig.patch.set_facecolor('#F8FAFC')

# Wireframe 1: Discovery
ax1 = axes[0, 0]
ax1.set_facecolor('white')
ax1.set_title("Wireframe 1: Student Discovery Hub", fontsize=9, fontweight='bold', color='#1E293B')
ax1.add_patch(patches.Rectangle((0.05, 0.85), 0.9, 0.1, facecolor='#EA580C', edgecolor='none')) # navbar
ax1.text(0.1, 0.9, "EventSphere | Discover", color='white', fontsize=7, fontweight='bold', va='center')
ax1.add_patch(patches.Rectangle((0.05, 0.7), 0.9, 0.12, facecolor='#FFF7ED', edgecolor='#FDBA74')) # hero
ax1.text(0.5, 0.76, "Search & Category Filters [Tech | Cult | Sports | Wksp]", color='#9A3412', fontsize=6, ha='center')
for c in range(3): # 3 cards
    cx = 0.05 + c * 0.31
    ax1.add_patch(patches.Rectangle((cx, 0.15), 0.28, 0.5, facecolor='#F1F5F9', edgecolor='#CBD5E1', lw=1))
    ax1.add_patch(patches.Rectangle((cx + 0.02, 0.45), 0.24, 0.16, facecolor='#E2E8F0', edgecolor='none'))
    ax1.text(cx + 0.04, 0.38, "Event Title", fontsize=6, fontweight='bold')
    ax1.add_patch(patches.Rectangle((cx + 0.04, 0.28), 0.2, 0.04, facecolor='#10B981', edgecolor='none')) # pulse
    ax1.text(cx + 0.04, 0.33, "Live Seat Pulse: 80% Full", fontsize=5, color='#047857')
    ax1.add_patch(patches.Rectangle((cx + 0.14, 0.18), 0.1, 0.06, facecolor='#EA580C', edgecolor='none'))
    ax1.text(cx + 0.19, 0.21, "Register", fontsize=5, color='white', ha='center')
ax1.set_xlim(0, 1)
ax1.set_ylim(0, 1)
ax1.axis('off')

# Wireframe 2: Event Details & Clash Modal
ax2 = axes[0, 1]
ax2.set_facecolor('white')
ax2.set_title("Wireframe 2: Event Details & Conflict Warning", fontsize=9, fontweight='bold', color='#1E293B')
ax2.add_patch(patches.Rectangle((0.05, 0.85), 0.9, 0.1, facecolor='#EA580C', edgecolor='none'))
ax2.add_patch(patches.Rectangle((0.05, 0.45), 0.9, 0.35, facecolor='#F8FAFC', edgecolor='#E2E8F0'))
ax2.text(0.1, 0.75, "HackVasavi 2026: 24-Hour Campus Hackathon", fontsize=7, fontweight='bold')
ax2.text(0.1, 0.68, "Date: Nov 12, 10:00 AM | Venue: Ramanujan Block | Club: ACM", fontsize=6, color='#64748B')
ax2.add_patch(patches.Rectangle((0.1, 0.55), 0.8, 0.08, facecolor='#FEF3C7', edgecolor='#F59E0B'))
ax2.text(0.5, 0.59, "Capacity: 50 | Registered: 42 | Available: 8 [Filling Fast]", fontsize=6, color='#92400E', ha='center')
# Modal Overlay
ax2.add_patch(patches.Rectangle((0.2, 0.1), 0.6, 0.35, facecolor='white', edgecolor='#F59E0B', lw=2))
ax2.add_patch(patches.Rectangle((0.2, 0.38), 0.6, 0.07, facecolor='#F59E0B', edgecolor='none'))
ax2.text(0.5, 0.415, "Schedule Clash Warning!", color='white', fontsize=6, fontweight='bold', ha='center')
ax2.text(0.5, 0.28, "You already registered for an overlapping event!\nProceed or Cancel?", fontsize=5, color='#334155', ha='center')
ax2.add_patch(patches.Rectangle((0.25, 0.15), 0.22, 0.07, facecolor='#E2E8F0', edgecolor='none'))
ax2.text(0.36, 0.185, "Cancel", fontsize=5, ha='center')
ax2.add_patch(patches.Rectangle((0.53, 0.15), 0.22, 0.07, facecolor='#F59E0B', edgecolor='none'))
ax2.text(0.64, 0.185, "Override", fontsize=5, color='white', ha='center')
ax2.set_xlim(0, 1)
ax2.set_ylim(0, 1)
ax2.axis('off')

# Wireframe 3: My Registrations & QR Pass
ax3 = axes[1, 0]
ax3.set_facecolor('white')
ax3.set_title("Wireframe 3: My Registrations & QuickCheck Pass", fontsize=9, fontweight='bold', color='#1E293B')
ax3.add_patch(patches.Rectangle((0.05, 0.85), 0.9, 0.1, facecolor='#EA580C', edgecolor='none'))
ax3.text(0.1, 0.77, "My Passes | Waitlists | Attended History", fontsize=6, fontweight='bold', color='#475569')
# QR Pass ticket mockup
ax3.add_patch(patches.Rectangle((0.25, 0.12), 0.5, 0.6, facecolor='white', edgecolor='#CBD5E1', lw=1.5))
ax3.add_patch(patches.Rectangle((0.25, 0.62), 0.5, 0.1, facecolor='#EA580C', edgecolor='none'))
ax3.text(0.5, 0.67, "QuickCheck Entry Pass", color='white', fontsize=6, fontweight='bold', ha='center')
ax3.add_patch(patches.Rectangle((0.37, 0.32), 0.26, 0.26, facecolor='#0F172A', edgecolor='none')) # QR code
ax3.text(0.5, 0.45, "[QR CODE]", color='white', fontsize=6, ha='center')
ax3.text(0.5, 0.25, "Pass ID: ES-2611-HACK01\nG Srija Santoshini (1602-24-733-117)", fontsize=5, ha='center', color='#334155')
ax3.text(0.5, 0.16, "Status: VALID ENTRY (Single-Use)", fontsize=5, color='#047857', fontweight='bold', ha='center')
ax3.set_xlim(0, 1)
ax3.set_ylim(0, 1)
ax3.axis('off')

# Wireframe 4: Organizer Dashboard & Scanner
ax4 = axes[1, 1]
ax4.set_facecolor('white')
ax4.set_title("Wireframe 4: Organizer Analytics & Scanner", fontsize=9, fontweight='bold', color='#1E293B')
ax4.add_patch(patches.Rectangle((0.05, 0.85), 0.9, 0.1, facecolor='#0F172A', edgecolor='none'))
ax4.text(0.1, 0.9, "Organizer Portal: Faculty & Club Lead", color='white', fontsize=7, fontweight='bold', va='center')
# KPI row
for k in range(4):
    kx = 0.05 + k * 0.23
    ax4.add_patch(patches.Rectangle((kx, 0.66), 0.21, 0.15, facecolor='#F1F5F9', edgecolor='#E2E8F0'))
ax4.text(0.15, 0.73, "6 Events", fontsize=5, fontweight='bold', ha='center')
ax4.text(0.38, 0.73, "88% Seats", fontsize=5, fontweight='bold', ha='center')
ax4.text(0.61, 0.73, "75% Attend", fontsize=5, fontweight='bold', ha='center')
ax4.text(0.84, 0.73, "QR Station", fontsize=5, fontweight='bold', ha='center')
# Attendee Table Mockup
ax4.add_patch(patches.Rectangle((0.05, 0.15), 0.9, 0.46, facecolor='white', edgecolor='#E2E8F0'))
ax4.add_patch(patches.Rectangle((0.05, 0.52), 0.9, 0.09, facecolor='#F8FAFC', edgecolor='#E2E8F0'))
ax4.text(0.08, 0.56, "Pass Code | Student Name | Roll No | Check-in Status | Action", fontsize=5, color='#475569')
for r in range(3):
    ry = 0.42 - r * 0.1
    ax4.text(0.08, ry, f"ES-2611-0{r+1} | Student {r+1} | 1602-24-733-0{r+1} | Confirmed | [Check In]", fontsize=5, color='#334155')
ax4.set_xlim(0, 1)
ax4.set_ylim(0, 1)
ax4.axis('off')

plt.tight_layout()
plt.savefig('docs/images/wireframes_sketch.png', dpi=200, bbox_inches='tight')
plt.close()

print("Generated diagrams successfully in docs/images/")
