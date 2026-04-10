You are a senior full-stack software engineer and system designer.

Your task is to design and build a production-ready internal IT ticketing system for an organization where all computers are connected on a local network.

The system must be modular, secure, scalable within a LAN environment, and easy to deploy on an internal server.

-----------------------------------
🎯 SYSTEM OVERVIEW
-----------------------------------

Build a role-based IT Helpdesk Ticketing System with the following core idea:

- Staff members belong to predefined offices (e.g., Accounts, HR, PMU, Secretaries).
- When staff create tickets, the system automatically captures their office.
- IT personnel (technicians, interns, ICT officer) manage and resolve tickets.
- Admin dashboard provides analytics and system-wide visibility.

-----------------------------------
👥 USER ROLES & PERMISSIONS
-----------------------------------

Implement strict role-based access control (RBAC):

1. ADMIN
   - Full system control
   - Manage users, roles, and offices
   - View system analytics and reports
   - Configure system settings

2. ICT OFFICER
   - View all tickets across all offices
   - Assign tickets to technicians/interns
   - Monitor ticket progress
   - Access high-level dashboard (not full admin controls)

3. TECHNICIAN
   - Has individual account
   - Can:
     - View tickets assigned to them
     - Update ticket status
     - Add comments/notes
     - Mark tickets as resolved
   - Cannot see system analytics or manage users

4. INTERN
   - Can:
     - View all OPEN tickets
     - View tickets they have handled
     - Update tickets they are working on
   - Limited privileges compared to technicians

5. STAFF (END USERS)
   - Belong to an OFFICE (mandatory field)
   - Can:
     - Register/login
     - Create tickets
     - View status of their own tickets
   - Cannot see other users' tickets

-----------------------------------
🏢 OFFICE-BASED STRUCTURE
-----------------------------------

- Offices are predefined (Accounts, HR, PMU, etc.)
- Each staff user must be linked to one office
- When a ticket is created:
  - Office is automatically attached (no manual input)
- Tickets should be filterable by office in dashboards

-----------------------------------
🎫 TICKET SYSTEM REQUIREMENTS
-----------------------------------

Each ticket must include:

- Ticket ID (auto-generated)
- Title
- Description
- Office (auto-attached)
- Created by (user)
- Assigned to (technician/intern)
- Status:
  - Open
  - In Progress
  - Pending
  - Resolved
  - Closed
- Priority:
  - Low
  - Medium
  - High
- Timestamps:
  - Created At
  - Updated At
  - Resolved At

Additional features:

- Comment system (threaded or simple log)
- Activity log (audit trail of actions)
- File attachments (optional but recommended)

-----------------------------------
📊 DASHBOARDS
-----------------------------------

ADMIN DASHBOARD:
- Total tickets
- Tickets by status
- Tickets by office
- Tickets by technician
- Resolution time metrics
- Graphs (daily/weekly trends)

ICT OFFICER DASHBOARD:
- All tickets overview
- Unassigned tickets
- Technician workload
- Quick assignment interface

TECHNICIAN DASHBOARD:
- Assigned tickets
- Status breakdown
- Recent activity

INTERN DASHBOARD:
- Open tickets
- Tickets handled by them

STAFF DASHBOARD:
- Their submitted tickets
- Status tracking

-----------------------------------
🔐 AUTHENTICATION & SECURITY
-----------------------------------

- Secure login system (hashed passwords, e.g., bcrypt)
- Role-based route protection
- Session or JWT authentication
- Input validation and sanitization
- Prevent unauthorized access to tickets

-----------------------------------
🧱 TECH STACK (PREFERRED)
-----------------------------------

Frontend:
- Next.js (App Router)
- Tailwind CSS

Backend:
- Node.js (Express or Next.js API routes)

Database:
- PostgreSQL or MySQL

ORM:
- Prisma (preferred)

-----------------------------------
🗃️ DATABASE DESIGN (IMPORTANT)
-----------------------------------

Design normalized tables for:

- Users
- Roles
- Offices
- Tickets
- Comments
- Activity Logs

Ensure:
- Proper foreign keys
- Indexing for performance
- Scalable schema

-----------------------------------
🔄 WORKFLOW LOGIC
-----------------------------------

1. Staff creates ticket → status = Open
2. ICT Officer assigns → status = In Progress
3. Technician/Intern works → updates status
4. When resolved → status = Resolved
5. Optionally closed after verification

-----------------------------------
🎨 UI/UX REQUIREMENTS
-----------------------------------

- Clean, modern dashboard design
- Role-based navigation menus
- Tables with filters (status, office, priority)
- Modal or page for ticket details
- Real-time-like updates (polling is acceptable)

-----------------------------------
🚀 DEPLOYMENT (FINAL STAGE)
-----------------------------------

- Must be deployable on:
  - Local server (Linux preferred)
- Accessible via internal IP
- Environment variables for config
- Database hosted locally

-----------------------------------
🧪 DEVELOPMENT APPROACH
-----------------------------------

Follow this order:

1. Setup project structure
2. Database schema (Prisma)
3. Authentication system
4. Role-based access control
5. Ticket CRUD operations
6. Dashboards per role
7. Comments & activity logs
8. Analytics (admin dashboard)
9. UI refinement
10. Deployment configuration

-----------------------------------
📦 OUTPUT REQUIREMENTS
-----------------------------------

- Provide clean, modular code
- Use best practices
- Add comments where necessary
- Include setup instructions
- Include sample seed data

-----------------------------------
⚡ BONUS FEATURES (IF POSSIBLE)
-----------------------------------

- Email notifications (or simulated internal notifications)
- SLA tracking
- Ticket escalation rules
- Search functionality
- Export reports (CSV/PDF)

-----------------------------------

Start by:
1. Designing the database schema (Prisma)
2. Then scaffold the project structure
3. Then implement authentication and roles

Do not skip steps. Build incrementally and explain key decisions.