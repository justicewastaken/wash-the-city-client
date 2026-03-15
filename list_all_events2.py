#!/usr/bin/env python3
import json, os, subprocess
from datetime import datetime

os.environ["GOG_KEYRING_PASSWORD"] = "opensesame"

calendars = [
    "primary",
    "justiceforanything@gmail.com",
    "f3812ad8499399d129019e2824e3079acc0f5cf63cd4f884c95c38d007023a1d@group.calendar.google.com",
    "67f1fbdabbfb8559f5d466cfe7d5a278b84c2a710ce2f26a52a9297fbbe1f404@group.calendar.google.com",
    "en.usa#holiday@group.v.calendar.google.com",
    "a6j8dedtp8h0q7v6lcmcpb01jjti5bii@import.calendar.google.com"
]

date_str = datetime.now().strftime("%Y-%m-%d")
all_events = []

for cal in calendars:
    try:
        result = subprocess.run(
            ["gog", "calendar", "events", cal, "--from", date_str, "--to", date_str, "--json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            for ev in data.get("events", []):
                start = ev.get("start", "")
                if "T" in start:
                    time_part = start.split("T")[1][:5]
                else:
                    time_part = start[:5]
                summary = ev.get("summary", "")
                all_events.append((time_part, summary, cal))
    except Exception as e:
        pass

all_events.sort(key=lambda x: x[0])

print(f"All events for {date_str} (from {len(calendars)} calendars):")
for time, summary, cal in all_events:
    print(f"{time} — {summary}")
