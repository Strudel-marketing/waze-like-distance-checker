from flask import Flask, request, jsonify
from WazeRouteCalculator import WazeRouteCalculator, WRCError

app = Flask(__name__)

@app.route("/waze-distance", methods=["GET"])
def waze_distance():
    try:
        lat1 = float(request.args.get("lat1"))
        lon1 = float(request.args.get("lon1"))
        lat2 = float(request.args.get("lat2"))
        lon2 = float(request.args.get("lon2"))

        route = WazeRouteCalculator(lat1, lon1, lat2, lon2, region="IL")
        routes = route.calc_all_routes_info()  # מחזיר dict של כל המסלולים

        # בוחרים את הקצר ביותר בק"מ
        shortest = min(routes.items(), key=lambda r: r[1][1])  # (שם מסלול, (דקות, ק"מ))
        route_name, (time_minutes, distance_km) = shortest

        return jsonify({
            "route": route_name,
            "time_minutes": time_minutes,
            "distance_km": distance_km,
            "source": "waze"
        })

    except WRCError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"בעיה בפרמטרים: {e}"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
