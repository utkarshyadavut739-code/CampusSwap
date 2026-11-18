import re

from flask import jsonify

from config import Config

PHONE_RE = re.compile(r"^\d{10}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def json_error(message, status=400):
    return jsonify(error=message), status


def valid_phone(phone):
    return bool(PHONE_RE.match(phone or ""))


def valid_email(email):
    return bool(EMAIL_RE.match(email or ""))


def email_domain_ok(email):
    domain = Config.ALLOWED_EMAIL_DOMAIN
    if not domain:
        return True
    return email.lower().endswith("@" + domain)


def parse_price(value):
    """Return a non-negative int price in rupees, or None if invalid."""
    try:
        price = int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None
    if price < 0 or price > 1_000_000:
        return None
    return price
