#!/usr/bin/env python3
"""
Robust weather fetcher with fallbacks and caching.
Primary: wttr.in
Secondary: Open-Meteo API
Fallback: cached previous weather
"""

import json
import os
import subprocess
import urllib.request
from datetime import datetime, timedelta

CACHE_FILE = '/root/.openclaw/workspace/cache/weather.json'

def load_cache():
    """Load cached weather data."""
    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"date": None, "weather": None, "location": "Eau Claire"}

def save_cache(weather, location="Eau Claire"):
    """Save weather data to cache."""
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, 'w') as f:
            json.dump({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "weather": weather,
                "location": location,
                "updated": datetime.now().isoformat()
            }, f)
    except:
        pass

def fetch_wttr(location="Eau%20Claire"):
    """Fetch weather from wttr.in."""
    try:
        url = f"https://wttr.in/{location}?format=%C+%t+%h"
        weather = urllib.request.urlopen(url, timeout=10).read().decode().strip()
        if weather and "unavailable" not in weather.lower():
            return weather
    except:
        pass
    return None

def fetch_openmeteo(location="Eau Claire"):
    """
    Fetch weather from Open-Meteo (free, no API key).
    Note: This requires geocoding the location first.
    For simplicity, using hardcoded coordinates for Eau Claire, WI.
    """
    try:
        # Eau Claire, WI coordinates: 44.8113, -91.4985
        url = "https://api.open-meteo.com/v1/forecast?latitude=44.8113&longitude=-91.4985&current_weather=true&hourly=relativehumidity_2m"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            cw = data.get("current_weather", {})
            temp = cw.get("temperature")
            code = cw.get("weathercode")
            wind = cw.get("windspeed")

            # Map weather code to simple description
            weather_codes = {
                0: "Clear", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle",
                53: "Moderate drizzle", 55: "Dense drizzle", 56: "Light freezing drizzle",
                57: "Dense freezing drizzle", 61: "Slight rain", 63: "Moderate rain",
                65: "Heavy rain", 66: "Light freezing rain", 67: "Heavy freezing rain",
                71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
                77: "Snow grains", 80: "Slight rain showers", 81: "Moderate rain showers",
                82: "Violent rain showers", 85: "Slight snow showers", 86: "Heavy snow showers",
                95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
            }
            condition = weather_codes.get(code, f"Code {code}")

            # Get humidity from last hourly reading
            humidity = None
            hourly = data.get("hourly", {})
            if "relativehumidity_2m" in hourly and hourly["relativehumidity_2m"]:
                humidity = hourly["relativehumidity_2m"][-1]

            parts = [f"{condition}", f"{temp}°C"]
            if humidity:
                parts.append(f"{humidity}% humidity")
            if wind:
                parts.append(f"{wind} km/h wind")
            return ", ".join(parts)
    except:
        pass
    return None

def get_weather(location="Eau Claire"):
    """
    Get weather with multiple fallbacks.
    Returns: weather string or None if all methods fail.
    """
    # Try wttr.in first
    weather = fetch_wttr(location.replace(" ", "%20"))
    if weather:
        save_cache(weather, location)
        return weather

    # Try Open-Meteo
    weather = fetch_openmeteo(location)
    if weather:
        save_cache(weather, location)
        return weather

    # Use cache if available and from today
    cache = load_cache()
    if cache.get("date") == datetime.now().strftime("%Y-%m-%d") and cache.get("weather"):
        return f"{cache['weather']} (cached)"

    # Use yesterday's cache as absolute fallback
    if cache.get("weather"):
        return f"{cache['weather']} (fallback)"

    return "unavailable"

if __name__ == "__main__":
    import sys
    location = sys.argv[1] if len(sys.argv) > 1 else "Eau Claire"
    print(get_weather(location))
