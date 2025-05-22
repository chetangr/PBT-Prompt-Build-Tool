import os
import requests
from datetime import datetime

def send_weekly_report():
    # Mock email sender
    print(f"[{datetime.utcnow()}] Sending weekly usage digest...")

def call_webhook():
    requests.post("https://yourapp.com/webhook", json={"event": "weekly_digest", "status": "sent"})

if __name__ == "__main__":
    send_weekly_report()
    call_webhook()
