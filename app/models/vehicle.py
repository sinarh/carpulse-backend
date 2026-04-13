from ..extensions import db


class Vehicle(db.Model):
    __tablename__ = "vehicles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    make = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    mileage = db.Column(db.Integer, nullable=False)

    nickname = db.Column(db.String(100), nullable=True)
    fuel_type = db.Column(db.String(50), nullable=True)
    transmission = db.Column(db.String(50), nullable=True)
    purchase_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    logs = db.relationship(
        "VehicleLog",
        backref="vehicle",
        lazy=True,
        cascade="all, delete-orphan"
    )

    maintenance_records = db.relationship(
        "MaintenanceRecord",
        backref="vehicle",
        lazy=True,
        cascade="all, delete-orphan"
    )

    health_snapshots = db.relationship(
        "HealthSnapshot",
        backref="vehicle",
        lazy=True,
        cascade="all, delete-orphan"
    )