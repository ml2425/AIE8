from fastmcp import Client

async def main():
    # Connect via stdio to a local script
    async with Client("server.py") as client:
        tools = await client.list_tools()
        print(f"Available tools: {tools}")
        
        result = await client.call_tool("web_search", {"query": "What is the capital of France?"})
        print(f"Result: {result}")

        # 1) Single-call happy path (recommended)
        wx = await client.call_tool("weather_by_place", {"place": "Singapore"})
        print("Weather by place:", wx.get("summary"), "| coords:", wx.get("latitude"), wx.get("longitude"))

        # 2) Two-step (explicit)
        geo = await client.call_tool("geo_lookup", {"place": "Lisbon"})
        wx2 = await client.call_tool("get_weather", {"lat": geo["lat"], "lon": geo["lon"], "summarize": True})
        print("Lisbon:", wx2.get("summary"))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())