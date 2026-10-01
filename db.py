"""Small PostgreSQL adapter used by both the bot and the Render web app."""
import os
import re
import psycopg2

try:
    import config as _settings
except Exception:
    _settings = None
DATABASE_URL = os.getenv("DATABASE_URL", "").strip() or (getattr(_settings, "DATABASE_URL", "") if _settings else "").strip()

SCHEMA = """
CREATE TABLE IF NOT EXISTS admin (user_id BIGINT, expire_date TEXT);
CREATE TABLE IF NOT EXISTS admin_licenses (key TEXT, days INTEGER);
CREATE TABLE IF NOT EXISTS code (code TEXT, value INTEGER);
CREATE TABLE IF NOT EXISTS guilds (id BIGINT, role_id BIGINT, token TEXT, expiredate TEXT, verify_webhook TEXT);
CREATE TABLE IF NOT EXISTS licenses (key TEXT, days INTEGER);
CREATE TABLE IF NOT EXISTS log_ids (log_id TEXT, log TEXT);
CREATE TABLE IF NOT EXISTS messages (guild__id BIGINT, name BIGINT, value BIGINT);
CREATE TABLE IF NOT EXISTS restore_log (channel_id BIGINT, admin_id BIGINT);
CREATE TABLE IF NOT EXISTS users (id BIGINT, token TEXT, guild_id BIGINT);
"""


class Cursor:
    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, sql, params=None):
        # Existing source uses SQLite's '?' placeholders and '=='.
        sql = sql.replace("==", "=")
        sql = re.sub(r"\?", "%s", sql)
        self._cursor.execute(sql, params or ())
        return self

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()


class Connection:
    def __init__(self, raw):
        self._raw = raw

    def cursor(self):
        return Cursor(self._raw.cursor())

    def commit(self):
        self._raw.commit()

    def close(self):
        self._raw.close()


def connect():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL을 Render와 Pterodactyl 양쪽에 입력하세요.")
    raw = psycopg2.connect(DATABASE_URL, sslmode="require", connect_timeout=15)
    con = Connection(raw)
    cur = con.cursor()
    for statement in SCHEMA.split(";"):
        if statement.strip():
            cur.execute(statement)
    con.commit()
    return con
