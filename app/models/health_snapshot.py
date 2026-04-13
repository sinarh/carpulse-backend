from ..extensions import db


class HealthSnapshot(db.Model):
    __tablename__ = "health_snapshots"

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False)

    mileage = db.Column(db.Integer, nullable=False)
    fuel_level = db.Column(db.Float, nullable=True)
    engine_temp = db.Column(db.Float, nullable=True)

    check_engine_light = db.Column(db.Boolean, nullable=False, default=False)

    battery_status = db.Column(db.String(50), nullable=True)
    tire_status = db.Column(db.String(50), nullable=True)
    brake_status = db.Column(db.String(50), nullable=True)

    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, server_default=db.func.now())