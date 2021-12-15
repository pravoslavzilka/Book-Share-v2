from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Table, Date
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from database import Base


association_table = Table('association', Base.metadata,
    Column('student_id', ForeignKey('student.id'), primary_key=True),
    Column('tag_id', ForeignKey('tag.id'), primary_key=True),
)


class User(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    password = Column(String(128))

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User %r>' % self.name


class Student(Base):
    __tablename__ = 'student'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(120))
    password = Column(String(128))
    authorized = Column(Boolean)
    code = Column(Integer, unique=True)
    bio = Column(String(250))
    grade_id = Column(Integer, ForeignKey('grade.id'))

    grade = relationship("Grade", back_populates="students", foreign_keys=[grade_id])
    books = relationship("Book", back_populates="student", foreign_keys="[Book.student_id]")
    events = relationship("Event", back_populates="student", foreign_keys="[Event.student_id]")

    tags = relationship("Tag", secondary=association_table, back_populates="students")

    def __init__(self, name=None, grade=None, code=None):
        self.name = name
        self.grade = grade
        self.code = code
        self.authorized = False

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<Student %r>' % self.name


class Grade(Base):
    __tablename__ = "grade"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    students = relationship("Student", back_populates="grade")

    def __init__(self, name):
        self.name = name


class Tag(Base):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True)

    students = relationship("Student", secondary=association_table, back_populates="tags")

    def __init__(self, name):
        self.name = name


class Event(Base):
    __tablename__ = "event"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    description = Column(String(300))
    time = Column(Date)
    teacher = Column(String(120))
    student_id = Column(Integer, ForeignKey('student.id'))

    student = relationship("Student", back_populates="events")

    def __init__(self, name=None, description=None, leader=None):
        self.name = name
        self.description = description
        self.student = leader


class Book(Base):
    __tablename__ = "book"
    id = Column(Integer,primary_key=True)
    code = Column(Integer)
    student_id = Column(Integer, ForeignKey('student.id'))
    book_type_id = Column(Integer, ForeignKey('book_type.id'))

    student = relationship("Student", back_populates="books", foreign_keys=[student_id])
    book_type = relationship("BookType", back_populates="books", foreign_keys=[book_type_id])


    def __init__(self,code=None,book_type=None):
        self.code = code
        self.book_type = book_type


class BookType(Base):
    __tablename__ = "book_type"
    id = Column(Integer,primary_key=True)
    name = Column(String(50))
    author = Column(String(50))
    books = relationship("Book", back_populates="book_type")
    
    def __init__(self, name=None, author=None):
        self.name = name
        self.author = author



