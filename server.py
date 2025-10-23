from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
import os
from dice_roller import DiceRoller

load_dotenv()

mcp = FastMCP("mcp-server")
client = TavilyClient(os.getenv("TAVILY_API_KEY"))

@mcp.tool()
def web_search(query: str) -> str:
    """Search the web for information about the given query"""
    search_results = client.get_search_context(query=query)
    return search_results

@mcp.tool()
def roll_dice(notation: str, num_rolls: int = 1) -> str:
    """Roll the dice with the given notation"""
    roller = DiceRoller(notation, num_rolls)
    return str(roller)

"""
Add your own tool here, and then use it through Cursor!
"""
# --- begin replacement for lines 24–30 ---
# Tools: geo_lookup, get_weather, weather_by_place
# Keep imports local to this block to avoid changing the top of the file.
from services.geo_weather import (
    geo_lookup as svc_geo_lookup,
    get_weather as svc_get_weather,
    summarize_weather,
)

@mcp.tool()
def geo_lookup(place: str) -> dict:
    """Geocode a place name to (lat, lon, label) using Nominatim (no API key)."""
    lat, lon, label = svc_geo_lookup(place)
    return {"lat": lat, "lon": lon, "label": label}

@mcp.tool()
def get_weather(lat: float, lon: float, summarize: bool = True) -> dict:
    """
    Fetch current weather from Open-Meteo for given coordinates.
    If summarize=True, also include a short human-readable summary.
    """
    payload = svc_get_weather(lat, lon)
    if summarize:
        payload["summary"] = summarize_weather(payload)
    return payload

@mcp.tool()
def weather_by_place(place: str) -> dict:
    """
    Convenience: place -> geocode -> weather -> summary.
    Ideal for natural-language calls from clients.
    """
    lat, lon, label = svc_geo_lookup(place)
    payload = svc_get_weather(lat, lon)
    payload["place"] = label
    payload["summary"] = summarize_weather(payload)
    return payload
# --- end replacement ---


if __name__ == "__main__":
    mcp.run(transport="stdio")