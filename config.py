import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")

    # MySQL
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "tack")

    # Uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

    # Leave blank to allow any email. Example: "cpur.edu.in" restricts signup
    # to addresses ending in @cpur.edu.in
    ALLOWED_EMAIL_DOMAIN = os.getenv("ALLOWED_EMAIL_DOMAIN", "").strip().lower()

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Marketplace data
    CATEGORIES = [
        "Books & Notes",
        "Electronics",
        "Furniture",
        "Bikes & Cycles",
        "Hostel Essentials",
        "Tickets & Passes",
    ]
    HOSTELS = ["Aravali Hostel", "Nilgiri Hostel", "Vindhya Hostel", "Day Scholar"]
    CONDITIONS = {
        "new": "Like new / unused",
        "used": "Used",
        "parts": "For parts",
    }
