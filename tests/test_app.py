import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.main import app  # noqa: E402


def client(tmp_path):
    os.environ["NOTES_DB"] = str(tmp_path / "test.db")
    import app.main as m
    m.DB_PATH = os.environ["NOTES_DB"]
    app.config["TESTING"] = True
    return app.test_client()


def test_index(tmp_path):
    c = client(tmp_path)
    assert c.get("/").status_code == 200


def test_add_and_list_notes(tmp_path):
    c = client(tmp_path)
    r = c.post("/notes", json={"owner": "eva", "body": "hello"})
    assert r.status_code == 201
    r = c.get("/notes?owner=eva")
    assert r.get_json()["notes"][0]["body"] == "hello"


def test_sql_injection_is_not_possible(tmp_path):
    c = client(tmp_path)
    c.post("/notes", json={"owner": "alice", "body": "secret"})
    r = c.get("/notes?owner=x' OR '1'='1")
    assert r.get_json()["notes"] == []


def test_hello_escapes_html(tmp_path):
    c = client(tmp_path)
    r = c.get("/hello?name=<script>alert(1)</script>")
    assert b"<script>" not in r.data
