from flask import Flask, request, jsonify
from WazeRouteCalculator import WazeRouteCalculator, WRCError
import requests

app = Flask(__name__)

# ORS settings
ORS_URL = "https://api.openrouteservice.org/v2/directions/driving-car"
ORS_API_KEY = "<ORS_API_KEY>"  # תכניס כאן את המפתח שלך


def try_waze(lat1, lon1, lat2, lon2, region=None):
    """
    מנסה להביא תוצאות מ-WazeRouteCalculator
    מחזיר dict אם הצליח, אחרת זורק Exception
    """
    calculator = WazeRouteCalculator(
        (lat1, lon1),
        (lat2, lon2),
        region=region
    )
    routes = calculator.calc_all_routes_info(real_time=True)

    if not routes:
        raise ValueError("No routes returned from Waze")

    best_distance = None
    best_name = None
    for name, info in routes.items():
        dist_km, duration_min = info
        if best_distance is None or dist_km < best_distance:
            best_distance = dist_km
            best_name = name

    return {
        "distance_km": round(best_distance, 2),
        "route": best_name,
        "source": f"waze{'' if not region else '_' + region}",
        "alternatives": {
            name: {
                "distance_km": round(info[0], 2),
                "duration_min": round(info[1], 1)
            }
            for name, info in routes.items()
        }
    }


def ors_fallback(lat1, lon1, lat2, lon2):
    """
    קריאה ל-ORS במקרה ש-Waze נכשל
    """
    body = {
        "coordinates": [[lon1, lat1], [lon2, lat2]],
        "units": "km"
    }
    headers = {"Authorization": ORS_API_KEY}
    res = requests.post(ORS_URL, json=body, headers=headers)

    if res.status_code != 200:
        raise ValueError(f"ORS error: HTTP {res.status_code}")

    data = res.json()
    km = data["features"][0]["properties"]["summary"]["distance"]
    return {
        "distance_km": round(km, 2),
        "source": "ors_fallback"
    }


@app.get("/waze-distance")
def waze_distance():
    try:
        lat1 = float(request.args["lat1"])
        lon1 = float(request.args["lon1"])
        lat2 = float(request.args["lat2"])
        lon2 = float(request.args["lon2"])

        # ניסיונות לפי סדר
        for region in ["IL", "israel", None]:
            try:
                result = try_waze(lat1, lon1, lat2, lon2, region)
                return jsonify(result)
            except Exception as e:
                print(f"Waze failed with region={region}: {e}")

        # אם הכול נכשל → ORS
        return jsonify(ors_fallback(lat1, lon1, lat2, lon2))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
