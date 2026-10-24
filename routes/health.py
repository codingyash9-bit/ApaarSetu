"""
Health check route for APAAR Nexus.
Returns service status, prototype version, and synthetic data notice.
"""
from flask import Blueprint, jsonify, current_app

health_bp = Blueprint("health", __name__)


@health_bp.route("/api/health", methods=["GET"])
def health_check():
    """Returns application health status."""
    return jsonify({
        "ok": True,
        "data": {
            "status": "healthy",
            "app_name": current_app.config.get("APP_NAME", "APAAR Nexus"),
            "version": current_app.config.get("APP_VERSION", "1.0.0-prototype"),
            "notice": current_app.config.get(
                "SYNTHETIC_NOTICE",
                "Prototype — synthetic data only. Not connected to AICTE, APAAR, UIDAI or DigiLocker."
            )
        }
    }), 200
