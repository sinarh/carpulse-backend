from ..extensions import db

class Vehicle(db.Model):
    __tablename__ = "vehicles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    make = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    mileage = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    logs = db.relationship("VehicleLog", backref="vehicle", lazy=True, cascade="all, delete-orphan")

