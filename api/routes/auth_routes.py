import os

from flask import Blueprint, current_app, jsonify, request
from itsdangerous import BadSignature, SignatureExpired

from api.auth import _decode, create_access_token, create_refresh_token

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    admin_user = os.getenv("ADMIN_USERNAME", "admin")
    admin_pass = os.getenv("ADMIN_PASSWORD", "password")

    if not username or not password or username != admin_user or password != admin_pass:
        return jsonify({"msg": "Invalid credentials"}), 401

    access = create_access_token(username)
    refresh = create_refresh_token(username)

    return jsonify({"access_token": access, "refresh_token": refresh}), 200


@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    data = request.get_json() or {}
    token = data.get("refresh_token")
    if not token:
        return jsonify({"msg": "Missing refresh_token"}), 400
    try:
        payload = _decode(token, current_app.config.get("JWT_REFRESH_EXPIRES", 86400))
    except SignatureExpired:
        return jsonify({"msg": "Refresh token expired"}), 401
    except BadSignature:
        return jsonify({"msg": "Invalid refresh token"}), 401

    identity = payload.get("sub")
    access = create_access_token(identity)
    return jsonify({"access_token": access}), 200
