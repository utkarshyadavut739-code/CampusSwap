from flask import Blueprint, jsonify, request, session

from database.db import execute, query
from utils.decorators import login_required
from utils.validators import json_error

messages_bp = Blueprint("messages", __name__)


@messages_bp.post("/api/listings/<int:listing_id>/message")
@login_required
def send_message(listing_id):
    d = request.get_json(silent=True) or {}
    body = (d.get("body") or "").strip()
    if len(body) < 2 or len(body) > 500:
        return json_error("Message must be 2-500 characters.")

    listing = query(
        "SELECT seller_id, status FROM listings WHERE id = %s", (listing_id,), one=True
    )
    if not listing:
        return json_error("Listing not found.", 404)
    if listing["status"] != "active":
        return json_error("This item has been sold.", 410)
    if listing["seller_id"] == session["user_id"]:
        return json_error("You can't message yourself.")

    execute(
        "INSERT INTO messages (listing_id, sender_id, body) VALUES (%s, %s, %s)",
        (listing_id, session["user_id"], body),
    )
    return jsonify(ok=True), 201


@messages_bp.get("/api/inbox")
@login_required
def inbox():
    """Messages that buyers sent about the logged-in user's listings."""
    rows = query(
        "SELECT m.id, m.body, m.created_at, l.id AS listing_id, l.title, "
        "u.name AS sender_name, u.phone AS sender_phone, u.email AS sender_email "
        "FROM messages m "
        "JOIN listings l ON l.id = m.listing_id "
        "JOIN users u ON u.id = m.sender_id "
        "WHERE l.seller_id = %s ORDER BY m.created_at DESC LIMIT 50",
        (session["user_id"],),
    )
    for r in rows:
        r["created_at"] = r["created_at"].isoformat()
    return jsonify(messages=rows)
