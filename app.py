import os
import csv
import sqlite3
from datetime import datetime
from flask import Flask, render_template, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from tuya_device import get_device_status, turn_on, turn_off

app = Flask(__name__)

BASEDIR = os.path.abspath(os.path.dirname(__file__))
DB      = os.path.join(BASEDIR, 'energy.db')
CSV     = os.path.join(BASEDIR, 'energy.csv')

def init_storage():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
      CREATE TABLE IF NOT EXISTS readings (
        ts       TEXT PRIMARY KEY,
        power    REAL,
        current  REAL,
        voltage  REAL
      )
    """)
    conn.commit()
    conn.close()

    if not os.path.exists(CSV):
        with open(CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ts', 'power', 'current', 'voltage'])

init_storage()

def record_reading():
    status = get_device_status()
    now_ts = datetime.utcnow().isoformat()
    print(f"[{now_ts}] record_reading → {status}")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
      "INSERT OR REPLACE INTO readings (ts,power,current,voltage) VALUES (?,?,?,?)",
      (now_ts, status["power"], status["current"], status["voltage"])
    )
    conn.commit()
    conn.close()

    with open(CSV, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([now_ts, status["power"], status["current"], status["voltage"]])

scheduler = BackgroundScheduler()
print("Scheduler starting…")
scheduler.add_job(record_reading, 'interval', minutes=5, next_run_time=datetime.utcnow())
scheduler.start()

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/status")
def api_status():
    return jsonify(get_device_status())

@app.route("/data")
def api_data():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT ts, power FROM readings ORDER BY ts ASC")
    rows = c.fetchall()
    conn.close()

    return jsonify([
        {"ts": ts, "power": power}
        for ts, power in rows
    ])



@app.route("/on")
def power_on():
    turn_on()
    return ("", 204)

@app.route("/off")
def power_off():
    turn_off()
    return ("", 204)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
