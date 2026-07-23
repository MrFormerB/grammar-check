#!/usr/bin/env python3
"""
Simple Flask backend for Grammar Check app
Provides persistent storage for teacher groups and student submissions
"""

import os
import json
import sqlite3
import hashlib
import hmac
import secrets
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
DB_PATH = "grammar_check.db"

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Teachers table
    c.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    # Groups table
    c.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            code TEXT PRIMARY KEY,
            teacher_id TEXT NOT NULL,
            name TEXT NOT NULL,
            target_level TEXT NOT NULL,
            structure_ids TEXT NOT NULL,
            admin_token TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (teacher_id) REFERENCES teachers(id)
        )
    """)
    
    # Submissions table
    c.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id TEXT PRIMARY KEY,
            group_code TEXT NOT NULL,
            student_id TEXT NOT NULL,
            data TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (group_code) REFERENCES groups(code)
        )
    """)
    
    # Storage table (for backward compatibility with shared storage)
    c.execute("""
        CREATE TABLE IF NOT EXISTS storage (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            shared INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash a password using PBKDF2"""
    salt = secrets.token_hex(32)
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${hash_obj.hex()}"

def verify_password(password, hash_str):
    """Verify a password against its hash"""
    try:
        salt, hash_hex = hash_str.split('$')
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return hmac.compare_digest(hash_hex, hash_obj.hex())
    except:
        return False

def get_teacher_id_from_request():
    """Extract and verify teacher ID from Authorization header"""
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return None
    token = auth[7:]
    # Token format: teacher_id:session_token
    try:
        teacher_id, session_token = token.split(':')
        # In production, validate session token more thoroughly
        return teacher_id
    except:
        return None

def require_auth(f):
    """Decorator to require teacher authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        teacher_id = get_teacher_id_from_request()
        if not teacher_id:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(teacher_id, *args, **kwargs)
    return decorated

# API Endpoints

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 400
    if not password or len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        teacher_id = secrets.token_hex(16)
        password_hash = hash_password(password)
        c.execute(
            "INSERT INTO teachers (id, username, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (teacher_id, username, password_hash, datetime.utcnow().isoformat())
        )
        conn.commit()
        
        session_token = secrets.token_hex(32)
        return jsonify({
            'success': True,
            'teacher_id': teacher_id,
            'session_token': session_token
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 409
    finally:
        conn.close()

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, password_hash FROM teachers WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    
    if not row or not verify_password(password, row[1]):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    teacher_id = row[0]
    session_token = secrets.token_hex(32)
    return jsonify({
        'success': True,
        'teacher_id': teacher_id,
        'session_token': session_token
    }), 200

@app.route('/api/storage/get', methods=['GET'])
def storage_get():
    key = request.args.get('key')
    shared = request.args.get('shared', 'false').lower() == 'true'
    
    if not key:
        return jsonify({'error': 'Missing key'}), 400
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT value FROM storage WHERE key = ? AND shared = ?", (key, 1 if shared else 0))
    row = c.fetchone()
    conn.close()
    
    if row:
        return jsonify({'value': row[0]})
    return jsonify({'value': None})

@app.route('/api/storage/set', methods=['POST'])
def storage_set():
    data = request.get_json()
    key = data.get('key')
    value = data.get('value')
    shared = data.get('shared', False)
    
    if not key or value is None:
        return jsonify({'error': 'Missing key or value'}), 400
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO storage (key, value, shared, created_at) VALUES (?, ?, ?, ?)",
        (key, value, 1 if shared else 0, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/storage/list', methods=['GET'])
def storage_list():
    prefix = request.args.get('prefix', '')
    shared = request.args.get('shared', 'false').lower() == 'true'
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT key FROM storage WHERE key LIKE ? AND shared = ?",
        (prefix + '%', 1 if shared else 0)
    )
    rows = c.fetchall()
    conn.close()
    
    return jsonify({'keys': [row[0] for row in rows]})

@app.route('/api/teacher/info', methods=['GET'])
@require_auth
def teacher_info(teacher_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, created_at FROM teachers WHERE id = ?", (teacher_id,))
    row = c.fetchone()
    
    if not row:
        return jsonify({'error': 'Teacher not found'}), 404
    
    c.execute("SELECT COUNT(*) FROM groups WHERE teacher_id = ?", (teacher_id,))
    group_count = c.fetchone()[0]
    conn.close()
    
    return jsonify({
        'id': row[0],
        'username': row[1],
        'created_at': row[2],
        'group_count': group_count
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='127.0.0.1', port=5000)
