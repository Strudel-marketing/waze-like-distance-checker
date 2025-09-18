from flask import Flask, request, jsonify
from WazeRouteCalculator import WazeRouteCalculator, WRCError

app = Flask(__name__)

@app.route("/waze-distance", methods=["GET"])
def waze_distance():
    try:
        lat1 = request.args.get("lat1")
        lon1 = request.args.get("lon1")
        lat2 = request.args.get("lat2")
        lon2 = request.args.get("lon2")

        if not lat1 or not lon1 or not lat2 or not lon2:
            return jsonify({"error": "Missing coordinates"}), 400

        origin = f"{lat1},{lon1}"
        destination = f"{lat2},{lon2}"

        route = WazeRouteCalculator(origin, destination, "IL")
        routes = route.calc_all_routes_info()  # מחזיר dict: { routeName: (time, distance) }

        # הפיכת הפלט לרשימה ידידותית
        all_routes = []
        for name, (time_minutes, distance_km) in routes.items():
            all_routes.append({
                "route": name,
                "time_minutes": time_minutes,
                "distance_km": distance_km
            })

        # בחירת המסלול הקצר ביותר בק״מ
        shortest = min(all_routes, key=lambda r: r["distance_km"])

        return jsonify({
            "distance_km": shortest["distance_km"],   # 👈 התאמה ל-Apps Script
            "chosen": shortest,                       # 👈 המסלול הקצר ביותר
            "all_routes": all_routes,                 # 👈 כל המסלולים להשוואה
            "source": "waze"
        })

    except WRCError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"שגיאה כללית: {e}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
