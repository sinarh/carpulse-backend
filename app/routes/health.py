from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

health_bp = Blueprint("health", __name__)

@health_bp.get("/")
def health():
    return jsonify({"status": "ok"}), 200

@health_bp.get("/protected")
@jwt_required()
def protected():
    user_id = get_jwt_identity()
    return jsonify({
    "status": "ok",
    "user_id": user_id,
    "message": "JWT is working"
    }), 200