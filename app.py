from flask import (
    Flask, render_template, request, jsonify,
    redirect, url_for, session, flash, send_file
)
import sqlite3
import io
import ssl
import smtplib
from datetime import datetime
from email.message import EmailMessage

from chatbot import get_response
from crypto_utils import encrypt_data, decrypt_data

# ===============================
# APP CONFIG
# ===============================
app = Flask(__name__)
app.secret_key = "rightsinsight_secret_key"

SMTP_EMAIL = "rightsinsightofficial@gmail.com"
SMTP_PASSWORD = "wbwrsuzzqlxxrffx"

AUTHORITY_EMAILS = {
    "Labour Commissioner": "labour@gmail.com",
    "Local Police Station": "police@gmail.com",
    "Cyber Crime Cell": "cybercrime@gmail.com",
    "Education Department": "education@gmail.com",
    "Human Rights Commission": "hrc@gmail.com"
}

# ===============================
# DATABASE INITIALIZATION
# ===============================
def init_users_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            role TEXT DEFAULT 'user'
        )
    """)

    authority_users = [
        ("Labour Authority", "labour@gmail.com", "labour@123", "authority"),
        ("Police Authority", "police@gmail.com", "police@123", "authority"),
        ("Cyber Crime Authority", "cybercrime@gmail.com", "cyber@123", "authority"),
        ("Education Authority", "education@gmail.com", "edu@123", "authority"),
        ("Human Rights Authority", "hrc@gmail.com", "hrc@123", "authority"),
    ]

    for a in authority_users:
        c.execute("""
            INSERT OR IGNORE INTO users (name,email,password,role)
            VALUES (?,?,?,?)
        """, a)

    conn.commit()
    conn.close()


def init_complaints_db():
    conn = sqlite3.connect("complaints.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT,
            category TEXT,
            authority TEXT,
            complaint TEXT,
            status TEXT DEFAULT 'PENDING',
            created_at TEXT
        )
    """)

    c.execute("PRAGMA table_info(complaints)")
    columns = [col[1] for col in c.fetchall()]

    if "sent_to_authority" not in columns:
        c.execute("ALTER TABLE complaints ADD COLUMN sent_to_authority INTEGER DEFAULT 0")
    if "sent_at" not in columns:
        c.execute("ALTER TABLE complaints ADD COLUMN sent_at TEXT")
    if "authority_email" not in columns:
        c.execute("ALTER TABLE complaints ADD COLUMN authority_email TEXT")
    if "authority_status" not in columns:
        c.execute("ALTER TABLE complaints ADD COLUMN authority_status TEXT DEFAULT 'RECEIVED'")
    if "authority_reply" not in columns:
        c.execute("ALTER TABLE complaints ADD COLUMN authority_reply TEXT")
    if "authority_updated_at" not in columns:
        c.execute("ALTER TABLE complaints ADD COLUMN authority_updated_at TEXT")
    
    conn.commit()
    conn.close()


def init_evidence_db():
    conn = sqlite3.connect("evidence.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            filename TEXT,
            encrypted_data BLOB,
            uploaded_at TEXT,
            downloaded_at TEXT
        )
    """)
    conn.commit()
    conn.close()


init_users_db()
init_complaints_db()
init_evidence_db()

# ===============================
# EMAIL FUNCTION
# ===============================
def send_email_to_authority(authority, subject, body):
    to_email = AUTHORITY_EMAILS.get(authority)
    if not to_email:
        return False

    msg = EmailMessage()
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)

    return True

# ===============================
# AUTH ROUTES
# ===============================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        try:
            conn = sqlite3.connect("users.db")
            conn.execute(
                "INSERT INTO users (name,email,password) VALUES (?,?,?)",
                (request.form["name"], request.form["email"], request.form["password"])
            )
            conn.commit()
            conn.close()
            return redirect("/login")
        except:
            return "Email already exists"
    return render_template("register.html")



@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        conn = sqlite3.connect("users.db")
        conn.row_factory = sqlite3.Row

        user = conn.execute("""
            SELECT * FROM users WHERE email=? AND password=?
        """, (request.form["email"], request.form["password"])).fetchone()

        conn.close()

        if not user:
            return render_template("login.html", error="Invalid email or password")

        session["user"] = user["name"]
        session["email"] = user["email"]
        session["role"] = user["role"]

        if user["role"] == "admin":
            return redirect("/admin")

        if user["role"] == "authority":
            return redirect("/authority/dashboard")

        return redirect("/")

    return render_template("login.html")
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ===============================
# CHATBOT
# ===============================
@app.route("/chat")
def chat_page():
    return render_template("chat.html")

@app.route("/chatbot", methods=["POST"])
def chatbot():
    reply = get_response(request.json["message"])
    return jsonify({"reply": reply})

# ---------------- EDUCATION PAGE ---------------- 
@app.route("/education")
def education(): return render_template("education.html")

@app.route("/about")
def about(): return render_template("about.html")
# ===============================
# COMPLAINT MODULE
# ===============================
@app.route("/complaint")
def complaint_page():
    if "user" not in session:
        return redirect("/login")
    return render_template("complaint.html")


@app.route("/generate-complaint", methods=["POST"])
def generate_complaint():
    data = request.json
    category = data["category"]
    incident = data["incident"]

    authority_map = {
        "Workplace Discrimination": "Labour Commissioner",
        "Harassment": "Local Police Station",
        "Privacy Violation": "Cyber Crime Cell",
        "Denial of Education": "Education Department",
        "Violation of Fundamental Rights": "Human Rights Commission"
    }

    authority = authority_map.get(category)

    complaint_text = f"""
To,
The {authority}

Subject: Complaint regarding {category}
Respected Sir/Madam,

I, {session['user']}, would like to formally bring to your notice the following incident concerning {category}.

Incident Details:
{incident}
The above incident has caused me significant mental distress and inconvenience. Despite my efforts to resolve the matter amicably, the issue persists and requires immediate attention from the concerned authority.

I kindly request you to investigate the matter and take appropriate action as per the applicable laws and regulations. I am willing to cooperate fully and provide any further information or evidence if required.

Thanking you.


Yours sincerely,
{session['user']}
Email: {session['email']} 
Date: {datetime.now().strftime("%d-%m-%Y")}
"""

    conn = sqlite3.connect("complaints.db")
    conn.execute("""
        INSERT INTO complaints
        (username,email,category,authority,complaint,status,created_at)
        VALUES (?,?,?,?,?,'PENDING',datetime('now'))
    """, (session["user"], session["email"], category, authority, complaint_text))
    conn.commit()
    conn.close()

    return jsonify({"complaint": complaint_text})


@app.route("/mycomplaints")
def my_complaints():
    conn = sqlite3.connect("complaints.db")
    conn.row_factory = sqlite3.Row
    complaints = conn.execute("""
        SELECT * FROM complaints WHERE email=?
        ORDER BY created_at DESC
    """, (session["email"],)).fetchall()
    conn.close()

    return render_template("mycomplaints.html", complaints=complaints)

# ===============================
# SEND TO AUTHORITY
# ===============================
@app.route("/send-to-authority", methods=["POST"])
def send_to_authority_route():
    cid = request.json["id"]

    conn = sqlite3.connect("complaints.db")
    conn.row_factory = sqlite3.Row
    c = conn.execute("SELECT * FROM complaints WHERE id=?", (cid,)).fetchone()

    send_email_to_authority(
        c["authority"],
        "New Approved Complaint",
        c["complaint"]
    )

    conn.execute("""
        UPDATE complaints
        SET sent_to_authority=1,
            sent_at=datetime('now'),
            authority_email=?,
            authority_status='RECEIVED'
        WHERE id=?
    """, (AUTHORITY_EMAILS[c["authority"]], cid))

    conn.commit()
    conn.close()
    return jsonify({"success": True})

# ===============================
# AUTHORITY DASHBOARD
# ===============================
@app.route("/authority/dashboard")
def authority_dashboard():
    if session.get("role") != "authority":
        return redirect("/login")

    conn = sqlite3.connect("complaints.db")
    conn.row_factory = sqlite3.Row

    complaints = conn.execute("""
        SELECT * FROM complaints
        WHERE authority_email = ?
        ORDER BY created_at DESC
    """, (session["email"],)).fetchall()

    conn.close()
    return render_template("authority.html", complaints=complaints)
@app.route("/authority/update", methods=["POST"])
def authority_update():
    if session.get("role") != "authority":
        return redirect("/login")

    complaint_id = request.form.get("id")
    status = request.form.get("status")
    reply = request.form.get("reply")

    if not complaint_id or not status:
        flash("Invalid request", "error")
        return redirect("/authority/dashboard")

    conn = sqlite3.connect("complaints.db")

    # 🔐 ensure this complaint belongs to this authority
    row = conn.execute("""
        SELECT id FROM complaints
        WHERE id=? AND authority_email=?
    """, (complaint_id, session["email"])).fetchone()

    if not row:
        conn.close()
        flash("Unauthorized access", "error")
        return redirect("/authority/dashboard")

    conn.execute("""
        UPDATE complaints
        SET authority_status = ?,
            authority_reply = ?,
            authority_updated_at = datetime('now')
        WHERE id = ?
    """, (status, reply, complaint_id))

    conn.commit()
    conn.close()

    flash("Complaint updated successfully", "success")
    return redirect("/authority/dashboard")


# ===============================
# ADMIN 
# ===============================
@app.route("/admin") 
def admin_dashboard(): 
    if session.get("role") != "admin":
        return "Access Denied" 

    conn = sqlite3.connect("users.db") 
    conn.row_factory = sqlite3.Row 

    # 👤 ONLY NORMAL USERS
    users = conn.execute(
        "SELECT name,email FROM users WHERE role='user'"
    ).fetchall()

    # 🏛️ ONLY AUTHORITIES
    authorities = conn.execute(
        "SELECT name,email FROM users WHERE role='authority'"
    ).fetchall()

    conn.close()

    # EVIDENCE
    conn_e = sqlite3.connect("evidence.db") 
    conn_e.row_factory = sqlite3.Row 
    evidences = conn_e.execute(
        "SELECT user,filename,uploaded_at,downloaded_at FROM evidence"
    ).fetchall() 
    conn_e.close()

    # COMPLAINTS
    conn_c = sqlite3.connect("complaints.db") 
    conn_c.row_factory = sqlite3.Row 
    complaints = conn_c.execute(
        "SELECT * FROM complaints ORDER BY created_at DESC"
    ).fetchall() 
    conn_c.close()

    return render_template(
        "admin.html",
        users=users,
        authorities=authorities,   # 🔥 separate
        evidences=evidences,
        complaints=complaints
    )
@app.route("/admin/approve/<int:id>", methods=["POST"]) 
def approve_complaint(id): 
    if session.get("role") != "admin": return "Access Denied" 
    conn = sqlite3.connect("complaints.db") 
    conn.execute("UPDATE complaints SET status='APPROVED' WHERE id=?", (id,)) 
    conn.commit() 
    conn.close() 
    return redirect("/admin")

@app.route("/admin/reject/<int:id>", methods=["POST"]) 
def reject_complaint(id): 
    if session.get("role") != "admin": return "Access Denied" 
    conn = sqlite3.connect("complaints.db")
    conn.execute("UPDATE complaints SET status='REJECTED' WHERE id=?", (id,))
    conn.commit() 
    conn.close() 
    return redirect("/admin")

# ===============================
#EVIDENCE VAULT
# ===============================
@app.route("/evidence", methods=["GET", "POST"])
def evidence():
    if "user" not in session:
        return redirect("/login")

    # ---------- HANDLE UPLOAD ----------
    if request.method == "POST":
        file = request.files.get("file")
        password = request.form.get("password")

        if not file or file.filename == "" or not password:
            flash("File and password required", "error")
            return redirect("/evidence")

        encrypted = encrypt_data(file.read(), password)

        conn = sqlite3.connect("evidence.db")
        conn.execute("""
            INSERT INTO evidence
            (user, filename, encrypted_data, uploaded_at, downloaded_at)
            VALUES (?, ?, ?, datetime('now'), NULL)
        """, (
            session["user"],
            file.filename,
            sqlite3.Binary(encrypted)
        ))
        conn.commit()
        conn.close()

        flash("Evidence uploaded successfully", "success")

    # ---------- ALWAYS FETCH EVIDENCES ----------
    conn = sqlite3.connect("evidence.db")
    conn.row_factory = sqlite3.Row
    evidences = conn.execute(
        "SELECT * FROM evidence WHERE user=? ORDER BY uploaded_at DESC",
        (session["user"],)
    ).fetchall()
    conn.close()

    return render_template("evidence.html", evidences=evidences)

@app.route("/download/<int:id>", methods=["POST"]) 
def download(id): 
    if "user" not in session: return redirect("/login")
    password = request.form.get("password") 
    conn = sqlite3.connect("evidence.db")
    conn.row_factory = sqlite3.Row 
    row = conn.execute( "SELECT * FROM evidence WHERE id=?", (id,) ).fetchone()
    if not row or row["user"] != session["user"]: 
        conn.close() 
        flash("Unauthorized", "error") 
        return redirect("/evidence")
    try:
          data = decrypt_data(row["encrypted_data"], password) 
    except: 
        conn.close() 
        flash("Wrong password", "error") 
        return redirect("/evidence")
    
    conn.execute( "UPDATE evidence SET downloaded_at=datetime('now') WHERE id=?", (id,) ) 
    conn.commit() 
    conn.close() 
    return send_file( io.BytesIO(data), as_attachment=True, download_name=row["filename"] )

@app.route("/delete/<int:id>", methods=["POST"]) 
def delete(id): 
    if "user" not in session: return redirect("/login") 
    password = request.form.get("password") 
    conn = sqlite3.connect("evidence.db") 
    conn.row_factory = sqlite3.Row 
    row = conn.execute( "SELECT * FROM evidence WHERE id=?", (id,) ).fetchone()
    if not row or row["user"] != session["user"]: 
        conn.close() 
        flash("Unauthorized", "error")
        return redirect("/evidence")
    try:
         decrypt_data(row["encrypted_data"], password)
    except: 
         conn.close() 
         flash("Wrong password", "error") 
         return redirect("/evidence")
    conn.execute("DELETE FROM evidence WHERE id=?", (id,)) 
    conn.commit() 
    conn.close() 
    flash("File deleted", "success") 
    return redirect("/evidence")


@app.route("/admin/delete-authority/<email>", methods=["POST"])
def delete_authority(email):
    if session.get("role") != "admin":
        return "Access Denied"

    conn = sqlite3.connect("users.db")
    cur = conn.cursor()

    # 🔐 Only delete authority (safety check)
    cur.execute("DELETE FROM users WHERE email=? AND role='authority'", (email,))

    conn.commit()
    conn.close()

    return redirect("/admin")

# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    app.run(debug=True)
