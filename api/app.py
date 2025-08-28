# app.py
from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash
import datetime

app = Flask(__name__)

# PostgreSQL connection
connection = psycopg2.connect(
    dbname='AGT',
    user='postgres',
    password='pgsqtk116chuk95',
    host='chukspace.ctiuisa62ks5.eu-north-1.rds.amazonaws.com',
    port='5432'
)

@app.route('/')
def index():
    return render_template('index.html')

# 🔎 Search workers
@app.route('/workers/search', methods=['POST'])
def worker_search():
    keyword = request.form['keyword']
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    sql_query = """
        SELECT id, first_name, last_name, age, gender, birthday, contact_number,
               age_group, department, relationship_status, email, address, consent
        FROM public."agt_user_data_records"
        WHERE "first_name" ILIKE %s 
           OR "last_name" ILIKE %s 
           OR "age"::TEXT ILIKE %s 
           OR "gender" ILIKE %s
           OR "birthday" ILIKE %s
           OR "contact_number"::TEXT ILIKE %s
           OR "age_group" ILIKE %s
           OR "department" ILIKE %s
           OR "relationship_status" ILIKE %s
           OR "email" ILIKE %s
           OR "address" ILIKE %s
           OR consent::TEXT ILIKE %s
        LIMIT 10
    """
    cursor.execute(sql_query, [f"%{keyword}%"] * 12)
    results = cursor.fetchall()
    cursor.close()

    # With RealDictCursor, `results` is already a list of dicts!
    return jsonify(results)


# 🔎 Get worker details
@app.route('/workers/<int:user_id>', methods=['GET'])
def get_worker_details(user_id):
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    # Get user data first
    cursor.execute("""
        SELECT id, first_name, last_name
        FROM public."agt_user_data_records"
        WHERE id = %s
    """, (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        return jsonify({"error": "User not found"}), 404

    # Check if the user exists in worker table
    cursor.execute("""
        SELECT id AS worker_id, role, department
        FROM public."agt_workers_voluntiers_records"
        WHERE user_id = %s
    """, (user_id,))
    worker = cursor.fetchone()
    cursor.close()

    return jsonify({
        "user": user,
        "worker": worker  # will be null if not found
    })

# ➕ Create admin
@app.route('/admin/create', methods=['POST'])
def create_admin():
    data = request.json
    user_id = data.get("user_id")
    worker_id = data.get("worker_id")
    role = data.get("role")
    user_name = data.get("user_name")
    email = data.get("email")
    password = data.get("password")

    password_hash = generate_password_hash(password)

    cursor = connection.cursor()
    sql_insert = """
        INSERT INTO public."agt_admin" (user_id, worker_id, role, user_name, email, password_hash, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
        RETURNING id
    """
    cursor.execute(sql_insert, (user_id, worker_id, role, user_name, email, password_hash))
    connection.commit()
    new_id = cursor.fetchone()[0]
    cursor.close()

    return jsonify({"success": True, "admin_id": new_id})
# =============================================================================

if __name__ == '__main__':
    app.run(debug=True)
