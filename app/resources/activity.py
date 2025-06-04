"""
User activity feed endpoints.

Added 2025-06-04
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.activity_log import ActivityLog

activity_bp = Blueprint("activity", __name__)

@activity_bp.route("/activities", methods=["GET"])
@jwt_required()
def get_my_activities():
    """
    Return the authenticated user’s recent activity log entries.

    Query-string parameters (all optional):
        limit   – max rows to return (default 50, max 100)
        offset  – starting row (default 0)
    """
    user_id = get_jwt_identity()
    if isinstance(user_id, str):
        user_id = int(user_id)

    try:
        limit = min(int(request.args.get("limit", 50)), 100)
        offset = int(request.args.get("offset", 0))
    except ValueError:
        return jsonify({"error": "limit and offset must be integers"}), 400

    logs = ActivityLog.get_user_activities(
        user_id=user_id,
        limit=limit,
        offset=offset
    )

    return jsonify([entry.to_dict() for entry in logs]), 200