import requests
import random
import time
from datetime import datetime

tags = ["A101", "A102", "B201", "C301"]
readers = ["Gate_Entry", "Zone_A", "Zone_B", "Gate_Exit"]
actions = ["entry", "move", "exit"]

while True:
    event = {
        "tag_id": random.choice(tags),
        "reader_id": random.choice(readers),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": random.choice(actions)
    }

    try:
        response = requests.post(
            "http://127.0.0.1:5000/rfid",
            json=event
        )
        print("Sent:", event, "| Status:", response.status_code)

    except Exception as e:
        print("Error sending data:", e)

    time.sleep(0.1)  # 10 events per second