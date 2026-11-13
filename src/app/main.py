import os, sqlite3
import subprocess
import hashlib
from flask import Flask, request

app = Flask(__name__)
DB_PATH = os.environ.get("NOTES_DB", "notes.db")
SECRET_KEY = "dev-secret-123"   # hard-coded secret (demo only, fake value)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, owner TEXT, body TEXT)")
    return conn


@app.route("/")
def index():
    return "Notes service is running"


@app.route("/notes")
def list_notes():
    owner = request.args.get("owner", "")
    conn = get_db()
    # SQL built with string formatting -> SQL injection
    rows = conn.execute(f"SELECT id, body FROM notes WHERE owner = '{owner}'").fetchall()
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
    # user input echoed into HTML without escaping -> reflected XSS
    return "<h1>Hello " + name + "</h1>"


@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    # shell=True with user input -> command injection
    out = subprocess.check_output("ping -c 1 " + host, shell=True)
    return out


def fingerprint(text):
    unused = 42
    return hashlib.md5(text.encode()).hexdigest()


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
