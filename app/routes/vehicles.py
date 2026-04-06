from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import Vehicle

vehicles_bp = Blueprint("vehicles", __name__)

@vehicles_bp.post("/")
@jwt_required()
def create_vehicle():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    vehicle = Vehicle(
        user_id=user_id,
        make=data.get("make"),
        model=data.get("model"),
        year=data.get("year"),
        mileage=data.get("mileage"),
    )

    db.session.add(vehicle)
    db.session.commit()

    return jsonify({"id": vehicle.id}), 201


@vehicles_bp.get("/")
@jwt_required()
def list_vehicles():
    user_id = int(get_jwt_identity())
    vehicles = Vehicle.query.filter_by(user_id=user_id).all()

    return jsonify([
        {
            "id": v.id,
            "make": v.make,
            "model": v.model,
            "year": v.year,
            "mileage": v.mileage,
        }
        for v in vehicles
    ]), 200
