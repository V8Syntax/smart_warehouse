from flask import Flask, request
import sqlite3

app = Flask(__name__)

# Create database + table if not exists
def init_db():
    conn = sqlite3.connect("warehouse.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movements (
            tag_id TEXT,
            reader_id TEXT,
            timestamp TEXT,
            action TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# API route to receive RFID events
@app.route('/rfid', methods=['POST'])
def receive_data():
    data = request.json

    conn = sqlite3.connect("warehouse.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO movements VALUES (?, ?, ?, ?)",
        (data['tag_id'], data['reader_id'], data['timestamp'], data['action'])
    )

    conn.commit()
    conn.close()

    return {"status": "received"}, 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)