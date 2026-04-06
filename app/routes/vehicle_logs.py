from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.vehicle import Vehicle
from ..models.vehicle_log import VehicleLog

vehicle_logs_bp = Blueprint("vehicle_logs", __name__)

def _get_vehicle_owned_or_404(vehicle_id: int, user_id: int):
    v = Vehicle.query.filter_by(id=vehicle_id, user_id=user_id).first()
    return v

@vehicle_logs_bp.post("/<int:vehicle_id>/logs")
@jwt_required()
def create_log(vehicle_id: int):
    user_id = int(get_jwt_identity())
    vehicle = _get_vehicle_owned_or_404(vehicle_id, user_id)
    if not vehicle:
        return jsonify({"error": "vehicle not found"}), 404

    data = request.get_json() or {}

    mileage = data.get("mileage")
    fuel_level = data.get("fuel_level")
    engine_temp = data.get("engine_temp")
    notes = data.get("notes")
    

    log = VehicleLog(
        vehicle_id=vehicle.id,
        mileage=int(mileage) if mileage is not None else None,
        fuel_level=int(fuel_level) if fuel_level is not None else None,
        engine_temp=float(engine_temp) if engine_temp is not None else None,
        notes=str(notes) if notes is not None else None,
    )

    db.session.add(log)
    db.session.commit()

    return jsonify({"id": log.id, "created_at": str(log.created_at)}), 201


@vehicle_logs_bp.get("/<int:vehicle_id>/logs")
@jwt_required()
def list_logs(vehicle_id: int):
    user_id = int(get_jwt_identity())
    vehicle = _get_vehicle_owned_or_404(vehicle_id, user_id)
    if not vehicle:
        return jsonify({"error": "vehicle not found"}), 404

    logs = (
        VehicleLog.query
        .filter_by(vehicle_id=vehicle.id)
        .order_by(VehicleLog.created_at.desc())
        .limit(50)
        .all()
    )

    return jsonify([
        {
            "id": l.id,
            "mileage": l.mileage,
            "fuel_level": l.fuel_level,
            "engine_temp": l.engine_temp,
            "notes": l.notes,
            "created_at": str(l.created_at),
        }
        for l in logs
    ]), 200


@vehicle_logs_bp.get("/<int:vehicle_id>/latest")
@jwt_required()
def latest_log(vehicle_id: int):
    user_id = int(get_jwt_identity())
    vehicle = _get_vehicle_owned_or_404(vehicle_id, user_id)
    if not vehicle:
        return jsonify({"error": "vehicle not found"}), 404

    l = (
        VehicleLog.query
        .filter_by(vehicle_id=vehicle.id)
        .order_by(VehicleLog.created_at.desc())
        .first()
    )

    if not l:
        return jsonify({"message": "no logs yet"}), 200

    return jsonify({
        "id": l.id,
        "mileage": l.mileage,
        "fuel_level": l.fuel_level,
        "engine_temp": l.engine_temp,
        "notes": l.notes,
        "created_at": str(l.created_at),
    }), 200
