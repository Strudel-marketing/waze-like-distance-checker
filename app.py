from flask import Flask, request, jsonify
from WazeRouteCalculator import WazeRouteCalculator, WRCError

app = Flask(__name__)

@app.get("/waze-distance")
def waze_distance():
    try:
        lat1 = float(request.args["lat1"])
        lon1 = float(request.args["lon1"])
        lat2 = float(request.args["lat2"])
        lon2 = float(request.args["lon2"])

        # יצירת אובייקט וייז
        calculator = WazeRouteCalculator(
            (lat1, lon1),
            (lat2, lon2),
            region="IL"
        )

        # החזרת כל המסלולים האפשריים
        routes = calculator.calc_all_routes_info(real_time=True)

        # בחירת המסלול הקצר ביותר
        best_distance = None
        best_name = None
        for name, info in routes.items():
            dist_km, duration_min = info
            if best_distance is None or dist_km < best_distance:
                best_distance = dist_km
                best_name = name

        if best_distance is None:
            raise ValueError("No valid route found")

        return jsonify({
            "distance_km": round(best_distance, 2),
            "route": best_name,
            "source": "waze",
            "alternatives": {
                name: {"distance_km": round(info[0], 2), "duration_min": round(info[1], 1)}
                for name, info in routes.items()
            }
        })

    except WRCError as we:
        return jsonify({"error": f"Waze error: {str(we)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
