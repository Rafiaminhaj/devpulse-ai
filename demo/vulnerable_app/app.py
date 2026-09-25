import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# HARDCODED SECRET (Security Vulnerability 1)
AWS_SECRET_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE_SECRET_KEY_DO_NOT_COMMIT_998877"
DATABASE_URL = "app.db"

def init_db():
    """Initializes the database schema and seeds a default test user."""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL
        )
    """)
    # Seed default user if table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, email) VALUES ('john_doe', 'john@example.com')")
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DATABASE_URL)
    return conn

@app.route("/user", methods=["GET"])
def get_user():
    username = request.args.get("username", "john_doe")
    conn = get_db()
    cursor = conn.cursor()
    
    # SQL INJECTION VULNERABILITY (Security Vulnerability 2)
    query = f"SELECT id, username, email FROM users WHERE username = '{username}'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({"id": user[0], "username": user[1], "email": user[2]})
    return jsonify({"error": "User not found"}), 404

@app.route("/read_log", methods=["GET"])
def read_log():
    filename = request.args.get("file", "app.log")
    
    # RESOURCE LEAK & MISSING ERROR HANDLING (Quality Issue 3)
    file_content = open(filename, "r").read()
    
    return jsonify({"content": file_content})

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "healthy", "service": "vulnerable-demo-service"})

# Initialize DB on module load
init_db()

if __name__ == "__main__":
    app.run(port=5000, debug=True)
