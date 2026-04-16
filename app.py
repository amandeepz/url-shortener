from flask import Flask, request, redirect, jsonify
import sqlite3
import string
import random

app = Flask(__name__)

# ------------------ DATABASE ------------------
def init_db():
    conn = sqlite3.connect("urls.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_id TEXT UNIQUE,
            long_url TEXT,
            clicks INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

init_db()


# ------------------ GENERATE UNIQUE ID ------------------
def generate_unique_short_id():
    conn = sqlite3.connect("urls.db")
    cursor = conn.cursor()

    characters = string.ascii_letters + string.digits

    while True:
        short_id = ''.join(random.choice(characters) for _ in range(6))

        cursor.execute(
            "SELECT 1 FROM urls WHERE short_id=?",
            (short_id,)
        )

        if not cursor.fetchone():
            conn.close()
            return short_id


# ------------------ SHORTEN API ------------------
@app.route("/shorten", methods=["POST"])
def shorten_url():
    data = request.get_json()
    long_url = data.get("url")

    if not long_url:
        return jsonify({"error": "URL is required"}), 400

    short_id = generate_unique_short_id()

    conn = sqlite3.connect("urls.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO urls (short_id, long_url) VALUES (?, ?)",
        (short_id, long_url)
    )
    conn.commit()
    conn.close()

    return jsonify({
        "short_url": f"http://localhost:5000/{short_id}"
    })


# ------------------ REDIRECT API ------------------
@app.route("/<short_id>")
def redirect_url(short_id):
    conn = sqlite3.connect("urls.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT long_url, clicks FROM urls WHERE short_id=?",
        (short_id,)
    )
    result = cursor.fetchone()

    if result:
        long_url, clicks = result

        # increment click count
        cursor.execute(
            "UPDATE urls SET clicks=? WHERE short_id=?",
            (clicks + 1, short_id)
        )
        conn.commit()
        conn.close()

        return redirect(long_url)
    else:
        conn.close()
        return "URL not found", 404


# ------------------ STATS API ------------------
@app.route("/stats/<short_id>")
def get_stats(short_id):
    conn = sqlite3.connect("urls.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT long_url, clicks, created_at FROM urls WHERE short_id=?",
        (short_id,)
    )
    result = cursor.fetchone()
    conn.close()

    if result:
        return jsonify({
            "long_url": result[0],
            "clicks": result[1],
            "created_at": result[2]
        })
    else:
        return jsonify({"error": "Not found"}), 404


# ------------------ HOME ------------------
@app.route("/")
def home():
    return "URL Shortener is running!"


# ------------------ RUN ------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
