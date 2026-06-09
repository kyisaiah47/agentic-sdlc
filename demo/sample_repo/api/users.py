from flask import Blueprint, request, jsonify, session
from auth.login import login, reset_password, get_user_profile

bp = Blueprint("users", __name__, url_prefix="/api/users")


@bp.route("/login", methods=["POST"])
def handle_login():
    data = request.get_json()
    ok = login(data["username"], data["password"])
    if ok:
        return jsonify({"status": "ok"})
    return jsonify({"status": "unauthorized"}), 401


@bp.route("/<int:user_id>/reset-password", methods=["POST"])
def handle_reset(user_id: int):
    data = request.get_json()
    # Missing auth check — any logged-in user can reset anyone's password
    reset_password(user_id, data["new_password"])
    return jsonify({"status": "ok"})


@bp.route("/<int:user_id>", methods=["GET"])
def handle_profile(user_id: int):
    profile = get_user_profile(user_id)
    return jsonify(profile)
