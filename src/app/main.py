import hashlib
import ipaddress
import os
import sqlite3

from flask import Flask, abort, request
from markupsafe import escape

app = Flask(__name__)
DB_PATH = os.environ.get("NOTES_DB", "notes.db")
# Secret now comes from the environment (GitHub secret in CI), never from source code.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", os.urandom(32))


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, owner TEXT, body TEXT)"
    )
    return conn


@app.route("/")
def index():
    return "Notes service is running"


@app.route("/notes")
def list_notes():
    owner = request.args.get("owner", "")
    conn = get_db()
    # Parameterised query: the driver treats `owner` as data, never as SQL.
    rows = conn.execute("SELECT id, body FROM notes WHERE owner = ?", (owner,)).fetchall()
    conn.close()
    return {"owner": owner, "notes": [{"id": r[0], "body": r[1]} for r in rows]}


@app.route("/notes", methods=["POST"])
def add_note():
    data = request.get_json(force=True)
    conn = get_db()
    conn.execute("INSERT INTO notes (owner, body) VALUES (?, ?)", (data["owner"], data["body"]))
    conn.commit()
    conn.close()
    return {"status": "created"}, 201


@app.route("/hello")
def hello():
    name = request.args.get("name", "world")
    return "<h1>Hello " + str(escape(name)) + "</h1>"


@app.route("/ping")
def ping():
    # Only accept a literal IP address; no shell is involved any more.
    try:
        host = ipaddress.ip_address(request.args.get("host", "127.0.0.1"))
    except ValueError:
        abort(400)
    return {"host": str(host), "reachable": host.is_loopback or host.is_private}


def fingerprint(text):
    return hashlib.sha256(text.encode()).hexdigest()


if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=os.environ.get("FLASK_DEBUG") == "1")
