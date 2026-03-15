#!/bin/bash
export GOG_KEYRING_PASSWORD="opensesame"
export TZ=America/Chicago

# Weather for Eau Claire, WI
WEATHER=$(curl -s "https://wttr.in/Eau%20Claire?format=%C+%t+%h")
if [ -z "$WEATHER" ]; then
  WEATHER="Weather unavailable"
fi

# Today's calendar events (all day)
DATE=$(date +%Y-%m-%d)
EVENTS_JSON=$(gog calendar events primary --from "$DATE" --to "$DATE" --json 2>/dev/null)
if [ -z "$EVENTS_JSON" ] || echo "$EVENTS_JSON" | grep -q '"events":\[\]'; then
  EVENTS_TEXT="No events scheduled for today."
else
  EVENTS_TEXT=$(echo "$EVENTS_JSON" | jq -r '.events[] | "- \(.start | split("T")[1] | split(":")[0..1] | join(":")) \(.summary)"' | head -20)
fi

MESSAGE="🌅 Good morning! Here's your briefing for $(date +'%A, %B %d'):\n\n"
MESSAGE+="Weather: $WEATHER\n\n"
MESSAGE+="Today's calendar:\n$EVENTS_TEXT\n\n"
MESSAGE+="Goals for the day: (we'll add these soon)\n\n"
MESSAGE+="🛠️ Focus on what matters."

# Send to Telegram via OpenClaw Gateway
TOKEN="643b1559039fffcfd8cfd7509e2384149ccd3670afc4b9b8"
CHAT_ID="5606165796"
curl -s -X POST "http://localhost:18789/message/send" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"channel\":\"telegram\",\"to\":\"$CHAT_ID\",\"message\":\"$MESSAGE\"}" >/dev/null 2>&1
