from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from database import db_session
from models import Grade, Student, Book, BookType
from werkzeug.utils import secure_filename
from flask_login import login_required
import openpyxl
from functools import wraps


book_bp = Blueprint("book_bp", __name__, template_folder="templates")

ALLOWED_EXTENSIONS = {'xlsx', 'xlsm', 'xltx', 'xltm'}


def check_admin(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if "permit" in session:
            if session["permit"] == 1:
                return func(*args, **kwargs)
        return redirect(url_for("student_bp.login_page"))
    return inner


@book_bp.route("/all/")
@check_admin
def landing_page():
    books = Book.query.all()
    free_books = Book.query.filter(Book.student == None).count()
    rent_books = Book.query.filter(Book.student).count()
    total_books = Book.query.count()

    book_types = BookType.query.all()

    return render_template("book/landing_page.html", books=books, book_types=book_types,
                           ctbooks=total_books, cfbooks=free_books, crbooks=rent_books
                           )


@book_bp.route("/type/<bt_name>/")
@check_admin
def book_type_page(bt_name):
    book_type = BookType.query.filter(BookType.name == bt_name).first()

    free_books = Book.query.filter(Book.student == None, Book.book_type == book_type).count()
    rent_books = Book.query.filter(Book.student, Book.book_type == book_type).count()
    total_books = Book.query.filter(Book.book_type == book_type).count()

    return render_template("book/book_type_page.html",book_type=book_type,
                           ctbooks=total_books, cfbooks=free_books, crbooks=rent_books
                           )


@book_bp.route("/total_list/")
@check_admin
def list_of_books():
    books = Book.query.all()
    book_types = BookType.query.all()
    return render_template("book/book_list.html", books=books,book_types=book_types)


@book_bp.route("/list/<book_state>/")
@check_admin
def books_state(book_state):
    book_types = BookType.query.all()
    if book_state == "free":
        books = Book.query.filter(Book.student_id == None).all()
    else:
        books = Book.query.filter(Book.student_id != None).all()

    return render_template("book/book_list.html",books=books,book_types=book_types)


@book_bp.route("/add_new/in/<bt_name>/",methods=["POST"])
@check_admin
def add_book_with_type(bt_name):
    book_code = request.form["book_code"]
    book = Book.query.filter(Book.code == book_code).first()

    if book:
        flash("U??ebnica s t??mto k??dom u?? existuje", "danger")
        return redirect(url_for("book_bp.book_type_page",bt_name=bt_name))

    book_type = BookType.query.filter(BookType.name == bt_name).first()
    new_book = Book(int(book_code), book_type)

    db_session.add(new_book)
    try:
        db_session.commit()
    except OverflowError:
        flash("Neplatn?? k??d", "danger")
        return redirect(url_for("book_bp.book_type_page", bt_name=bt_name))

    flash(f"U??ebnica s k??dom {book_code} ??spe??ne pridan??","success")
    return redirect(url_for("book_bp.book_type_page", bt_name=bt_name))


@book_bp.route("/return/",methods=["GET"])
@check_admin
def return_book_view():
    return render_template("book/return_book.html")


@book_bp.route("/return-book-s-page/<int:book_code>")
@check_admin
def return_book_s_page(book_code):
    book = Book.query.filter(Book.code == int(book_code)).first()
    if book:
        if book.student:
            student = Student.query.filter(Student.id == book.student.id).first()
            student.books.remove(book)
            db_session.commit()
            flash(f"Kniha s k??dom {book.code} bola ??spe??ne vr??ten??", "success")
            return redirect(url_for("student_bp.view_student", student_id=student.id))

    return redirect(url_for("student_bp.landing_page"))


@book_bp.route("/return/",methods=["POST"])
@check_admin
def return_book():
    code = int(request.form["book_code"])
    try:
        book = Book.query.filter(Book.code == code).first()
    except OverflowError:
        flash("Neplatn?? k??d", "danger")
        return redirect(url_for("book_bp.return_book_view"))

    if book:
        if book.student:
            student = Student.query.filter(Student.id == book.student.id).first()
            student.books.remove(book)
            db_session.commit()
        flash(f"Kniha s k??dom {book.code} bola ??spe??ne vr??ten??","success")
        return redirect(url_for("book_bp.return_book_view"))

    flash("Neplatn?? k??d","danger")
    return redirect(url_for("book_bp.return_book_view"))


@book_bp.route("/return/from/list/",methods=["POST"])
@check_admin
def return_book_from_list():
    code = int(request.form["book_code"])
    try:
        book = Book.query.filter(Book.code == code).first()
    except OverflowError:
        flash("Neplatn?? k??d", "danger")
        return redirect(url_for("book_bp.list_of_books"))

    if book:
        if book.student:
            student = Student.query.filter(Student.id == book.student.id).first()
            student.books.remove(book)
            db_session.commit()
        flash(f"U??ebnica s k??dom {book.code} bola ??spe??ne vr??ten??", "success")
        return redirect(url_for("book_bp.list_of_books"))

    flash("Neplatn?? k??d", "danger")
    return redirect(url_for("book_bp.list_of_books"))


@book_bp.route("/return/with/type/",methods=["POST"])
@check_admin
def return_book_with_type():
    code = int(request.form["book_code"])
    try:
        book = Book.query.filter(Book.code == code).first()
    except OverflowError:
        flash("Neplatn?? k??d", "danger")
        return redirect(url_for("book_bp.book_type_page"))

    if book:
        if book.student:
            student = Student.query.filter(Student.id == book.student.id).first()
            student.books.remove(book)
            db_session.commit()
        flash(f"U??ebnica s k??dom {book.code} bola ??spe??ne vr??ten??", "success")
        return redirect(url_for("book_bp.book_type_page",bt_name=book.book_type.name))

    flash("Neplatn?? k??d", "danger")
    return redirect(url_for("book_bp.book_type_page",bt_name=book.book_type.name))


@book_bp.route("/delete/",methods=['POST'])
@check_admin
def delete_book():
    book_code = int(request.form["book_code"])
    try:
        book = Book.query.filter(Book.code == book_code).first()
    except OverflowError:
        flash("Neplatn?? k??d", "danger")
        return redirect(url_for("book_bp.list_of_books"))

    if book:
        book_type = BookType.query.filter(BookType.id == book.book_type_id).first()
        db_session.delete(book)
        db_session.commit()
        flash(f"Kniha s k??dom {book.code} bola ??spe??ne odstr??nen??","success")
        return redirect(url_for("book_bp.book_type_page",bt_name=book_type.name))

    flash("Neplatn?? k??d", "danger")
    return redirect(url_for("book_bp.list_of_books"))


@book_bp.route("/delete/from/list/",methods=['POST'])
@check_admin
def delete_book_from_list():
    book_code = int(request.form["book_code"])
    try:
        book = Book.query.filter(Book.code == book_code).first()
    except OverflowError:
        flash("Neplatn?? k??d","danger")
        return redirect(url_for("book_bp.list_of_books"))

    db_session.delete(book)
    db_session.commit()
    flash(f"Kniha s k??dom {book.code} bola ??spe??ne odstr??nen??","success")
    return redirect(url_for("book_bp.list_of_books"))


@book_bp.route("/add_type/",methods=["POST"])
@check_admin
def add_book_type():
    req_bt = request.form["book_name"]
    req_ba = request.form["book_author"]

    try:
        book_type = BookType.query.filter(BookType.name == req_bt).first()
    except OverflowError:
        flash("Neplatn?? k??d","danger")
        return redirect(url_for("book_bp.landing_page"))

    if book_type:
        flash("Typ tejto u??ibnice u?? existuje","danger")
        return redirect(url_for("book_bp.landing_page"))

    new_bt = BookType(req_bt,req_ba)
    db_session.add(new_bt)
    try:
        db_session.commit()
    except OverflowError:
        flash("Neplatn?? ??daje", "danger")
        return redirect(url_for("book_bp.landing_page"))

    flash(f"Nov?? typ u??ebn??c {req_bt} bol ??spe??ne pridan??", "success")
    return redirect(url_for("book_bp.landing_page"))


@book_bp.route("/update/type/<int:type_id>/", methods=["POST"])
@check_admin
def update_book_type(type_id):
    book_type = BookType.query.filter(BookType.id == type_id).first()

    if book_type:
        n_name = request.form["book_type_name"]
        n_author = request.form["book_type_author"]
        book_type.name = n_name
        book_type.author = n_author
        db_session.commit()
        flash(f"U??ebnica '{book_type.name}' bola aktualizovan??.","success")
        return redirect(url_for("book_bp.book_type_page", bt_name=book_type.name))
    else:
        return redirect(url_for("book_bp.landing_page"))


@book_bp.route("/delete/type/<int:type_id>/")
@check_admin
def delete_type(type_id):

    try:
        book_type = BookType.query.filter(BookType.id == type_id).first()
    except OverflowError:
        flash("Neplatan?? k??d", "danger")
        return redirect(url_for("book_bp.landing_page"))

    count_of_books = 0
    if book_type:
        for index,book in enumerate(book_type.books):
            db_session.delete(book)
            count_of_books += 1

        db_session.delete(book_type)
        db_session.commit()
        flash(f"Typ u??ebnice '{book_type.name}' bol ??spe??ne vymazan?? a s n??m {count_of_books} u??ebn??c","success")
        return redirect(url_for("book_bp.landing_page"))

    flash("Neplatan?? k??d", "danger")
    return redirect(url_for("book_bp.landing_page"))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@book_bp.route('/upload/source/excel/',methods=["POST"])
@check_admin
def upload_file():

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        wb_obj = openpyxl.load_workbook(file)
        sheet_obj = wb_obj.active

        try:
            for i in range(1,sheet_obj.max_row):
                name = sheet_obj.cell(row=i+1, column=1).value
                code = sheet_obj.cell(row=i+1, column=3).value

                book_type = BookType.query.filter(BookType.name == name).first()
                if book_type:
                    new_book = Book(code,book_type)
                    db_session.add(new_book)
                elif name == ": Geografick?? atlas pre Z?? a S??":
                    book_type = BookType.query.filter(BookType.name == "Geografick?? atlas pre Z?? a S??").first()
                    if book_type:
                        new_book = Book(code, book_type)
                        db_session.add(new_book)
                    else:
                        print(name,"FAIL")

                elif name == "Litetat??ra 1 pre  S??":
                    book_type = BookType.query.filter(BookType.name == "Litetat??ra 1  pre  S??").first()
                    if book_type:
                        new_book = Book(code, book_type)
                        db_session.add(new_book)
                    else:
                        print(name, "FAIL")
                elif name == None:
                    pass
                else:
                    print(name,"FAIL")

            db_session.commit()
        except:
            flash("Nastala chyba pri nahr??van??. Ujistite sa, ??i ??tudenti z tabu??ky nie su u?? v syst??me", "danger")
            return redirect(url_for("book_bp.landing_page"))

        flash("U??ebnice z execelu boli ??spe??ne pridan??","success")
        return redirect(url_for("book_bp.landing_page"))

    allow_f_string = ' / '.join(map(str, ALLOWED_EXTENSIONS))
    flash(f"S??bor nie je podporovan??. Typ s??boru mus?? by??: {allow_f_string}","danger")
    return redirect(url_for("book_bp.landing_page"))

