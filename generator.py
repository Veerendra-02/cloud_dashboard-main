import sqlite3
import time
import random
from datetime import datetime

# Connect to a local database (creates the file if it doesn't exist)
conn = sqlite3.connect('local_metrics.db')
cursor = conn.cursor()

# Create the table for our data
cursor.execute('''
    CREATE TABLE IF NOT EXISTS metrics (
        timestamp TEXT, 
        cpu_usage REAL, 
        active_users INTEGER
    )
''')
conn.commit()

print("Starting real-time data generation... Press Ctrl+C to stop.")

try:
    while True:
        # Generate fake data
        current_time = datetime.now().strftime('%H:%M:%S')
        cpu = round(random.uniform(20.0, 95.0), 2)
        users = random.randint(100, 500)

        # Insert into database
        cursor.execute("INSERT INTO metrics VALUES (?, ?, ?)", (current_time, cpu, users))
        conn.commit()

        print(f"Inserted -> Time: {current_time} | CPU: {cpu}% | Users: {users}")
        
        # Wait 2 seconds before generating the next data point
        time.sleep(2) 
        
except KeyboardInterrupt:
    print("\nData generation stopped.")
finally:
    conn.close()