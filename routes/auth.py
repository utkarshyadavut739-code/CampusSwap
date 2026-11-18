from flask import Blueprint, jsonify, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config
from database.db import execute, query
from utils.validators import (
    email_domain_ok,
    json_error,
    valid_email,
    valid_phone,
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/login")
def login():
    return render_template("login.html", next=request.args.get("next", ""))


@auth_bp.get("/register")
def register():
    return render_template("register.html")


@auth_bp.post("/api/register")
def api_register():
    d = request.get_json(silent=True) or {}
    name = (d.get("name") or "").strip()
    email = (d.get("email") or "").strip().lower()
    phone = (d.get("phone") or "").strip()
    hostel = (d.get("hostel") or "").strip()
    password = d.get("password") or ""

    if len(name) < 2 or len(name) > 80:
        return json_error("Enter your name (2-80 characters).")
    if not valid_email(email):
        return json_error("Enter a valid email address.")
    if not email_domain_ok(email):
        return json_error(f"Please use your college email (@{Config.ALLOWED_EMAIL_DOMAIN}).")
    if not valid_phone(phone):
        return json_error("Enter a valid 10-digit phone number.")
    if hostel not in Config.HOSTELS:
        return json_error("Choose your hostel.")
    if len(password) < 8:
        return json_error("Password must be at least 8 characters.")

    if query("SELECT id FROM users WHERE email = %s", (email,), one=True):
        return json_error("An account with this email already exists.", 409)

    user_id = execute(
        "INSERT INTO users (name, email, password_hash, phone, hostel) VALUES (%s, %s, %s, %s, %s)",
        (name, email, generate_password_hash(password), phone, hostel),
    )
    session.clear()
    session["user_id"] = user_id
    session["user_name"] = name
    return jsonify(ok=True)


@auth_bp.post("/api/login")
def api_login():
    d = request.get_json(silent=True) or {}
    email = (d.get("email") or "").strip().lower()
    password = d.get("password") or ""

    user = query("SELECT * FROM users WHERE email = %s", (email,), one=True)
    if not user or not check_password_hash(user["password_hash"], password):
        return json_error("Wrong email or password.", 401)

    session.clear()
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    return jsonify(ok=True)


@auth_bp.post("/api/logout")
def api_logout():
    session.clear()
    return jsonify(ok=True)
