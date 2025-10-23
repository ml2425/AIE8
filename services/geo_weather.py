# services/geo_weather.py
import requests
from typing import Tuple, Dict, Any

# Be polite to Nominatim (they require a UA); keep timeouts short for agents
UA = {"User-Agent": "mcp-demo/0.1 (contact: you@example.com)"}
TO = 12  # seconds

def geo_lookup(place: str) -> Tuple[float, float, str]:
    """Geocode a place name to (lat, lon, display_name) using Nominatim."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": place, "format": "json", "limit": 1}
    r = requests.get(url, params=params, headers=UA, timeout=TO)
    r.raise_for_status()
    data = r.json()
    if not data:
        raise ValueError(f"No results for place: {place}")
    lat = float(data[0]["lat"]); lon = float(data[0]["lon"])
    label = data[0].get("display_name", place)
    return lat, lon, label

def get_weather(lat: float, lon: float) -> Dict[str, Any]:
    """Fetch current weather from Open-Meteo."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": lat, "longitude": lon, "current_weather": True}
    r = requests.get(url, params=params, timeout=TO)
    r.raise_for_status()
    return r.json()

def summarize_weather(payload: Dict[str, Any]) -> str:
    cw = payload.get("current_weather") or {}
    t = cw.get("temperature"); w = cw.get("windspeed"); d = cw.get("winddirection")
    code = cw.get("weathercode")
    return (
        f"Current weather: {t}°C, wind {w} m/s (dir {d}°), code {code}. "
        "Source: Open-Meteo."
    )
