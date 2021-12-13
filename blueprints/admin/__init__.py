from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from models import User


admin_bp = Blueprint("admin_bp",__name__,template_folder="templates",static_folder="static")


@admin_bp.route("/sign-in/")
def sign_in():
    return render_template("admin/sign_in.html")


@admin_bp.route("/sign_in/",methods=["GET"])
def sign_in_page():
    return render_template("admin/login_page.html")


@admin_bp.route("/sign_in/",methods=["POST"])
def sign_in_page2():

    user = User.query.filter(User.email == request.form["email"]).first()

    if user and user.check_password(request.form["password"]):
        try:
            check = request.form["remember_me"]
            login_user(user, remember=True)
        except:
            login_user(user)
        flash("Vitajte späť","success")
        return redirect(url_for("welcome_page"))

    flash("Chybný email alebo heslo","danger")
    return render_template("admin/login_page.html")


@admin_bp.route("/sign_out")
@login_required
def sign_out():
    logout_user()
    flash("Boli ste odhlásený","success")
    return redirect(url_for("welcome_page"))
