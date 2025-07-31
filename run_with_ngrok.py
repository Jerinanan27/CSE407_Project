from flask import Flask
from app import app  # This imports your actual Flask app
from threading import Thread
import os

# Automatically start ngrok if installed
def start_ngrok():
    os.system("ngrok http 5000")

if __name__ == "__main__":
    print("Starting ngrok tunnel...")
    Thread(target=start_ngrok).start()
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=5000)
