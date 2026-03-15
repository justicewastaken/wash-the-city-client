#!/usr/bin/env python3
import json, os, subprocess, urllib.request
from datetime import datetime

os.environ["GOG_KEYRING_PASSWORD"] = "opensesame"

# Get bot token from config
with open('/root/.openclaw/openclaw.json') as f:
    cfg = json.load(f)
bot_token = cfg.get('channels', {}).get('telegram', {}).get('botToken')
chat_id = "5606165796"

# Weather - robust fetch with fallbacks
try:
    # Import the robust weather module (from workspace root)
    import sys
    sys.path.insert(0, '/root/.openclaw/workspace')
    from weather_robust import get_weather
    weather = get_weather("Eau Claire")
except Exception as e:
    # If the robust module fails somehow, try a simple direct fetch
    try:
        import urllib.request
        weather = urllib.request.urlopen("https://wttr.in/Eau%20Claire?format=%C+%t+%h", timeout=10).read().decode().strip()
    except:
        weather = "unavailable"

# Calendar
date_str = datetime.now().strftime("%Y-%m-%d")
events = []
try:
    result = subprocess.run(["gog", "calendar", "events", "primary", "--from", date_str, "--to", date_str, "--json"], capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        data = json.loads(result.stdout)
        for ev in data.get("events", [])[:10]:
            start = ev.get("start", "")
            time_part = start.split("T")[1][:5] if "T" in start else start[:5]
            events.append(f"- {time_part} {ev.get('summary', '')}")
except:
    pass

# Build message
msg = f"🌅 Good morning! {datetime.now().strftime('%A, %B %d')}\n\nWeather: {weather}\n\nToday's calendar:\n" + ("\n".join(events) if events else "No events") + "\n\nGoals: (coming soon)\n\nFocus on what matters."

# Send
payload = {"chat_id": chat_id, "text": msg}
req = urllib.request.Request(f"https://api.telegram.org/bot{bot_token}/sendMessage", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
try:
    urllib.request.urlopen(req, timeout=10).read()
except:
    pass
