from flask import Blueprint, request, jsonify, current_app, session
from datetime import datetime, timedelta
from database.db import db
from database.models import LoginAttempt
from security.risk_engine import calculate_risk
import requests

security_bp = Blueprint("security", __name__)


@security_bp.route("/check-login", methods=["POST"])
def check_login():

    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request"}), 400

    user_id = data.get("user_id")
    success = data.get("success", False)

    if not user_id:
        return jsonify({"error": "User ID missing"}), 400

    ip_address = request.remote_addr
    user_agent = request.headers.get("User-Agent")

    # ---------------- FETCH RECENT ATTEMPTS ----------------
    window = datetime.utcnow() - timedelta(
        minutes=current_app.config.get("LOGIN_ATTEMPT_WINDOW_MINUTES", 5)
    )

    recent_attempts = LoginAttempt.query.filter(
        LoginAttempt.user_id == user_id,
        LoginAttempt.timestamp >= window
    ).all()

    # ---------------- INTERNAL RULE ENGINE ----------------
    risk_score = calculate_risk(ip_address, user_agent, recent_attempts)

    # ---------------- SAVE ATTEMPT ----------------
    attempt = LoginAttempt(
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
        risk_score=risk_score
    )

    db.session.add(attempt)
    db.session.commit()

    # ---------------- HARD BLOCK (Rule Based) ----------------
    if risk_score >= current_app.config.get("HIGH_RISK_SCORE_THRESHOLD", 80):
        return jsonify({
            "status": "blocked",
            "source": "rule_engine",
            "risk_score": risk_score
        }), 403

    # ---------------- 🔥 ML SERVICE CALL ----------------
    try:
        ml_response = requests.post(
            current_app.config["ML_SERVICE_URL"],
            json={
                "attempts": len(recent_attempts),
                "status": "success" if success else "fail"
            },
            timeout=3
        )

        ml_data = ml_response.json()

    except Exception as e:
        print("ML Service Error:", e)

        # If ML fails → allow but mark low confidence
        return jsonify({
            "status": "allowed",
            "source": "fallback",
            "risk_score": risk_score,
            "ask_user_choice": False
        }), 200

    decision = ml_data.get("decision")
    ml_risk_score = ml_data.get("risk_score", 0)

    # ---------------- ML DECISION HANDLING ----------------
    if decision == "BLOCK":
        return jsonify({
            "status": "blocked",
            "source": "ml_model",
            "risk_score": ml_risk_score
        }), 403

    if decision == "OTP_REQUIRED":
        return jsonify({
            "status": "otp_required",
            "source": "ml_model"
        }), 200

    if decision == "SUSPICIOUS":
        # 🔥 store in session for dashboard use
        session["ml_result"] = "Suspicious Login"

        return jsonify({
            "status": "suspicious",
            "source": "ml_model",
            "risk_score": ml_risk_score,
            "ask_user_choice": True
        }), 200

    # ---------------- NORMAL CASE ----------------
    session["ml_result"] = "Normal Login"

    return jsonify({
        "status": "allowed",
        "source": "ml_model",
        "risk_score": ml_risk_score,
        "ask_user_choice": False
    }), 200
