from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "secret123"

# Upload folder
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ======================
# MODELS
# ======================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(50))

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student = db.Column(db.String(100))
    date = db.Column(db.String(50))
    status = db.Column(db.String(20))

class Homework(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.String(500))

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student = db.Column(db.String(100))
    marks = db.Column(db.String(200))

class Gallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))

# ======================
# INIT DB
# ======================
with app.app_context():
    db.create_all()

    if not User.query.filter_by(role="TECHADMIN").first():
        db.session.add(User(
            username="TECHADMIN@OWNER",
            password="TEST@4321@1234",
            role="TECHADMIN"
        ))
        db.session.commit()

# ======================
# LOGIN
# ======================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(
            username=request.form["username"],
            password=request.form["password"],
            role=request.form["role"]
        ).first()

        if user:
            session["user"] = user.username
            session["role"] = user.role

            if user.role == "TECHADMIN":
                return redirect("/admin")
            return redirect("/dashboard")

        return "Invalid Login"

    return render_template("login.html")

# ======================
# ADMIN
# ======================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if session.get("role") != "TECHADMIN":
        return "Access Denied"

    if request.method == "POST":
        db.session.add(User(
            username=request.form["username"],
            password=request.form["password"],
            role=request.form["role"]
        ))
        db.session.commit()

    users = User.query.all()
    return render_template("admin.html", users=users)

# ======================
# DASHBOARD
# ======================
@app.route("/dashboard")
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    return render_template(
        "dashboard.html",
        user=session["user"],
        role=session["role"]
    )
# ======================
# ATTENDANCE
# ======================
@app.route("/attendance", methods=["GET","POST"])
def attendance():
    if "user" not in session:
        return redirect("/")

    if session["role"] == "TEACHER" and request.method == "POST":
        db.session.add(Attendance(
            student=request.form["student"],
            date=request.form["date"],
            status=request.form["status"]
        ))
        db.session.commit()

    records = Attendance.query.all()
    return render_template("attendance.html", records=records)

# ======================
# HOMEWORK
# ======================
@app.route("/homework", methods=["GET","POST"])
def homework():
    if "user" not in session:
        return redirect("/")

    if session["role"] == "TEACHER" and request.method == "POST":
        db.session.add(Homework(
            title=request.form["title"],
            content=request.form["content"]
        ))
        db.session.commit()

    data = Homework.query.all()
    return render_template("homework.html", data=data)

# ======================
# REPORT
# ======================
@app.route("/report", methods=["GET","POST"])
def report():
    if "user" not in session:
        return redirect("/")

    if session["role"] == "TEACHER" and request.method == "POST":
        db.session.add(Report(
            student=request.form["student"],
            marks=request.form["marks"]
        ))
        db.session.commit()

    data = Report.query.all()
    return render_template("report.html", data=data)

# ======================
# GALLERY
# ======================
@app.route("/gallery", methods=["GET","POST"])
def gallery():
    if "user" not in session:
        return redirect("/")

    if session["role"] == "TEACHER" and request.method == "POST":
        file = request.files["image"]
        if file:
            path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(path)

            db.session.add(Gallery(filename=file.filename))
            db.session.commit()

    images = Gallery.query.all()
    return render_template("gallery.html", images=images)

# ======================
# LOGOUT
# ======================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
