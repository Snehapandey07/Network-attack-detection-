from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

DATABASE = "database.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    with open("schema.sql", "r") as f:
        conn.executescript(f.read())

    conn.commit()
    conn.close()


@app.route("/")
def index():
    conn = get_db_connection()

    computers = conn.execute(
        "SELECT * FROM computers"
    ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        computers=computers
    )


@app.route("/add_computer", methods=["POST"])
def add_computer():

    name = request.form["name"]
    ip_address = request.form["ip_address"]
    device_type = request.form["device_type"]

    conn = get_db_connection()

    conn.execute(
        """
        INSERT INTO computers
        (name, ip_address, device_type)
        VALUES (?, ?, ?)
        """,
        (name, ip_address, device_type)
    )

    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)