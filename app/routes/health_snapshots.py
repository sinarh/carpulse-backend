from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models import Vehicle, HealthSnapshot

health_snapshots_bp = Blueprint("health_snapshots", __name__)


def _health_snapshot_to_dict(snapshot: HealthSnapshot):
    return {
        "id": snapshot.id,
        "vehicle_id": snapshot.vehicle_id,
        "mileage": snapshot.mileage,
        "fuel_level": snapshot.fuel_level,
        "engine_temp": snapshot.engine_temp,
        "check_engine_light": snapshot.check_engine_light,
        "battery_status": snapshot.battery_status,
        "tire_status": snapshot.tire_status,
        "brake_status": snapshot.brake_status,
        "notes": snapshot.notes,
        "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None,
    }


def _get_owned_vehicle(vehicle_id: int, user_id: int):
    return Vehicle.query.filter_by(id=vehicle_id, user_id=user_id).first()


@health_snapshots_bp.post("/vehicle/<int:vehicle_id>/health-snapshots")
@jwt_required()
def create_health_snapshot(vehicle_id: int):
    user_id = int(get_jwt_identity())
    vehicle = _get_owned_vehicle(vehicle_id, user_id)

    if not vehicle:
        return jsonify({"error": "vehicle not found"}), 404

    data = request.get_json() or {}

    mileage = data.get("mileage")
    if mileage is None:
        return jsonify({"error": "mileage is required"}), 400

    try:
        mileage = int(mileage)
    except (TypeError, ValueError):
        return jsonify({"error": "mileage must be a number"}), 400

    fuel_level = data.get("fuel_level")
    engine_temp = data.get("engine_temp")

    try:
        fuel_level = float(fuel_level) if fuel_level not in (None, "") else None
        engine_temp = float(engine_temp) if engine_temp not in (None, "") else None
    except (TypeError, ValueError):
        return jsonify({"error": "fuel_level and engine_temp must be numbers"}), 400

    snapshot = HealthSnapshot(
        vehicle_id=vehicle.id,
        mileage=mileage,
        fuel_level=fuel_level,
        engine_temp=engine_temp,
        check_engine_light=bool(data.get("check_engine_light", False)),
        battery_status=data.get("battery_status"),
        tire_status=data.get("tire_status"),
        brake_status=data.get("brake_status"),
        notes=data.get("notes"),
    )

    db.session.add(snapshot)
    db.session.commit()

    return jsonify(_health_snapshot_to_dict(snapshot)), 201


@health_snapshots_bp.get("/vehicle/<int:vehicle_id>/health-snapshots")
@jwt_required()
def list_health_snapshots(vehicle_id: int):
    user_id = int(get_jwt_identity())
    vehicle = _get_owned_vehicle(vehicle_id, user_id)

    if not vehicle:
        return jsonify({"error": "vehicle not found"}), 404

    snapshots = (
        HealthSnapshot.query
        .filter_by(vehicle_id=vehicle.id)
        .order_by(HealthSnapshot.created_at.desc())
        .all()
    )

    return jsonify([_health_snapshot_to_dict(snapshot) for snapshot in snapshots]), 200