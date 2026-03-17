#!/usr/bin/env python3
"""
Telegram Calendar Reminders
Checks calendar every 5 minutes and sends Telegram notifications 15 minutes before events.
"""
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

os.environ["GOG_KEYRING_PASSWORD"] = "opensesame"

# Config
CHAT_ID = "5606165796"
STATE_FILE = Path("/root/.openclaw/workspace/.calendar_reminders_state.json")
REMINDER_WINDOW_MINUTES = 15
CHECK_AHEAD_HOURS = 24

def load_state():
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except:
            return {"notified_events": []}
    return {"notified_events": []}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def get_upcoming_events():
    """Get events for today and tomorrow"""
    now = datetime.now()
    start_date = now.strftime("%Y-%m-%d")
    end_date = (now + timedelta(days=2)).strftime("%Y-%m-%d")

    try:
        result = subprocess.run(
            ["gog", "calendar", "events", "primary", "--from", start_date, "--to", end_date, "--json", "--no-input"],
            capture_output=True, text=True, timeout=30, env=os.environ
        )
        if result.returncode == 0:
            return json.loads(result.stdout).get("events", [])
    except Exception as e:
        print(f"Error fetching calendar: {e}", file=sys.stderr)
    return []

def send_telegram(message):
    """Send Telegram message"""
    try:
        with open('/root/.openclaw/openclaw.json') as f:
            cfg = json.load(f)
        bot_token = cfg.get('channels', {}).get('telegram', {}).get('botToken')
        if not bot_token:
            return False

        payload = {"chat_id": CHAT_ID, "text": message}
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        urllib.request.urlopen(req, timeout=10).read()
        return True
    except Exception as e:
        print(f"Error sending Telegram: {e}", file=sys.stderr)
        return False

def main():
    state = load_state()
    notified = set(state.get("notified_events", []))

    events = get_upcoming_events()
    now = datetime.now()
    reminder_time = now + timedelta(minutes=REMINDER_WINDOW_MINUTES)

    new_notifications = []

    for event in events:
        event_id = event.get("id")
        if event_id in notified:
            continue

        # Parse start time
        start_str = event.get("start", {}).get("dateTime", "")
        if not start_str:
            continue

        try:
            # Parse ISO format with timezone
            start_time = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            # Convert to local timezone (America/Chicago)
            # Simple approach: we'll keep times as-is and compare with naive now
            # We'll convert start_time to naive local time by extracting the time portion
            start_time_local = start_time.astimezone()
            start_time_naive = datetime(
                start_time_local.year,
                start_time_local.month,
                start_time_local.day,
                start_time_local.hour,
                start_time_local.minute,
                start_time_local.second
            )
        except:
            continue

        # Check if event starts within our reminder window (next 15-20 minutes)
        time_diff = (start_time_naive - now).total_seconds() / 60
        if 0 <= time_diff <= REMINDER_WINDOW_MINUTES + 5:
            summary = event.get("summary", "Event")
            time_formatted = start_time_local.strftime("%I:%M %p")
            message = f"⏰ Reminder: '{summary}' starts at {time_formatted} (in {int(time_diff)} minutes)"
            if send_telegram(message):
                notified.add(event_id)
                new_notifications.append(event_id)

    # Save state
    state["notified_events"] = list(notified)
    save_state(state)

    # Optional: clean old event IDs from state (older than 7 days)
    # For now we keep them growing; can add cleanup later

if __name__ == "__main__":
    main()
