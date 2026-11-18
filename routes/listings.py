import os
import uuid

from flask import (
    Blueprint,
    abort,
    current_app,
    jsonify,
    render_template,
    request,
    session,
)
from werkzeug.utils import secure_filename

from config import Config
from database.db import execute, query
from utils.decorators import login_required
from utils.validators import json_error, parse_price, valid_phone

listings_bp = Blueprint("listings", __name__)

# Whitelist: user input never goes straight into ORDER BY
SORTS = {
    "newest": "l.created_at DESC",
    "price_asc": "l.price ASC",
    "price_desc": "l.price DESC",
    "hostel": "l.hostel ASC, l.created_at DESC",
}


def image_url(path):
    return f"/static/uploads/{path}" if path else None


def to_public(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "category": row["category"],
        "price": row["price"],
        "condition": row["item_condition"],
        "condition_label": Config.CONDITIONS.get(row["item_condition"], ""),
        "description": row["description"],
        "hostel": row["hostel"],
        "image": image_url(row["image_path"]),
        "status": row["status"],
        "created_at": row["created_at"].isoformat(),
        "seller_name": row.get("seller_name"),
    }


def save_image(file):
    """Save an uploaded image and return its stored filename (or None)."""
    if not file or not file.filename:
        return None
    ext = secure_filename(file.filename).rsplit(".", 1)[-1].lower()
    if ext not in current_app.config["ALLOWED_EXTENSIONS"]:
        raise ValueError("Photo must be a PNG, JPG or WEBP image.")
    name = f"{uuid.uuid4().hex}.{ext}"
    file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], name))
    return name


def remove_image(name):
    if not name:
        return
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], os.path.basename(name))
    if os.path.exists(path):
        os.remove(path)


def get_owned(listing_id):
    return query(
        "SELECT * FROM listings WHERE id = %s AND seller_id = %s",
        (listing_id, session["user_id"]),
        one=True,
    )


# ---------- Pages ----------

@listings_bp.get("/")
def index():
    active = query("SELECT COUNT(*) AS n FROM listings WHERE status = 'active'", one=True)["n"]
    me = None
    if "user_id" in session:
        me = query("SELECT phone, hostel FROM users WHERE id = %s", (session["user_id"],), one=True)
    return render_template("index.html", active_count=active, me=me)


@listings_bp.get("/my-listings")
@login_required
def my_listings_page():
    return render_template("my_listings.html")


@listings_bp.get("/listing/<int:listing_id>")
def detail(listing_id):
    row = query(
        "SELECT l.*, u.name AS seller_name FROM listings l "
        "JOIN users u ON u.id = l.seller_id WHERE l.id = %s",
        (listing_id,),
        one=True,
    )
    if not row:
        abort(404)
    return render_template(
        "listing_detail.html",
        listing=row,
        image=image_url(row["image_path"]),
        condition_label=Config.CONDITIONS.get(row["item_condition"], ""),
        is_owner=row["seller_id"] == session.get("user_id"),
    )


# ---------- API ----------

@listings_bp.get("/api/listings")
def api_list():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "")
    max_price = request.args.get("max_price", "")
    condition = request.args.get("condition", "")
    hostel = request.args.get("hostel", "")
    sort = request.args.get("sort", "newest")

    where = ["l.status = 'active'"]
    params = []

    if q:
        like = f"%{q}%"
        where.append("(l.title LIKE %s OR l.description LIKE %s)")
        params += [like, like]
    if category == "Free Stuff":
        where.append("l.price = 0")
    elif category in Config.CATEGORIES:
        where.append("l.category = %s")
        params.append(category)
    if max_price.isdigit():
        where.append("l.price <= %s")
        params.append(int(max_price))
    if condition in Config.CONDITIONS:
        where.append("l.item_condition = %s")
        params.append(condition)
    if hostel in Config.HOSTELS:
        where.append("l.hostel = %s")
        params.append(hostel)

    order = SORTS.get(sort, SORTS["newest"])
    rows = query(
        "SELECT l.*, u.name AS seller_name FROM listings l "
        "JOIN users u ON u.id = l.seller_id "
        f"WHERE {' AND '.join(where)} ORDER BY {order} LIMIT 100",
        params,
    )
    return jsonify(listings=[to_public(r) for r in rows])


@listings_bp.get("/api/my-listings")
@login_required
def api_mine():
    rows = query(
        "SELECT l.*, u.name AS seller_name FROM listings l "
        "JOIN users u ON u.id = l.seller_id "
        "WHERE l.seller_id = %s ORDER BY l.created_at DESC",
        (session["user_id"],),
    )
    return jsonify(listings=[to_public(r) for r in rows])


def validate_fields(form, require_all=True):
    """Validate listing fields. Returns (clean_dict, error_message)."""
    clean = {}
    title = (form.get("title") or "").strip()
    if require_all or "title" in form:
        if len(title) < 3 or len(title) > 100:
            return None, "Title must be 3-100 characters."
        clean["title"] = title

    if require_all or "price" in form:
        price = parse_price(form.get("price"))
        if price is None:
            return None, "Enter 0 or a positive price."
        clean["price"] = price

    if require_all or "description" in form:
        desc = (form.get("description") or "").strip()
        if len(desc) > 1000:
            return None, "Description is too long (max 1000 characters)."
        clean["description"] = desc

    if require_all:
        category = form.get("category")
        if category not in Config.CATEGORIES:
            return None, "Choose a category."
        condition = form.get("condition")
        if condition not in Config.CONDITIONS:
            return None, "Choose the item's condition."
        hostel = form.get("hostel")
        if hostel not in Config.HOSTELS:
            return None, "Choose a hostel / block."
        phone = (form.get("phone") or "").strip()
        if not valid_phone(phone):
            return None, "Enter a valid 10-digit phone number."
        clean.update(category=category, condition=condition, hostel=hostel, phone=phone)
    return clean, None


@listings_bp.post("/api/listings")
@login_required
def api_create():
    clean, error = validate_fields(request.form)
    if error:
        return json_error(error)
    try:
        filename = save_image(request.files.get("photo"))
    except ValueError as exc:
        return json_error(str(exc))

    listing_id = execute(
        "INSERT INTO listings "
        "(seller_id, title, category, price, item_condition, description, hostel, phone, image_path) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (
            session["user_id"],
            clean["title"],
            clean["category"],
            clean["price"],
            clean["condition"],
            clean["description"],
            clean["hostel"],
            clean["phone"],
            filename,
        ),
    )
    return jsonify(ok=True, id=listing_id), 201


@listings_bp.put("/api/listings/<int:listing_id>")
@login_required
def api_update(listing_id):
    if not get_owned(listing_id):
        return json_error("Listing not found.", 404)
    data = request.get_json(silent=True) or {}
    clean, error = validate_fields(data, require_all=False)
    if error:
        return json_error(error)
    if not clean:
        return json_error("Nothing to update.")

    sets = ", ".join(f"{col} = %s" for col in clean)  # column names come from our own dict keys
    execute(f"UPDATE listings SET {sets} WHERE id = %s", [*clean.values(), listing_id])
    return jsonify(ok=True)


@listings_bp.post("/api/listings/<int:listing_id>/sold")
@login_required
def api_toggle_sold(listing_id):
    row = get_owned(listing_id)
    if not row:
        return json_error("Listing not found.", 404)
    new_status = "active" if row["status"] == "sold" else "sold"
    execute("UPDATE listings SET status = %s WHERE id = %s", (new_status, listing_id))
    return jsonify(ok=True, status=new_status)


@listings_bp.delete("/api/listings/<int:listing_id>")
@login_required
def api_delete(listing_id):
    row = get_owned(listing_id)
    if not row:
        return json_error("Listing not found.", 404)
    execute("DELETE FROM listings WHERE id = %s", (listing_id,))
    remove_image(row["image_path"])
    return jsonify(ok=True)


@listings_bp.get("/api/listings/<int:listing_id>/contact")
@login_required
def api_contact(listing_id):
    """Seller's phone number is only revealed to logged-in users."""
    row = query(
        "SELECT l.phone, l.status, u.name AS seller_name FROM listings l "
        "JOIN users u ON u.id = l.seller_id WHERE l.id = %s",
        (listing_id,),
        one=True,
    )
    if not row:
        return json_error("Listing not found.", 404)
    if row["status"] != "active":
        return json_error("This item has been sold.", 410)
    return jsonify(phone=row["phone"], seller_name=row["seller_name"])
