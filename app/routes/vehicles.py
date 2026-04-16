from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models import Vehicle

vehicles_bp = Blueprint("vehicles", __name__)


def _vehicle_to_dict(vehicle: Vehicle):
    return {
        "id": vehicle.id,
        "make": vehicle.make,
        "model": vehicle.model,
        "year": vehicle.year,
        "mileage": vehicle.mileage,
        "nickname": vehicle.nickname,
        "fuel_type": vehicle.fuel_type,
        "transmission": vehicle.transmission,
        "purchase_date": vehicle.purchase_date.isoformat() if vehicle.purchase_date else None,
        "notes": vehicle.notes,
        "created_at": vehicle.created_at.isoformat() if vehicle.created_at else None,
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


@vehicles_bp.post("/")
@jwt_required()
def create_vehicle():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    make = data.get("make")
    model = data.get("model")
    year = data.get("year")
    mileage = data.get("mileage")

    if not make or not model or year is None or mileage is None:
        return jsonify({"error": "make, model, year, and mileage are required"}), 400

    try:
        year = int(year)
        mileage = int(mileage)
    except (TypeError, ValueError):
        return jsonify({"error": "year and mileage must be numbers"}), 400

    purchase_date_raw = data.get("purchase_date")
    purchase_date = _parse_date(purchase_date_raw)
    if purchase_date_raw not in (None, "") and purchase_date is None:
        return jsonify({"error": "purchase_date must be YYYY-MM-DD"}), 400

    vehicle = Vehicle(
        user_id=user_id,
        make=str(make).strip(),
        model=str(model).strip(),
        year=year,
        mileage=mileage,
        nickname=data.get("nickname"),
        fuel_type=data.get("fuel_type"),
        transmission=data.get("transmission"),
        purchase_date=purchase_date,
        notes=data.get("notes"),
    )

    db.session.add(vehicle)
    db.session.commit()

    return jsonify(_vehicle_to_dict(vehicle)), 201


@vehicles_bp.get("/")
@jwt_required()
def list_vehicles():
    user_id = int(get_jwt_identity())
    vehicles = Vehicle.query.filter_by(user_id=user_id).order_by(Vehicle.created_at.desc()).all()
    return jsonify([_vehicle_to_dict(v) for v in vehicles]), 200


@vehicles_bp.get("/<int:vehicle_id>")
@jwt_required()
def get_vehicle(vehicle_id: int):
    user_id = int(get_jwt_identity())
    vehicle = _get_owned_vehicle(vehicle_id, user_id)

    if not vehicle:
        return jsonify({"error": "vehicle not found"}), 404

    return jsonify(_vehicle_to_dict(vehicle)), 200


@vehicles_bp.put("/<int:vehicle_id>")
@jwt_required()
def update_vehicle(vehicle_id: int):
    user_id = int(get_jwt_identity())
    vehicle = _get_owned_vehicle(vehicle_id, user_id)

    if not vehicle:
        return jsonify({"error": "vehicle not found"}), 404

    data = request.get_json() or {}

    if "make" in data:
        vehicle.make = str(data["make"]).strip()
    if "model" in data:
        vehicle.model = str(data["model"]).strip()
    if "year" in data:
        try:
            vehicle.year = int(data["year"])
        except (TypeError, ValueError):
            return jsonify({"error": "year must be a number"}), 400
    if "mileage" in data:
        try:
            vehicle.mileage = int(data["mileage"])
        except (TypeError, ValueError):
            return jsonify({"error": "mileage must be a number"}), 400

    if "nickname" in data:
        vehicle.nickname = data["nickname"]
    if "fuel_type" in data:
        vehicle.fuel_type = data["fuel_type"]
    if "transmission" in data:
        vehicle.transmission = data["transmission"]
    if "purchase_date" in data:
        parsed_date = _parse_date(data["purchase_date"])
        if data["purchase_date"] not in (None, "") and parsed_date is None:
            return jsonify({"error": "purchase_date must be YYYY-MM-DD"}), 400
        vehicle.purchase_date = parsed_date
    if "notes" in data:
        vehicle.notes = data["notes"]

    db.session.commit()
    return jsonify(_vehicle_to_dict(vehicle)), 200


@vehicles_bp.delete("/<int:vehicle_id>")
@jwt_required()
def delete_vehicle(vehicle_id: int):
    user_id = int(get_jwt_identity())
    vehicle = _get_owned_vehicle(vehicle_id, user_id)

    if not vehicle:
        return jsonify({"error": "vehicle not found"}), 404

    db.session.delete(vehicle)
    db.session.commit()

    return jsonify({"message": "vehicle deleted"}), 200