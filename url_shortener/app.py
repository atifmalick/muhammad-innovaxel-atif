from flask import Flask, request, jsonify, abort
import sqlite3
import string
import random
from datetime import datetime

app = Flask(__name__)
DB_NAME = "urls.db"

# Initialize database
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            shortcode TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            access_count INTEGER DEFAULT 0
        )
        """)
        conn.commit()

# Generate random shortcode
def generate_shortcode(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

# Create Short URL
@app.route('/shorten', methods=['POST'])
def create_short_url():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "URL is required"}), 400

    url = data['url']
    shortcode = generate_shortcode()

    created_at = updated_at = datetime.utcnow().isoformat()

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO urls (url, shortcode, created_at, updated_at) VALUES (?, ?, ?, ?)",
                       (url, shortcode, created_at, updated_at))
        conn.commit()
        new_id = cursor.lastrowid

    return jsonify({
        "id": new_id,
        "url": url,
        "shortCode": shortcode,
        "createdAt": created_at,
        "updatedAt": updated_at
    }), 201

# Retrieve Original URL
@app.route('/shorten/<string:shortcode>', methods=['GET'])
def get_original_url(shortcode):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, url, shortcode, created_at, updated_at, access_count FROM urls WHERE shortcode = ?", (shortcode,))
        row = cursor.fetchone()

        if row is None:
            abort(404)

        # Update access count
        cursor.execute("UPDATE urls SET access_count = access_count + 1, updated_at = ? WHERE shortcode = ?",
                       (datetime.utcnow().isoformat(), shortcode))
        conn.commit()

    return jsonify({
        "id": row[0],
        "url": row[1],
        "shortCode": row[2],
        "createdAt": row[3],
        "updatedAt": row[4],
        "accessCount": row[5] + 1
    }), 200

# Update Short URL
@app.route('/shorten/<string:shortcode>', methods=['PUT'])
def update_short_url(shortcode):
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "URL is required"}), 400

    new_url = data['url']
    updated_at = datetime.utcnow().isoformat()

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM urls WHERE shortcode = ?", (shortcode,))
        row = cursor.fetchone()

        if row is None:
            abort(404)

        cursor.execute("UPDATE urls SET url = ?, updated_at = ? WHERE shortcode = ?",
                       (new_url, updated_at, shortcode))
        conn.commit()

    return jsonify({
        "id": row[0],
        "url": new_url,
        "shortCode": shortcode,
        "updatedAt": updated_at
    }), 200

# Delete Short URL
@app.route('/shorten/<string:shortcode>', methods=['DELETE'])
def delete_short_url(shortcode):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM urls WHERE shortcode = ?", (shortcode,))
        row = cursor.fetchone()

        if row is None:
            abort(404)

        cursor.execute("DELETE FROM urls WHERE shortcode = ?", (shortcode,))
        conn.commit()

    return '', 204

# Get URL Statistics
@app.route('/shorten/<string:shortcode>/stats', methods=['GET'])
def get_url_stats(shortcode):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, url, shortcode, created_at, updated_at, access_count FROM urls WHERE shortcode = ?", (shortcode,))
        row = cursor.fetchone()

        if row is None:
            abort(404)

    return jsonify({
        "id": row[0],
        "url": row[1],
        "shortCode": row[2],
        "createdAt": row[3],
        "updatedAt": row[4],
        "accessCount": row[5]
    }), 200

# Run app
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
