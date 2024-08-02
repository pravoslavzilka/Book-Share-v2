from flask import Flask, render_template, redirect, url_for, flash, request
from blueprints.admin.__init__ import admin_bp
from blueprints.student.__init__ import student_bp
from blueprints.book.__init__ import book_bp
from database import db_session
from flask_mail import Mail, Message
from flask_login import LoginManager
from threading import Thread
from models import User, Student
from itsdangerous import URLSafeTimedSerializer
import os


UPLOAD_FOLDER = '/path/files'

app = Flask(__name__)

app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(student_bp, url_prefix="/student")
app.register_blueprint(book_bp, url_prefix="/book")

app.secret_key = os.environ['secretKey']
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["REMEMBER_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = True
app.config["REMEMBER_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = 'Lax'

UsersStatus = []

app.jinja_env.autoescape = True | False


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "student_bp.login_page"
login_manager.login_message = "Prihlás sa do aplikácie"
login_manager.login_message_category = "info"
login_manager.session_protection = "strong"

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)


app.config["MAIL_SERVER"] = 'smtp.gma.sk'
app.config["MAIL_PORT"] = '587'
app.config["MAIL_USERNAME"] = 'no-reply@gma.sk'
app.config["MAIL_PASSWORD"] = 'y@RmeC95'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER '] = "no-reply@gma.sk"

mail = Mail(app)


@app.route("/")
def welcome_page():
    return redirect(url_for("student_bp.login_page"))


@app.errorhandler(400)
def error_400(error):
    return render_template("400.html")


@app.errorhandler(404)
def error_404(error):
    return render_template("404.html")


@app.errorhandler(405)
def error_405(error):
    return render_template("404.html")


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@login_manager.user_loader
def load_user(user_id):
    return Student.query.filter(Student.id == user_id).first() or User.query.filter(User.id == user_id).first()


@app.route("/lost-password/", methods=['GET'])
def lost_password_view():
    return render_template("student/lost_password.html")


@app.route("/lost-password/", methods=['POST'])
def lost_password_fun():
    email = request.form["email"]

    student = Student.query.filter(Student.email == email).first()
    if student:
        send_email_page(email)
        return render_template("student/lost_password_info.html")

    admin = User.query.filter(User.email == email).first()
    if admin:
        send_email_page(email)
        return render_template("student/lost_password_info.html")

    flash("Nenašli sme používateľa s týmto emailom.","danger")
    return render_template("student/lost_password.html")


def send_email_page(email):
    msg = Message(sender=app.config['MAIL_DEFAULT_SENDER '])
    msg.subject = "eSklad - Obnova hesla"
    msg.recipients = [email]
    msg.body = "Dobrý deň, \n\nNa následujúcom linku sa Vám otvorí stránka kde si budete môcť resetovať vaše heslo: https://esklad.gma.sk" + generate_reset_link(email) + "\n\nV prípade že ste nežiadali zmenu hesla, prosím ignorujte tento email.\n\nAk by ste mali problémy so svojím účtom, prosím kontaktujte nás na help@gma.sk \n\nS pozdravom, \nTím eSklad "
    Thread(target=send_email, args=(app, msg)).start()


def generate_reset_link(email):
    password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    password_reset_url = url_for('check_token_request',
                                 token=password_reset_serializer.dumps(email, salt='password-reset-salt'),
                                 external=True)
    return password_reset_url


def send_email(app, msg):
    with app.app_context():
        mail.send(msg)


@app.route("/reset-password/<token>/", methods=['GET'])
def check_token_request(token):
    try:
        password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = password_reset_serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except:
        flash("Link na obnovu hesla je nesprávný alebo mu vypršala platnosť, skúste to znova neskôr", "danger")
        return redirect(url_for("student_bp.login_page"))

    flash("Teraz si môžete resetovať heslo", "success")
    return render_template("student/reset_password.html", email=email)


@student_bp.route("/reset-password/", methods=["POST"])
def reset_password():
    email = request.form["email"]
    password = request.form["password"]

    student = Student.query.filter(Student.email == email).first()
    if student:
        student.set_password(password)
        db_session.commit()
        flash("Heslo úspešne obnovené", "success")
        return redirect(url_for("student_bp.login_page"))

    admin = User.query.filter(User.email == email).first()
    if admin:
        admin.set_password(password)
        db_session.commit()
        flash("Heslo úspešne obnovené", "success")
        return redirect(url_for("student_bp.login_page"))

    return redirect(url_for("student_bp.login_page"))


@app.route("/email-set/")
def reset_password():
    emails =["asfdasd"]

    for email in emails:
        msg = Message(sender=app.config['MAIL_DEFAULT_SENDER '])
        msg.subject = "eSklad - Oprava Emailu"
        msg.recipients = [email]
        msg.body = f"Dobrý deň, \n\nVáš email na stránke https://esklad.gma.sk/ bol opravený. Prosím používajte email: {email} na prihlásenie sa. " + "\n\nAk by ste mali problémy so svojím účtom, prosím kontaktujte nás na help@gma.sk \n\nS pozdravom, \nTím eSklad "
        Thread(target=send_email, args=(app, msg)).start()

    return '00'


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
