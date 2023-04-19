from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Admin(db.Model, UserMixin):
    admin_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True, nullable=False)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    password = db.Column(db.String(255))

    def is_active(self):
        return True

    def get_id(self):
        return self.email  
    __tablename__ = 'admin'


class Teacher(db.Model, UserMixin):
    teacher_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    password = db.Column(db.String(255))
    __tablename__ = 'teacher'

    students = db.relationship('Student', backref='teacher', lazy=True)

    
    def is_active(self):
        return True
    def get_id(self):
        return self.email

class Student(db.Model):
    student_id = db.Column(db.String(255), primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    classroom_number = db.Column(db.Integer)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.teacher_id')) 
    teacher_name = db.Column(db.String(255))
    guardian_1 = db.Column(db.String(255))
    primary_phone = db.Column(db.BigInteger)
    secondary_phone = db.Column(db.BigInteger, nullable=True)
    __tablename__ = 'students'

class Pickup(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_name = db.Column(db.String(255))
    pickup_time = db.Column(db.DateTime)
    __tablename__= 'student_pickup'

class EmailQueue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient = db.Column(db.String(255))
    subject = db.Column(db.String(255))
    body = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    __tablename__= 'email_queue'

class student_dropoff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id_fk = db.Column(db.String(255))
    student_name = db.Column(db.String(255))
    dropoff_time = db.Column(db.DateTime)
    __tablename__ = 'student_dropoff'
