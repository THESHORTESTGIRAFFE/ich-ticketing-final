# ICH Ticketing System — Security & Failsafe Measures

> Generated: April 2026  
> For follow-up by the system administrator or IT lead.

---

## ✅ Implemented (Active Now)

### 1. Login Brute-Force Lockout
**Where:** `app.py → login()`  
After **5 consecutive failed login attempts** from the same browser session, the account is locked for **15 minutes**. The remaining attempts are shown on each failure so users know where they stand.  
- Resets automatically on successful login.  
- Counter is stored in the encrypted server-side session cookie.

---

### 2. Session Security
**Where:** `app.py` — app config block  
| Setting | Value | Effect |
|---|---|---|
| `PERMANENT_SESSION_LIFETIME` | 8 hours | Session expires after 8 hours of inactivity |
| `SESSION_COOKIE_HTTPONLY` | True | JavaScript cannot read the session cookie |
| `SESSION_COOKIE_SAMESITE` | Lax | Prevents cross-site request forgery (CSRF) from external sites |
| `SECRET_KEY` | From `SECRET_KEY` env var | Rotating this key invalidates all active sessions |

> [!IMPORTANT]
> Set `SECRET_KEY` as a real environment variable before production deployment. The fallback value in code is **not safe** for production.

---

### 3. HTTP Security Headers
**Where:** `app.py → set_security_headers()` (runs on every response)  
| Header | Value | Protection |
|---|---|---|
| `X-Content-Type-Options` | `nosniff` | Prevents MIME-type sniffing attacks |
| `X-Frame-Options` | `SAMEORIGIN` | Prevents clickjacking in iframes |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Limits referrer data leakage |

---

### 4. Open Redirect Guard
**Where:** `app.py → login()`  
The `?next=` redirect parameter (used to return users to their intended page after login) is now validated. Any redirect that does not start with `/` (e.g., an external URL like `http://evil.com`) is silently discarded, preventing phishing via redirect chaining.

---

### 5. Password Policy (Registration)
**Where:** `app.py → register()`  
New accounts must meet all of:
- Minimum **8 characters**
- At least one **uppercase letter**
- At least one **number**

Enforced server-side — cannot be bypassed by disabling browser validation.

---

### 6. Input Sanitization
**Where:** `app.py → sanitize()` — applied on all user-submitted text  
All free-text fields (name, email, ticket title, description, comments) are:
- Stripped of leading/trailing whitespace
- Cleared of null bytes and ASCII control characters
- Truncated to a maximum safe length (255 chars for names/emails, 2000 chars for descriptions)

This prevents garbage data and a class of injection-style attacks.

---

### 7. Email Format Validation
**Where:** `app.py → register()`  
Email addresses are validated against a regex pattern server-side before the account is created. Malformed or obviously fake emails are rejected with a clear message.

---

### 8. Office ID Integrity Check
**Where:** `app.py → register()`  
The `officeId` submitted during registration is verified to exist in the database before use. This prevents crafted POST requests from assigning a user to a non-existent office or bypassing the dropdown restriction.

---

### 9. Role-Based Access Control (RBAC)
**Where:** All protected routes in `app.py`  
Every route checks `current_user.role` before processing. Key rules:
- `ICT_OFFICER`, `TECHNICIAN`, `INTERN` → **cannot create tickets**
- `STAFF` → **cannot view other users' tickets** (enforced on `view_ticket`)
- Only `ADMIN` and `ICT_OFFICER` → can assign tickets
- Only `ADMIN` → can access `/admin/*` routes
- Admin **cannot modify their own account** from the user table (prevents self-lockout)

---

### 10. Account Status Gates
**Where:** `app.py → login()`  
Suspended or deactivated accounts receive a specific error message and **cannot log in**, even with correct credentials. The admin can toggle these states at any time from the Users panel.

---

### 11. Date Range Validation (Report Filter)
**Where:** `admin_report.html` + `app.py → admin_report()`  
- Browser: `min` and `max` attributes on date inputs block future dates and dates older than 1 year
- Server: Invalid or unparseable date strings are silently ignored (no crash, defaults to full date range)

---

### 12. Ticket Input Validation
**Where:** `app.py → new_ticket()`  
- Title must be at least **5 characters**
- Priority must be one of `LOW`, `MEDIUM`, `HIGH` (defaults to MEDIUM if tampered)
- User must have an assigned office before a ticket can be created

---

## 🔲 Follow-Up Items (Not Yet Implemented)

These require additional infrastructure or decisions but are strongly recommended before going live on a wider network.

| # | Item | Priority | Notes |
|---|---|---|---|
| 1 | **HTTPS / TLS** | 🔴 Critical | All traffic is currently unencrypted. Deploy behind nginx with a self-signed or Let's Encrypt certificate. |
| 2 | **CSRF Token on Forms** | 🔴 Critical | Add `Flask-WTF` or manually generate a `csrf_token` hidden input on all POST forms. SameSite=Lax is partial mitigation only. |
| 3 | **Production WSGI Server** | 🔴 Critical | Replace Flask dev server with `gunicorn` or `uwsgi`. The dev server is single-threaded and not safe for multi-user use. |
| 4 | **Production SECRET_KEY** | 🔴 Critical | Generate with `python -c "import secrets; print(secrets.token_hex(32))"` and inject via environment variable. |
| 5 | **Password Reset via Email** | 🟡 Medium | Currently only admin can reset passwords. A self-service flow via email token would reduce admin burden. Requires SMTP config. |
| 6 | **Email Verification on Register** | 🟡 Medium | New accounts can use any email. Verification ensures the address is real and owned by the registrant. |
| 7 | **Audit Log Review UI** | 🟡 Medium | `ActivityLog` entries are recorded but there is no admin UI to view them. A log viewer page would improve accountability. |
| 8 | **Database Backups** | 🟡 Medium | Schedule automated nightly backups of the SQLite file (or MySQL database). Store off-device. |
| 9 | **Comment Content Validation** | 🟢 Low | Comments are sanitized but have no minimum length check — empty comment submissions are possible. |
| 10 | **Session Fixation Protection** | 🟢 Low | Flask-Login regenerates session on login by default. Confirm this is not disabled in any custom middleware if added later. |
| 11 | **Inactive Account Auto-Deactivation** | 🟢 Low | A cron job could automatically deactivate accounts that haven't logged in for 90+ days. |

---

## Running the App Securely

```bash
# Set required environment variables first
export SECRET_KEY="your-real-secret-here"
export DATABASE_URL="mysql+pymysql://user:pass@localhost/ich_ticketing"

# Run via gunicorn (production)
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Or for local development only
python3 app.py
```
