import os
from functools import wraps

from flask import current_app, g, jsonify, request
from itsdangerous import BadSignature, SignatureExpired
from itsdangerous import URLSafeTimedSerializer as Serializer


def _get_secret() -> str:
    return current_app.config.get(
        "JWT_SECRET_KEY",
        os.getenv("JWT_SECRET_KEY", current_app.secret_key or "dev-secret"),
    )


def _serializer():
    # URLSafeTimedSerializer requires a secret and a salt; use a stable salt for tokens
    return Serializer(_get_secret(), salt="api-auth-salt")


def create_access_token(identity: str) -> str:
    s = _serializer()
    token = s.dumps({"sub": identity})
    return token.decode("utf-8") if isinstance(token, (bytes, bytearray)) else token


def create_refresh_token(identity: str) -> str:
    s = _serializer()
    token = s.dumps({"sub": identity})
    return token.decode("utf-8") if isinstance(token, (bytes, bytearray)) else token


def _decode(token: str, max_age: int) -> dict:
    s = _serializer()
    return s.loads(token, max_age=max_age)


def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"msg": "Missing Authorization header"}), 401
        token = auth.split(None, 1)[1]
        try:
            data = _decode(token, current_app.config.get("JWT_ACCESS_EXPIRES", 900))
        except SignatureExpired:
            return jsonify({"msg": "Token expired"}), 401
        except BadSignature:
            return jsonify({"msg": "Invalid token"}), 401

        g.current_user = data.get("sub")
        return fn(*args, **kwargs)

    return wrapper


def get_current_user() -> str | None:
    return getattr(g, "current_user", None)
