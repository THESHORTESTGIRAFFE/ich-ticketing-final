# ICH Ticketing System — Staff Training Guide

**Version 1.0 | April 2026**

---

## Contents
1. [Getting Started](#1-getting-started)
2. [Logging In](#2-logging-in)
3. [Staff — Submitting a Ticket](#3-staff--submitting-a-ticket)
4. [Staff — Tracking Your Tickets](#4-staff--tracking-your-tickets)
5. [ICT Officer — Managing the Queue](#5-ict-officer--managing-the-queue)
6. [Technician & Intern — Working Tickets](#6-technician--intern--working-tickets)
7. [Administrator — User Management](#7-administrator--user-management)
8. [Administrator — Reports](#8-administrator--reports)
9. [FAQ](#9-faq)

---

## 1. Getting Started

Open your web browser and navigate to:

```
http://[server-ip]:5000
```

*(Your IT administrator will provide the exact address on your local network.)*

You will be presented with the login screen.

---

## 2. Logging In

1. Enter your **email address** and **password**.
2. Click **Sign In**.

> **First time?** Click **Register here** below the Sign In button to create your account.  
> You will need to select your department from the dropdown — if your department is not listed, contact the ICT administrator.

**Password requirements for new accounts:**
- Minimum 8 characters
- At least one uppercase letter
- At least one number

**Locked out?** After 5 failed login attempts, the system will lock you out for 15 minutes. Wait and try again, or contact the administrator to reset your password.

---

## 3. Staff — Submitting a Ticket

Only regular staff members can open tickets. ICT staff use the system to *respond to* tickets, not create them.

### Steps:

1. After logging in, click the **"New Ticket"** button on your dashboard (or in the navigation menu).

2. Fill in the form:
   - **Title** — Short description of the fault (at least 5 characters). Example: *"Printer not responding in Block A"*
   - **Description** — Give as much detail as possible: what happened, when it started, what you have already tried.
   - **Priority** — Select Low, Medium, or High based on urgency.

3. Click **Submit Ticket**.

Your ticket will appear on your dashboard immediately and will be assigned to a technician by the ICT Officer.

### Ticket ID Format
Every ticket gets a unique reference code in the format:  
**`{department}{date}{time}`** — e.g., `ACC100426_1011`

Keep this code when following up with ICT staff.

---

## 4. Staff — Tracking Your Tickets

Your dashboard shows all tickets you have submitted.

| Status | Meaning |
|---|---|
| **OPEN** | Submitted, waiting to be assigned |
| **IN PROGRESS** | Assigned to a technician who is working on it |
| **PENDING** | Waiting on something (e.g., parts, information from you) |
| **RESOLVED** | The technician has resolved the fault |
| **CLOSED** | Confirmed closed |

Click any ticket to view its full history, comments from the technician, and the current status.

You cannot see or access other staff members' tickets.

---

## 5. ICT Officer — Managing the Queue

The ICT Officer dashboard shows all **unassigned (OPEN)** tickets from all departments.

### Assigning a ticket:
1. Click on a ticket to open it.
2. In the **"Assign Ticket"** panel on the right, select a Technician or Intern from the dropdown.
3. Click **Assign**. The ticket status automatically changes to **IN PROGRESS** and the assignee can now see it on their dashboard.

> ICT Officers cannot create tickets themselves — they manage and delegate them.

---

## 6. Technician & Intern — Working Tickets

Your dashboard shows tickets that have been assigned to you.

### Updating a ticket:
1. Click a ticket to open it.
2. **Add a comment** — use the comment box to update the staff member on progress, ask for more information, or describe what you did.
3. **Update the status** — use the status dropdown to change the ticket to:
   - `IN_PROGRESS` — you have started working on it
   - `PENDING` — waiting for something
   - `RESOLVED` — fault is fixed
   - `CLOSED` — confirmed done

> ⚡ **Important:** The timestamp of your **first comment or status update** is recorded as the *response time* and will appear on the administrator's performance report. Respond promptly!

---

## 7. Administrator — User Management

Go to **Users** in the top navigation bar.

### Actions available for each user:

| Action | Effect |
|---|---|
| **Set Role** | Change the user's role (Staff, Intern, Technician, ICT Officer, Admin) |
| **Reset PW** | Set a new password for the user (minimum 6 characters) |
| **Suspend** | Temporarily block login — user sees a "suspended" message |
| **Unsuspend** | Re-enable a suspended account |
| **Deactivate** | Permanently block login — use for staff who have left |
| **Re-activate** | Restore a deactivated account |

> You cannot modify your own account from this panel (prevents accidental self-lockout).

### Adding a new user:
1. Click the **"Add User"** button (top right).
2. Fill in: Full Name, Email, Role, Office, Initial Password.
3. Click **Create User**.

The new user can log in immediately with the provided credentials.

---

## 8. Administrator — Reports

Go to **Report** in the top navigation bar.

The report shows all tickets that were assigned to Interns and Technicians, along with how long each one took to resolve.

### Filtering by date:
- Use the **From** and **To** date pickers to limit the report to a specific period.
- Dates cannot be set in the future or more than one year in the past.
- Click **Filter** to apply. Click **Clear** to reset to all time.

### Printing:
1. Click the **Print Report** button.
2. In the browser print dialog:
   - Set **Destination** to your printer or "Save as PDF".
   - Under **More settings**, turn off **"Headers and footers"** to remove the URL line from the printout.
3. Click **Print**.

The printout includes:
- ICH banner (full width)
- Report period and generation time
- Ticket table (Fault, Assigned To, Status, Time to Resolve)
- Summary totals (total / resolved / pending / average resolution time)
- ICT Officer name and signature block

---

## 9. FAQ

**Q: I can't see the "New Ticket" button.**  
A: ICT staff (ICT Officer, Technician, Intern) cannot create tickets. Only regular Staff and Admins can. If your role is wrong, contact the Administrator.

**Q: My office is not in the dropdown on registration.**  
A: Contact the ICT Administrator to add your office to the system. They can do this from the **Offices** menu.

**Q: I forgot my password.**  
A: Contact the ICT Administrator — they can reset your password from the User Management panel.

**Q: The system logged me out automatically.**  
A: For security, sessions expire after 8 hours of inactivity. Simply log back in.

**Q: Can I delete a ticket?**  
A: Currently, tickets cannot be deleted — only closed. This maintains an audit trail of all issues reported.

---

*For technical issues with the system itself, contact your ICT department.*
