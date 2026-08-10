from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    passhash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False) 
    contact = db.Column(db.String(20), nullable=True)
    blacklist_status = db.Column(db.Boolean, default=False, nullable=False)
    active_status = db.Column(db.Boolean, default = True, nullable = False)
    
    trekk_assigned = db.relationship('Trek', backref='staff', lazy=True, foreign_keys='Trek.assigned_staff')
    
    bookings = db.relationship('Booking', backref='trekker', lazy=True, cascade='all, delete-orphan', foreign_keys='Booking.trekker_id')


class Trek(db.Model):
    __tablename__ = 'trek'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    desc = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    difficulty = db.Column(db.String(10), nullable=False, default='Moderate')
    time_duration = db.Column(db.Integer, nullable=False)
    total_slots = db.Column(db.Integer, nullable=False)
    slots = db.Column(db.Integer, nullable=False)
    trek_fee = db.Column(db.Float, nullable=False, default='0.00')
    status = db.Column(db.String(20), nullable=False, default='Pending')
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    assigned_staff = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    bookings = db.relationship('Booking', backref='trek', lazy=True, cascade='all, delete-orphan') 


class Booking(db.Model):
    __tablename__ = 'booking'
    
    id = db.Column(db.Integer, primary_key=True)
    trekker_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    trek_id = db.Column(db.Integer, db.ForeignKey('trek.id'))
    book_date = db.Column(db.Date, default=date.today(), nullable=False)
    booked_slots = db.Column(db.Integer, default=0, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    pay_status = db.Column(db.String(20), nullable=False, default='Pending')


class TokenBlocklist(db.Model):
    __tablename__ = 'tokenblocklist'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)