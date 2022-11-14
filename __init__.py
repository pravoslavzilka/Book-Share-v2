from flask import Flask, render_template, redirect, url_for
from blueprints.admin.__init__ import admin_bp
from blueprints.student.__init__ import student_bp
from blueprints.book.__init__ import book_bp
from database import db_session
from flask_mail import Mail, Message
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from threading import Thread
from models import User, Student
import os


UPLOAD_FOLDER = '/path/files'

app = Flask(__name__)

app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(student_bp, url_prefix="/student")
app.register_blueprint(book_bp, url_prefix="/book")

app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(16)
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


@app.route("/send-email")
def send_email_page():
    msg = Message(sender=app.config['MAIL_DEFAULT_SENDER '])
    msg.subject = "Reset password"
    msg.recipients = ["pravoslav.zilka@gmail.com"]
    msg.body = "hello"
    Thread(target=send_email, args=(app, msg)).start()

    print("MAIL SENT")
    return redirect(url_for("welcome_page"))


def send_email(app, msg):
    with app.app_context():
        mail.send(msg)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
