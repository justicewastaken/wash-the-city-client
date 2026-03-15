#!/usr/bin/env python3
import sys
sys.path.insert(0, '/root/.openclaw/workspace')
from weather_robust import get_weather, fetch_wttr, fetch_openmeteo, load_cache, save_cache

print("=== Testing Weather Robustness ===\n")

# Test 1: Normal fetch
print("1. Normal fetch (should work):")
print(f"   Result: {get_weather('Eau Claire')}\n")

# Test 2: Cache loading
print("2. Cache contents:")
cache = load_cache()
print(f"   {cache}\n")

# Test 3: Simulate wttr failure by testing with invalid location
print("3. wttr with invalid location (should fallback):")
result = get_weather('zzzz_invalid_zzzz')
print(f"   Result: {result}\n")

print("All tests completed!")
