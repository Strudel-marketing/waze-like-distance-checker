from flask import Flask, request, jsonify
from wazeroutecalculator import WazeRouteCalculator
import requests
import os

app = Flask(__name__)

ORS_API_KEY = os.environ.get("ORS_API_KEY", "")

def get_waze_distance(lat1, lon1, lat2, lon2):
    servers = ["www.waze.com", "il.waze.com", "row.waze.com"]
    last_error = None
    debug = []

    for server in servers:
        try:
            debug.append(f"Trying Waze server: {server}")
            route_calc = WazeRouteCalculator(lat1, lon1, lat2, lon2, region="IL", server=server)
            routes = route_calc.calc_all_routes_info()
            distances = [info[0] for info in routes.values()]
            km = min(distances) / 1000.0
            debug.append(f"Waze success from {server}: {km} km")
            return round(km, 2), server, debug
        except Exception as e:
            last_error = str(e)
            debug.append(f"Waze failed on {server}: {e}")
            continue

    raise Exception(f"Waze failed on all servers: {last_error}\n{debug}")

def get_ors_distance(lat1, lon1, lat2, lon2):
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    body = {
        "coordinates": [[lon1, lat1], [lon2, lat2]],
        "units": "km"
    }
    headers = {"Authorization": ORS_API_KEY}
    res = requests.post(url, json=body, headers=headers)

    if res.status_code == 200:
        data = res.json()
        km = data["features"][0]["properties"]["summary"]["distance"]
        return round(km, 2)
    else:
        raise Exception(f"ORS failed: HTTP {res.status_code}, {res.text}")

@app.get("/waze-distance")
def waze_distance():
    try:
        lat1 = float(request.args["lat1"])
        lon1 = float(request.args["lon1"])
        lat2 = float(request.args["lat2"])
        lon2 = float(request.args["lon2"])

        debug_log = []

        try:
            km, server, debug = get_waze_distance(lat1, lon1, lat2, lon2)
            debug_log.extend(debug)
            return jsonify({
                "distance_km": km,
                "source": f"waze:{server}",
                "debug_log": debug_log
            })
        except Exception as e:
            debug_log.append(f"Waze failed: {e}")
            # fallback ל־ORS
            if ORS_API_KEY:
                try:
                    km = get_ors_distance(lat1, lon1, lat2, lon2)
                    debug_log.append(f"ORS success: {km} km")
                    return jsonify({
                        "distance_km": km,
                        "source": "ors",
                        "debug_log": debug_log
                    })
                except Exception as ors_e:
                    debug_log.append(f"ORS failed: {ors_e}")
            return jsonify({"error": str(e), "debug_log": debug_log}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
