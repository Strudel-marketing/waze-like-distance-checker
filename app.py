from flask import Flask, request, jsonify
from pywaze.route_calculator import WazeRouteCalculator  # ✅ במקום WazeClient
from cache import DistanceCache
import asyncio

app = Flask(__name__)
cache = DistanceCache("cache.db")

@app.get("/waze-distance")
def waze_distance():
    try:
        lat1 = float(request.args["lat1"])
        lon1 = float(request.args["lon1"])
        lat2 = float(request.args["lat2"])
        lon2 = float(request.args["lon2"])

        # בדוק אם יש בקאש
        cached = cache.get(lat1, lon1, lat2, lon2)
        if cached:
            return jsonify({"distance_km": cached, "source": "cache"})

        async def get_distance():
            async with WazeRouteCalculator("IL") as client:
                start = f"{lat1},{lon1}"
                end = f"{lat2},{lon2}"
                results = await client.calc_routes(start, end)
                # results = [("Route 1", (time_minutes, distance_km)), ...]
                route_time, route_dist = results[0][1]
                return route_dist

        km = asyncio.run(get_distance())
        cache.set(lat1, lon1, lat2, lon2, km)

        return jsonify({"distance_km": round(km, 2), "source": "waze"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
