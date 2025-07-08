from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# -------------------- User Model --------------------
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False) 
    fullname = db.Column(db.String(100))
    address = db.Column(db.String(200))
    pincode = db.Column(db.String(10))

# -------------------- ParkingLot Model --------------------
class ParkingLot(db.Model):
    __tablename__ = 'parking_lot'   

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)

    pincode = db.Column(db.String(10), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    max_spots = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    creator = db.relationship('User', backref=db.backref('parking_lots', lazy=True))

# -------------------- ParkingHistory Model --------------------
from models import db

# models.py

class ParkingHistory(db.Model):
    __tablename__ = 'parking_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'))
    spot_id = db.Column(db.Integer, nullable=False)  # ✅ NEW FIELD
    vehicle_no = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False)

    lot = db.relationship('ParkingLot', backref=db.backref('histories', lazy=True))
