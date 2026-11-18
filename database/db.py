import mysql.connector
from flask import current_app, g


def get_db():
    """One MySQL connection per request, stored on flask.g."""
    if "db" not in g:
        cfg = current_app.config
        g.db = mysql.connector.connect(
            host=cfg["DB_HOST"],
            port=cfg["DB_PORT"],
            user=cfg["DB_USER"],
            password=cfg["DB_PASSWORD"],
            database=cfg["DB_NAME"],
            charset="utf8mb4",
        )
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query(sql, params=None, one=False):
    """Run a SELECT. Returns a list of dicts, or a single dict/None if one=True."""
    cur = get_db().cursor(dictionary=True)
    cur.execute(sql, params or ())
    rows = cur.fetchall()
    cur.close()
    if one:
        return rows[0] if rows else None
    return rows


def execute(sql, params=None):
    """Run INSERT/UPDATE/DELETE. Returns the last inserted id."""
    db = get_db()
    cur = db.cursor()
    cur.execute(sql, params or ())
    db.commit()
    last_id = cur.lastrowid
    cur.close()
    return last_id
