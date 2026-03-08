import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Connect to database
conn = sqlite3.connect("warehouse.db")

# Load data
df = pd.read_sql_query("SELECT * FROM movements", conn)

conn.close()

# Calculate stock level
stock = 0
stock_levels = []

for action in df['action']:
    if action == "entry":
        stock += 1
    elif action == "exit":
        stock -= 1
    stock_levels.append(stock)

df['stock'] = stock_levels

# Plot stock graph
plt.figure()
plt.plot(df.index, df['stock'])
plt.title("Stock Level Over Time")
plt.xlabel("Event Number")
plt.ylabel("Stock Count")
plt.show()
