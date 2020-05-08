from flask import Flask, request, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, LoginManager, UserMixin, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://joshedgar:is668db1@joshedgar.mysql.pythonanywhere-services.com/joshedgar$gradebook"
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

app.secret_key = "is668secretkey-whocaresthisisadevenvironment"
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):

    __tablename__ = "instructors"

    username = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))
    id = db.Column(db.Integer, primary_key=True)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def get_id(self):
        return self.username

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(username=user_id).first()

class Student(db.Model):

    __tablename__ = "students"

    first_name = db.Column(db.String(4096))
    last_name = db.Column(db.String(4096))
    major_program = db.Column(db.String(4096))
    email_address = db.Column(db.String(4096))
    id = db.Column(db.Integer, primary_key=True)

class Assignment(db.Model):

    __tablename__ = "assignments"

    assignment_name = db.Column(db.String(4096))
    assignment_desc = db.Column(db.String(4096))
    id = db.Column(db.Integer, primary_key=True)

class Grade(db.Model):

    __tablename__ = "grades"

    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True)
    points = db.Column(db.Integer)
    id = db.Column(db.Integer, primary_key=True)
    assignment = db.relationship('Assignment', foreign_keys=assignment_id)
    student = db.relationship('Student', foreign_keys=student_id)

def getstudentavg(studentid):
    grades = Grade.query.filter_by(student_id=studentid).all()
    if(Grade.query.filter_by(student_id=studentid).count() != 0):
        i = 0
        j = 0
        for scores in grades:
            i = i + scores.points
            j = j + 1
        k = i / j
        return round(k)
    return "0"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("main_page.html", students=Student.query.order_by(Student.last_name).all(), assignments=Assignment.query.all())
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route("/student_add", methods=["POST"])
def student_add():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    addstudent = Student(first_name=request.form["first_name"].capitalize(), last_name=request.form["last_name"].capitalize(), major_program=request.form["major_program"].capitalize(), email_address=request.form["email_address"])
    db.session.add(addstudent)
    db.session.commit()
    return redirect(url_for('index'))

@app.route("/student_delete", methods=["GET"])
def student_delete():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    studentid = request.args.get('id')
    delstudent = Student.query.filter_by(id=studentid).first()
    db.session.delete(delstudent)
    db.session.commit()
    return redirect(url_for('index'))

@app.route("/assignment_add", methods=["POST"])
def assignment_add():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    addassignment = Assignment(assignment_name=request.form["assignment_name"].capitalize(), assignment_desc=request.form["assignment_desc"].capitalize())
    db.session.add(addassignment)
    db.session.commit()
    return redirect(url_for('index'))

@app.route("/assignment_delete", methods=["GET"])
def assignment_delete():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    assignmentid = request.args.get('id')
    delassignment = Assignment.query.filter_by(id=assignmentid).first()
    db.session.delete(delassignment)
    db.session.commit()
    return redirect(url_for('index'))

@app.route("/student_grades", methods=["GET"])
def student_grades():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    studentid = request.args.get('id')
    grades = Grade.query.filter_by(student_id=studentid).all()
    if(Grade.query.filter_by(student_id=studentid).count() != 0):
        i = 0
        j = 0
        for scores in grades:
            i = i + scores.points
            j = j + 1
        k = i / j
        return render_template("student_grades.html", grades=Grade.query.filter_by(student_id=studentid).all(), student=Student.query.filter_by(id=studentid).first(), gradeavg=round(k))
    return render_template("student_grades.html", grades=Grade.query.filter_by(student_id=studentid).all(), student=Student.query.filter_by(id=studentid).first(), gradeavg=0)

@app.route("/assignment_grades", methods=["GET"])
def assignment_grades():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    assignmentid = request.args.get('id')
    grades = Grade.query.filter_by(assignment_id=assignmentid).all()
    if(Grade.query.filter_by(assignment_id=assignmentid).count() != 0):
        i = 0
        j = 0
        for scores in grades:
            i = i + scores.points
            j = j + 1
        k = i / j
        return render_template("assignment_grades.html", grades=Grade.query.filter_by(assignment_id=assignmentid).join(Student).order_by(Student.last_name).all(), assignment=Assignment.query.filter_by(id=assignmentid).first(), gradeavg=round(k))
    return render_template("assignment_grades.html", grades=Grade.query.filter_by(assignment_id=assignmentid).join(Student).order_by(Student.last_name).all(), assignment=Assignment.query.filter_by(id=assignmentid).first(), gradeavg=0)

@app.route("/roster_detailed", methods=["GET"])
def roster_detailed():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template("roster_detailed.html", students=Student.query.order_by(Student.last_name).all(), getaverage=getstudentavg)

@app.route("/grade_assignment", methods=["GET"])
def grade_assignment():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template("grade_assignment.html", students=Student.query.order_by(Student.last_name).all(), assignments=Assignment.query.order_by(Assignment.assignment_name).all())

@app.route("/grade_assignment_do", methods=["POST"])
def grade_assignment_do():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    addgrade = Grade(assignment_id=request.form["assignment"], student_id=request.form["student"], points=request.form["points"])
    db.session.add(addgrade)
    db.session.commit()
    return redirect(url_for('index'))

@app.route("/modify_grade", methods=["GET"])
def modify_grade():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    gradeid = request.args.get('id')
    grade = Grade.query.filter_by(id=gradeid).first()
    studentid = grade.student.id
    assignmentid = grade.assignment.id
    return render_template("modify_grade.html", grade=grade, student=Student.query.filter_by(id=studentid).first(), assignment=Assignment.query.filter_by(id=assignmentid).first())

@app.route("/modify_grade_do", methods=["POST"])
def modify_grade_do():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    grade = Grade.query.filter_by(id=request.form["gradeid"]).first()
    grade.points = request.form["new_grade"]
    db.session.commit()
    return redirect(url_for('index'))

@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login_page.html", error=False)

    user = load_user(request.form["username"])
    if user is None:
        return render_template("login_page.html", error=True)

    if not user.check_password(request.form["password"]):
        return render_template("login_page.html", error=True)

    login_user(user)
    return redirect(url_for('index'))

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
