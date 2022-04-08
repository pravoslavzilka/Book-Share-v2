from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from database import db_session
from models import Grade, Student, Book, Tag, User
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user, login_user, logout_user
import openpyxl
import random
import string


student_bp = Blueprint("student_bp",__name__,template_folder="templates")

ALLOWED_EXTENSIONS = {'xlsx','xlsm','xltx','xltm'}
UPLOAD_FOLDER = '/path/files'


@student_bp.route("/view/<int:student_id>/")
@login_required
def view_student(student_id):
    try:
        student = Student.query.filter(Student.id == student_id).first()
    except OverflowError:
        flash("Neplatný kód študenta", "danger")
        return redirect(url_for("student_bp.search_student"))

    if student:
        grades = Grade.query.all()
        return render_template("student/student_page.html",student=student, grades=grades)
    flash("Neplatný kód študenta","danger")
    return redirect(url_for("student_bp.search_student"))


@student_bp.route("/account/")
@login_required
def student_account():

    grades = Grade.query.all()
    return render_template("student/student_page.html", student=current_user, grades=grades)


@student_bp.route("/<int:student_id>/rent_book/",methods=["POST"])
def rent_book(student_id):
    try:
        book = Book.query.filter(Book.code == int(request.form["code"])).first()
    except OverflowError:
        flash("Neplatný kód učebnice","danger")
        return redirect(url_for("student_bp.view_student", student_id=student_id))

    if book:
        if book.student:
            flash("Učebnica s týmto kódom je už požičaná","danger")
        else:
            student = Student.query.filter(Student.id == student_id).first()
            if student:
                student.books.append(book)
                db_session.commit()
                flash("Učebnica bola pridaná", "success")
            else:
                return redirect(url_for("student_bp.search_student"))
    else:
        flash("Neplatný kód","danger")
    return redirect(url_for("student_bp.view_student",student_id=student_id))


@student_bp.route("/search_student/")
def search_student():
    return render_template("student/search_student.html")


@student_bp.route("/search_student/",methods=["POST"])
def search_student2():
    student_code = request.form["student_code"]
    if 1 < len(student_code) < 25:
        student = Student.query.filter(Student.code == student_code).first()
        if student:
            return redirect(url_for("student_bp.view_student",student_id=student.id))

    flash("Neplatný kód","danger")
    return render_template("student/search_student.html")


@student_bp.route("/login/", methods=["GET"])
def login_page():
    return render_template("student/login_page.html")


@student_bp.route("/login/", methods=["POST"])
def login_page2():
    student_code = request.form["student-code"]
    student = Student.query.filter(Student.code == student_code).first()
    if student:
        if not student.authorized:
            flash("Pokračuj v registrácií", "success")
            return render_template("student/continue_login.html", student=student)

        flash("Už máš vytvorený profil, prihlás sa doň", "success")
        return render_template("student/login_page.html")

    flash("Neplatný kód", "danger")
    return render_template("student/login_page.html", register_bool=True)


@student_bp.route("/login-check/", methods=["POST"])
def login_page3():
    email = request.form["email"]
    password = request.form["password"]

    student = Student.query.filter(Student.email == email).first()

    if student and student.check_password(password):
        try:
            check = request.form["remember_me"]
            login_user(student, remember=True)
        except:
            login_user(student)
        flash("Vitaj späť", "success")
        return redirect(url_for("student_bp.student_account"))

    admin = User.query.filter(User.email == email).first()
    if admin and admin.check_password(password):
        try:
            check = request.form["remember_me"]
            login_user(admin, remember=True)

        except:
            login_user(admin)

        session["permit"] = 1

        flash("Vitaj späť", "success")
        return redirect(url_for("admin_bp.landing_page"))

    flash("Chybný email alebo heslo", "danger")
    return render_template("student/login_page.html")


@student_bp.route("/logoff")
@login_required
def logoff():
    if "permit" in session:
        session.pop("permit")

    logout_user()
    flash("Bol si odhlásený", "success")
    return redirect(url_for("student_bp.login_page"))


@student_bp.route("/login/register/<int:code>/", methods=["POST"])
def finish_registration(code):
    student = Student.query.filter(Student.code == code).first()
    if student:
        st_check = Student.query.filter(Student.email == request.form["student-email"]).first()
        ad_check = User.query.filter(User.email == request.form["student-email"]).first()

        if st_check or ad_check:
            flash("Email sa už používa", "danger")
            print("sdfsd")
            return render_template("student/login_page.html", register_bool=True)

        student.email = request.form["student-email"]
        student.set_password(request.form["student-password"])
        student.authorized = True
        student.bio = request.form["student-bio"]
        tags = list(request.form["student-tags"].split(","))
        for tag in tags:
            s_tag = Tag.query.filter(Tag.name == tag).first()
            if s_tag:
                student.tags.append(s_tag)
            else:
                n_tag = Tag(tag)
                db_session.add(n_tag)
                student.tags.append(n_tag)

        db_session.commit()
        flash("Profil vytvorený, môžeš as prihlásiť", "success")
        return render_template("student/login_page.html")

    flash("Neplatný kód", "danger")
    return render_template("student/login_page.html", register_bool=True)

