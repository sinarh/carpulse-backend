from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from openai import OpenAI
import os

from ..extensions import db
from ..models.vehicle import Vehicle
from ..models.vehicle_log import VehicleLog

ai_bp = Blueprint("ai", __name__, url_prefix="/ai")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@ai_bp.route("/chat/", methods=["POST"])
@jwt_required()
def chat():
    data = request.get_json(silent=True) or {}
    vehicle_id = data.get("vehicle_id")
    user_message = (data.get("message") or "").strip()

    if not vehicle_id or not user_message:
        return jsonify({"error": "vehicle_id and message required"}), 400

    user_id = int(get_jwt_identity())

    vehicle = Vehicle.query.filter_by(id=vehicle_id, user_id=user_id).first()
    if not vehicle:
        return jsonify({"error": "vehicle not found"}), 404

    logs = (
        VehicleLog.query
        .filter_by(vehicle_id=vehicle.id)
        .order_by(VehicleLog.created_at.desc())
        .limit(20)
        .all()
    )

    # Build a compact context (keep it short to control cost)
    log_lines = []
    for l in reversed(logs):
        log_lines.append(
            f"- {l.created_at.isoformat()} | mileage={l.mileage} | fuel={l.fuel_level} | temp={l.engine_temp} | notes={l.notes or ''}"
        )

    system_text = (
        "You are CarPulse, an automotive maintenance assistant. "
        "Use ONLY the vehicle profile + logs provided. "
        "Be practical and conservative. If data is missing, say what you need. "
        "Output: short diagnosis + 3-6 actionable steps."
    )

    context_text = (
        f"Vehicle: {vehicle.year} {vehicle.make} {vehicle.model}\n"
        f"Known mileage: {vehicle.mileage}\n"
        "Recent logs:\n" + ("\n".join(log_lines) if log_lines else "- (no logs yet)")
    )

    # Responses API call (recommended)
    resp = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": system_text},
            {"role": "user", "content": context_text},
            {"role": "user", "content": f"User question: {user_message}"},
        ],
    )

    return jsonify({"reply": resp.output_text}), 200
