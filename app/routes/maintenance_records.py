from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models import Vehicle, MaintenanceRecord

maintenance_records_bp = Blueprint("maintenance_records", __name__)


def _maintenance_record_to_dict(record: MaintenanceRecord):
    return {
        "id": record.id,
        "vehicle_id": record.vehicle_id,
        "service_type": record.service_type,
        "service_date": record.service_date.isoformat() if record.service_date else None,
        "mileage": record.mileage,
        "cost": record.cost,
        "notes": record.notes,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }


def _get_owned_vehicle(vehicle_id: int, user_id: int):
    return Vehicle.query.filter_by(id=vehicle_id, user_id=user_id).first()


def _parse_date(value):
    if value in (None, ""):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


@maintenance_records_bp.post("/vehicle/<int:vehicle_id>/maintenance-records")
@jwt_required()
def create_maintenance_record(vehicle_id: int):
    user_id = int(get_jwt_identity())
    vehicle = _get_owned_vehicle(vehicle_id, user_id)

    if not vehicle:
        return jsonify({"error": "vehicle not found"}), 404

    data = request.get_json() or {}

    service_type = data.get("service_type")
    service_date_raw = data.get("service_date")
    mileage = data.get("mileage")

    if not service_type or not service_date_raw or mileage is None:
        return jsonify({"error": "service_type, service_date, and mileage are required"}), 400

    service_date = _parse_date(service_date_raw)
    if service_date is None:
        return jsonify({"error": "service_date must be YYYY-MM-DD"}), 400

    try:
        mileage = int(mileage)
    except (TypeError, ValueError):
        return jsonify({"error": "mileage must be a number"}), 400

    cost = data.get("cost")
    try:
        cost = float(cost) if cost not in (None, "") else None
    except (TypeError, ValueError):
        return jsonify({"error": "cost must be a number"}), 400

    record = MaintenanceRecord(
        vehicle_id=vehicle.id,
        service_type=str(service_type).strip(),
        service_date=service_date,
        mileage=mileage,
        cost=cost,
        notes=data.get("notes"),
    )

    db.session.add(record)
    db.session.commit()

    return jsonify(_maintenance_record_to_dict(record)), 201


@maintenance_records_bp.get("/vehicle/<int:vehicle_id>/maintenance-records")
@jwt_required()
def list_maintenance_records(vehicle_id: int):
    user_id = int(get_jwt_identity())
    vehicle = _get_owned_vehicle(vehicle_id, user_id)

    if not vehicle:
        return jsonify({"error": "vehicle not found"}), 404

    records = (
        MaintenanceRecord.query
        .filter_by(vehicle_id=vehicle.id)
        .order_by(MaintenanceRecord.service_date.desc(), MaintenanceRecord.created_at.desc())
        .all()
    )

    return jsonify([_maintenance_record_to_dict(record) for record in records]), 200