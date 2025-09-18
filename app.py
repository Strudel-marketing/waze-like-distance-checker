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
        route_time, route_distance = route.calc_route_info()

        return jsonify({
            "time_minutes": route_time,
            "distance_km": route_distance
        })

    except WRCError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"בעיה בפרמטרים: {e}"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
