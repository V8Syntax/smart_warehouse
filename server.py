import matplotlib
matplotlib.use('Agg')

from flask import Flask, request, render_template
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

app = Flask(__name__)


def get_db():
    return sqlite3.connect("warehouse.db")


@app.route('/rfid', methods=['POST'])
def receive_data():

    data = request.json

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movements(
        tag_id TEXT,
        reader_id TEXT,
        timestamp TEXT,
        action TEXT
    )
    """)

    cursor.execute("""
    INSERT INTO movements(tag_id, reader_id, timestamp, action)
    VALUES (?, ?, ?, ?)
    """, (data['tag_id'], data['reader_id'], data['timestamp'], data['action']))

    conn.commit()
    conn.close()

    return {"status": "received"}, 200


@app.route('/')
def dashboard():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM movements ORDER BY timestamp DESC LIMIT 20")
    rows = cursor.fetchall()

    # only recent events for better graph updates
    cursor.execute("""
    SELECT tag_id, reader_id, action, timestamp 
    FROM movements 
    ORDER BY timestamp DESC 
    LIMIT 200
    """)

    data = cursor.fetchall()
    data = list(reversed(data))

    stock = 0
    stock_history = []
    tag_location = {}
    suspicious = []
    last_entry = {}

    for tag, reader, action, timestamp in data:

        if action == "entry":
            stock += 1
            last_entry[tag] = timestamp

        elif action == "exit":
            stock -= 1

            if tag in last_entry:

                t1 = datetime.strptime(last_entry[tag], "%Y-%m-%d %H:%M:%S")
                t2 = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

                if (t2 - t1).seconds == 0:
                    if tag not in suspicious:
                        suspicious.append(tag)

        stock_history.append(stock)

        tag_location[tag] = reader

    # analytics cards
    cursor.execute("SELECT COUNT(*) FROM movements")
    total_packets = cursor.fetchone()[0]

    active_items = len(tag_location)

    # ---------- STOCK GRAPH ----------
    if len(stock_history) > 0:

        plt.figure(figsize=(7,4))
        plt.style.use("seaborn-v0_8")

        plt.plot(stock_history, color="#2c3e50", linewidth=2)

        plt.title("Stock Level Trend")
        plt.xlabel("Recent Events")
        plt.ylabel("Stock Count")

        plt.grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig("static/stock.png")
        plt.close()

    # ---------- ACTIVITY GRAPH ----------
    cursor.execute("SELECT timestamp FROM movements")
    timestamps = cursor.fetchall()

    hours = {}

    for t in timestamps:

        hour = t[0][11:13]

        hours[hour] = hours.get(hour, 0) + 1

    if len(hours) > 0:

        plt.figure(figsize=(7,4))
        plt.style.use("seaborn-v0_8")

        plt.bar(hours.keys(), hours.values(), color="#3498db")

        plt.title("Warehouse Activity by Hour")
        plt.xlabel("Hour")
        plt.ylabel("RFID Events")

        plt.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        plt.savefig("static/activity.png")
        plt.close()

    # ---------- ZONE GRAPH ----------
    cursor.execute("SELECT reader_id FROM movements")
    zones = cursor.fetchall()

    zone_count = {}

    for z in zones:
        zone_count[z[0]] = zone_count.get(z[0], 0) + 1

    if len(zone_count) > 0:

        plt.figure(figsize=(7,4))
        plt.style.use("seaborn-v0_8")

        plt.bar(zone_count.keys(), zone_count.values(), color="#27ae60")

        plt.title("Zone Activity")
        plt.xlabel("Warehouse Zones")
        plt.ylabel("Scans")

        plt.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        plt.savefig("static/zones.png")
        plt.close()

    conn.close()

    return render_template(
        "dashboard.html",
        rows=rows,
        stock=stock,
        packets=total_packets,
        active_items=active_items,
        locations=tag_location,
        suspicious=suspicious
    )


if __name__ == "__main__":
    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000)