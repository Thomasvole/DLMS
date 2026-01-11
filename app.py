import re
import sqlite3
from datetime import datetime

from flask import Flask, render_template, abort, request, redirect

app = Flask(__name__)

DB_PATH = "dlms.db"
MACHINE_ID_PATTERN = re.compile(r"^[MF][A-D][1-8]$")


def is_valid_machine_id(machine_id: str) -> bool:
    return MACHINE_ID_PATTERN.match(machine_id) is not None


def keep_digits_only(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit())


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with open("schema.sql", "r", encoding="utf-8") as f:
        schema = f.read()
    conn = get_db_connection()
    conn.executescript(schema)
    conn.close()


@app.route("/")
def home():
    return "DLMS running"


@app.route("/init-db")
def init_db_route():
    # Run once to create tables, then you can remove or protect this route
    init_db()
    return "Database initialized."


@app.route("/machine/<machine_id>", methods=["GET"])
def machine_start(machine_id):
    if not is_valid_machine_id(machine_id):
        abort(404)

    return render_template(
        "machine_start.html",
        machine_id=machine_id,
        errors={},
        values={"first_name": "", "last_name": "", "phone_number": ""}
    )


@app.route("/machine/<machine_id>/start", methods=["POST"])
def start_session(machine_id):
    if not is_valid_machine_id(machine_id):
        abort(404)

    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    phone_raw = request.form.get("phone_number", "").strip()
    phone_clean = keep_digits_only(phone_raw)

    errors = {}
    if first_name == "":
        errors["first_name"] = "First name is required"
    if last_name == "":
        errors["last_name"] = "Last name is required"
    if len(phone_clean) != 10:
        errors["phone_number"] = "Enter a valid 10 digit US phone number"

    if errors:
        return render_template(
            "machine_start.html",
            machine_id=machine_id,
            errors=errors,
            values={"first_name": first_name, "last_name": last_name, "phone_number": phone_raw}
        )

    time_in = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "active"

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO sessions (machine_id, first_name, last_name, phone_number, time_in, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (machine_id, first_name, last_name, phone_clean, time_in, status)
    )
    session_id = cur.lastrowid
    conn.commit()
    conn.close()

    return redirect(f"/session/{session_id}")


@app.route("/session/<int:session_id>", methods=["GET"])
def session_confirmation(session_id: int):
    conn = get_db_connection()
    session = conn.execute(
        "SELECT * FROM sessions WHERE session_id = ?",
        (session_id,)
    ).fetchone()
    conn.close()

    if session is None:
        abort(404)

    return render_template("session_started.html", session=session)


if __name__ == "__main__":
    app.run(debug=True)
