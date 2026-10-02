from flask import Flask, request, jsonify, send_from_directory
import sqlite3

app = Flask(__name__)
DB_NAME = "donors.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS donors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            location TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return send_from_directory(app.root_path, "blood.html")


@app.route("/api/donors", methods=["GET"])
def get_donors():

    search = request.args.get("search", "").strip()
    group = request.args.get("group", "").strip()

    conn = get_db()

    if group:
        rows = conn.execute("""
            SELECT id, name, phone, email, blood_group, location
            FROM donors
            WHERE (name LIKE ? OR location LIKE ?)
            AND blood_group = ?
            ORDER BY id DESC
        """, (f"%{search}%", f"%{search}%", group)).fetchall()
    else:
        rows = conn.execute("""
            SELECT id, name, phone, email, blood_group, location
            FROM donors
            WHERE name LIKE ? OR location LIKE ?
            ORDER BY id DESC
        """, (f"%{search}%", f"%{search}%")).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


@app.route("/api/donors", methods=["POST"])
def register_donor():

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    email = data.get("email", "").strip()
    group = data.get("group", "").strip()
    location = data.get("location", "").strip()

    if not all([name, phone, email, group, location]):
        return jsonify({"error": "All fields are required"}), 400

    conn = get_db()

    conn.execute("""
        INSERT INTO donors
        (name, phone, email, blood_group, location)
        VALUES (?, ?, ?, ?, ?)
    """, (name, phone, email, group, location))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Donor registered successfully!"
    }), 201


if __name__ == "__main__":
    init_db()

    print("====================================")
    print("Blood Donor Management System")
    print("Server started successfully")
    print("====================================")

    app.run(host="0.0.0.0", port=5000, debug=True)