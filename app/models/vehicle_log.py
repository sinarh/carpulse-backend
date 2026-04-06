from ..extensions import db

class VehicleLog(db.Model):
    __tablename__ = "vehicle_logs"

    id = db.Column(db.Integer, primary_key=True)

    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False)

    # (manual data entry)
    mileage = db.Column(db.Integer, nullable=True)
    fuel_level = db.Column(db.Integer, nullable=True)      # 0–100
    engine_temp = db.Column(db.Float, nullable=True)       # celsius
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, server_default=db.func.now(), index=True)
