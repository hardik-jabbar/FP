from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Database setup
DATABASE = 'contact.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL,
                subject TEXT NOT NULL,
                message TEXT NOT NULL
            )
        ''')
        conn.commit()

# Initialize the database
init_db()

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    data = request.json
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    email = data.get('email')
    subject = data.get('subject')
    message = data.get('message')

    if not all([first_name, last_name, email, subject, message]):
        return jsonify({'error': 'All fields are required'}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO contacts (first_name, last_name, email, subject, message)
            VALUES (?, ?, ?, ?, ?)
        ''', (first_name, last_name, email, subject, message))
        conn.commit()

    return jsonify({'message': 'Contact form submitted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)