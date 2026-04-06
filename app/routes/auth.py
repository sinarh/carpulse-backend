from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from ..extensions import db
from ..models.user import User
from ..utils.security import hash_password, verify_password

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/register")
def register():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400
    if len(password.encode("utf-8")) > 72:
        return jsonify ({"error": "password too long (max 72 bytes)"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email already registered"}), 409

    user = User(email=email, password_hash=hash_password(password))
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "registered"}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(password, user.password_hash):
        return jsonify({"error": "invalid credentials"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token}), 200
