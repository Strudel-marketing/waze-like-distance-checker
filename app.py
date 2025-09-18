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
        
                all_routes = []
                for route in results:
                    print(f"Route: {route.name}, Distance: {route.distance:.2f} km, Time: {route.time:.1f} min")
                    all_routes.append({
                        "name": route.name,
                        "distance_km": round(route.distance, 2),
                        "time_min": round(route.time, 1)
                    })

        # בוחר את המסלול הקצר ביותר
        best_route = min(results, key=lambda r: r.distance)

        return round(best_route.distance, 2), all_routes

        km, all_routes = asyncio.run(get_distance())
        cache.set(lat1, lon1, lat2, lon2, km)
        
        return jsonify({
            "distance_km": km,
            "source": "waze",
            "routes": all_routes
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
