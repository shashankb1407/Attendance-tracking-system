from flask import Flask, request, redirect, url_for, session
import subprocess
import sys
import os
import pickle
import csv

app = Flask(__name__)
app.secret_key = "supersecretkey"

STATUS_FILE = "status.txt"
ATTENDANCE_FILE = "attendance/attendance.csv"

# ---------------- LOAD VALID STUDENTS ----------------
def load_valid_students():
    if not os.path.exists("labels.pkl"):
        return set()
    with open("labels.pkl", "rb") as f:
        label_map = pickle.load(f)
    return set(label_map.values())

VALID_STUDENTS = load_valid_students()

# ---------------- FACULTY CREDENTIALS ----------------
FACULTY_USERNAME = "admin"
FACULTY_PASSWORD = "admin123"


# ---------------- SUBJECT-WISE STATS ----------------
def calculate_stats():
    stats = {}

    if not os.path.exists(ATTENDANCE_FILE):
        return []

    with open(ATTENDANCE_FILE, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            student = row["Student"].strip()
            subject = row["Subject"].strip()
            status = row["Status"].strip()

            key = (student, subject)

            if key not in stats:
                stats[key] = {
                    "student": student,
                    "subject": subject,
                    "total": 0,
                    "present": 0
                }

            stats[key]["total"] += 1

            if status.lower() == "present":
                stats[key]["present"] += 1

    results = []
    for data in stats.values():
        total = data["total"]
        present = data["present"]
        percentage = round((present / total) * 100, 2) if total else 0

        results.append({
            "student": data["student"],
            "subject": data["subject"],
            "total": total,
            "present": present,
            "percentage": percentage
        })

    return results


# ---------------- STUDENT PAGE ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    global VALID_STUDENTS
    message = ""
    color = ""

    if request.method == "POST":
        student = request.form["student"].strip()
        subject = request.form["subject"].strip()

        VALID_STUDENTS = load_valid_students()

        if student not in VALID_STUDENTS:
            message = "🚫 Access Denied: Student not registered"
            color = "red"
        else:
            subprocess.run(
                [sys.executable, "recognize_attendance.py"],
                input=f"{student}\n{subject}\n",
                text=True
            )

            if os.path.exists(STATUS_FILE):
                with open(STATUS_FILE) as s:
                    status = s.read().strip()

                if status == "PRESENT":
                    message = f"✅ Attendance marked for {student} ({subject})"
                    color = "green"
                elif status == "PROXY":
                    message = "🚨 Proxy detected! Attendance denied"
                    color = "red"
                else:
                    message = "⚠️ Unknown response"
                    color = "orange"

    return f"""
<!DOCTYPE html>
<html>
<head>
<title>Face Recognition Attendance</title>
<style>
body {{
    margin:0;
    height:100vh;
    font-family:Arial;
    background:linear-gradient(135deg,#667eea,#764ba2);
}}
.login-btn {{
    position:absolute;
    top:20px;
    right:30px;
    background:#4c51bf;
    color:white;
    padding:10px 18px;
    border-radius:25px;
    text-decoration:none;
    font-weight:bold;
}}
.card {{
    background:white;
    width:420px;
    padding:40px;
    border-radius:12px;
    box-shadow:0 10px 30px rgba(0,0,0,0.2);
    text-align:center;
    margin:auto;
    margin-top:120px;
}}
input {{
    width:100%;
    padding:12px;
    margin:10px 0;
    border-radius:6px;
    border:1px solid #ccc;
}}
button {{
    width:100%;
    padding:12px;
    background:#667eea;
    border:none;
    color:white;
    border-radius:6px;
    font-size:16px;
}}
.msg {{
    margin-top:20px;
    font-weight:bold;
    color:{color};
}}
</style>
</head>
<body>

<a class="login-btn" href="/faculty">👨‍🏫 Faculty Login</a>

<div class="card">
<h2>Student Attendance</h2>
<form method="post">
<input name="student" placeholder="Student Name" required>
<input name="subject" placeholder="Subject Name" required>
<button type="submit">Mark Attendance</button>
</form>
<div class="msg">{message}</div>
</div>

</body>
</html>
"""


# ---------------- FACULTY LOGIN ----------------
@app.route("/faculty", methods=["GET", "POST"])
def faculty():
    error = ""

    if request.method == "POST":
        if request.form["username"] == FACULTY_USERNAME and request.form["password"] == FACULTY_PASSWORD:
            session["faculty"] = True
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid credentials"

    return f"""
<html>
<head>
<title>Faculty Login</title>
<style>
body {{
    background:linear-gradient(135deg,#667eea,#764ba2);
    font-family:Arial;
}}
.card {{
    width:350px;
    background:white;
    padding:30px;
    margin:150px auto;
    border-radius:12px;
    text-align:center;
}}
input,button {{
    width:100%;
    padding:12px;
    margin:10px 0;
}}
</style>
</head>
<body>
<div class="card">
<h2>Faculty Login</h2>
<form method="post">
<input name="username" placeholder="Username" required>
<input type="password" name="password" placeholder="Password" required>
<button>Login</button>
</form>
<p style="color:red;">{error}</p>
</div>
</body>
</html>
"""


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if not session.get("faculty"):
        return redirect(url_for("faculty"))

    stats = calculate_stats()
    rows = ""

    for s in stats:
        rows += f"""
        <tr>
            <td>{s['student']}</td>
            <td>{s['subject']}</td>
            <td>{s['total']}</td>
            <td>{s['present']}</td>
            <td>{s['percentage']}%</td>
        </tr>
        """

    return f"""
<html>
<head>
<title>Faculty Dashboard</title>
<style>
body {{
    background:linear-gradient(135deg,#667eea,#764ba2);
    font-family:Arial;
    padding:40px;
}}
.card {{
    background:white;
    padding:30px;
    border-radius:12px;
}}
table {{
    width:100%;
    border-collapse:collapse;
}}
th {{
    background:#667eea;
    color:white;
    padding:12px;
}}
td {{
    padding:12px;
    border-bottom:1px solid #ddd;
    text-align:center;
}}
.top {{
    display:flex;
    justify-content:space-between;
    align-items:center;
}}
.add {{
    background:#48bb78;
    color:white;
    padding:10px 16px;
    border-radius:20px;
    text-decoration:none;
    font-weight:bold;
}}
.logout {{
    font-weight:bold;
}}
</style>
</head>
<body>

<div class="card">
<div class="top">
<h2>Faculty Dashboard</h2>
<div>
<a class="add" href="/add-student">➕ Add Student</a>
<a class="logout" href="/logout">Logout</a>
</div>
</div>

<table>
<tr>
<th>Student</th>
<th>Subject</th>
<th>Total Classes</th>
<th>Attended</th>
<th>Attendance %</th>
</tr>
{rows}
</table>

</div>
</body>
</html>
"""


# ---------------- ADD STUDENT (AUTO TRAIN) ----------------
@app.route("/add-student", methods=["GET", "POST"])
def add_student():
    global VALID_STUDENTS

    if not session.get("faculty"):
        return redirect(url_for("faculty"))

    message = ""

    if request.method == "POST":
        student = request.form["student"].strip()

        if student:
            # Capture faces
            subprocess.run(
                [sys.executable, "capture_faces.py"],
                input=student + "\n",
                text=True
            )

            # Train model automatically
            subprocess.run([sys.executable, "train_model.py"])

            # Reload students
            VALID_STUDENTS = load_valid_students()

            message = f"✅ {student} registered and model trained successfully!"

    return f"""
<html>
<head>
<title>Register Student</title>
<style>
body {{
    background:linear-gradient(135deg,#667eea,#764ba2);
    font-family:Arial;
}}
.card {{
    width:400px;
    background:white;
    padding:30px;
    margin:150px auto;
    border-radius:12px;
    text-align:center;
}}
input,button {{
    width:100%;
    padding:12px;
    margin:10px 0;
}}
.msg {{
    margin-top:15px;
    font-weight:bold;
    color:green;
}}
</style>
</head>
<body>

<div class="card">
<h2>Register New Student</h2>
<form method="post">
<input name="student" placeholder="Student Name" required>
<button>Add Student</button>
</form>
<div class="msg">{message}</div>
<a href="/dashboard">⬅ Back to Dashboard</a>
</div>

</body>
</html>
"""


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
