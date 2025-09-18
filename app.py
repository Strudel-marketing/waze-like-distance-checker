import os
import math
import sqlite3
from flask import Flask, request, jsonify
import requests

# WazeRouteCalculator היציבה מ-PyPI
from WazeRouteCalculator import WazeRouteCalculator, WRCError

# ---------- קונפיג ----------
PORT = int(os.environ.get("PORT", "8080"))
WAZE_REGION = os.environ.get("WAZE_REGION", "IL")  # IL כברירת מחדל
ORS_API_KEY = os.environ.get("ORS_API_KEY")        # לפולבאק
CACHE_DB = os.environ.get("CACHE_DB", "cache.db")
CACHE_TTL_SEC = int(os.environ.get("CACHE_TTL_SEC", "86400"))  # 24h

# ---------- Cache פשוט ב-SQLite ----------
class DistanceCache:
    def __init__(self, path):
        self.path = path
        self._ensure()

    def _ensure(self):
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS distances (
              k TEXT PRIMARY KEY,
              km REAL NOT NULL,
              ts INTEGER NOT NULL
            )
        """)
        con.commit()
        con.close()

    def _key(self, lat1, lon1, lat2, lon2, strategy):
        # עיגול קל כדי לאחד פרמטרים כמעט זהים
        def r(x): return round(float(x), 5)
        return f"{r(lat1)},{r(lon1)}->{r(lat2)},{r(lon2)}|{strategy}"

    def get(self, lat1, lon1, lat2, lon2, strategy):
        k = self._key(lat1, lon1, lat2, lon2, strategy)
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute("SELECT km, ts FROM distances WHERE k=?", (k,))
        row = cur.fetchone()
        con.close()
        if not row:
            return None
        km, ts = row
        if (int(os.time()) - ts) > CACHE_TTL_SEC if hasattr(os, "time") else False:
            return km  # אם אין os.time בסביבה, נתעלם מ-TTL
        return km

    def set(self, lat1, lon1, lat2, lon2, strategy, km):
        import time
        k = self._key(lat1, lon1, lat2, lon2, strategy)
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute("REPLACE INTO distances (k, km, ts) VALUES (?, ?, ?)", (k, float(km), int(time.time())))
        con.commit()
        con.close()

# ---------- Helpers ----------
def haversine_km(lat1, lon1, lat2, lon2):
    # שימושי לבדיקה/השוואה
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlmb/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def call_waze_all_routes(lat1, lon1, lat2, lon2, region=WAZE_REGION):
    """
    מחזיר את כל המסלולים מ-Waze:
    [{"name": <str>, "time_min": <float>, "distance_km": <float>} ...]
    """
    start = (lat1, lon1)
    end = (lat2, lon2)
    wrc = WazeRouteCalculator(start, end, region)
    routes = wrc.calc_all_routes_info()  # dict: name -> (time_min, dist_km) או name -> {"time":..., "distance":...}

    alts = []
    # תמיכה בשתי תצורות הערך
    for name, data in routes.items():
        if isinstance(data, dict):
            t = float(data.get("time"))
            d = float(data.get("distance"))
        elif isinstance(data, (list, tuple)) and len(data) >= 2:
            t = float(data[0])
            d = float(data[1])
        else:
            # לא מוכר – נדלג
            continue
        alts.append({
            "name": name,
            "time_min": round(t, 2),
            "distance_km": round(d, 2)
        })
    if not alts:
        raise ValueError("Waze returned no alternatives")
    return alts

def call_ors_distance_km(lat1, lon1, lat2, lon2):
    """
    פולבאק ל-ORS: מחזיר (distance_km, meta)
    """
    if not ORS_API_KEY:
        raise RuntimeError("ORS_API_KEY not set for fallback")

    url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
    body = {
        "coordinates": [[lon1, lat1], [lon2, lat2]],
        "instructions": False,
        "units": "m",
    }
    headers = {"Authorization": ORS_API_KEY, "Content-Type": "application/json"}
    r = requests.post(url, json=body, headers=headers, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"ORS HTTP {r.status_code}: {r.text[:200]}")

    j = r.json()
    feat = (j.get("features") or [None])[0]
    if not feat:
        raise RuntimeError("ORS: missing features")
    props = feat.get("properties", {})
    summary = props.get("summary", {})
    m = float(summary.get("distance", 0.0))
    if m <= 0:
        raise RuntimeError("ORS: invalid distance")
    return (round(m/1000.0, 2), {"ors_summary": summary})

# ---------- Flask ----------
app = Flask(__name__)
cache = DistanceCache(CACHE_DB)

@app.get("/waze-distance")
def waze_distance():
    try:
        # פרמטרים
        lat1 = float(request.args["lat1"])
        lon1 = float(request.args["lon1"])
        lat2 = float(request.args["lat2"])
        lon2 = float(request.args["lon2"])

        # אסטרטגיית בחירה:
        # - min_distance (ברירת מחדל): המסלול הקצר ביותר בק"מ
        # - fastest: המסלול המהיר ביותר בדקות
        strategy = request.args.get("strategy", "min_distance").lower()
        verbose = request.args.get("verbose", "0") in ("1", "true", "yes")

        # קאש
        ck = cache.get(lat1, lon1, lat2, lon2, strategy)
        if ck is not None and not verbose:
            return jsonify({"distance_km": round(float(ck), 2), "source": "cache"})

        # נסה וויז
        try:
            alts = call_waze_all_routes(lat1, lon1, lat2, lon2, region=WAZE_REGION)
            if strategy == "fastest":
                chosen = min(alts, key=lambda r: r["time_min"])
            else:
                chosen = min(alts, key=lambda r: r["distance_km"])

            cache.set(lat1, lon1, lat2, lon2, strategy, chosen["distance_km"])

            payload = {
                "distance_km": chosen["distance_km"],
                "source": "waze",
                "strategy": strategy
            }
            if verbose:
                payload["alternatives"] = alts
                payload["as_the_crow_flies_km"] = round(haversine_km(lat1, lon1, lat2, lon2), 2)
            return jsonify(payload)

        except (WRCError, Exception) as we:
            # פולבאק ל-ORS אם וויז נופל
            try:
                km, meta = call_ors_distance_km(lat1, lon1, lat2, lon2)
                payload = {
                    "distance_km": km,
                    "source": "ors_fallback",
                    "strategy": strategy,
                    "waze_error": str(we),
                }
                if verbose:
                    payload["ors_meta"] = meta
                    payload["as_the_crow_flies_km"] = round(haversine_km(lat1, lon1, lat2, lon2), 2)
                return jsonify(payload)
            except Exception as oe:
                return jsonify({
                    "error": "waze_and_ors_failed",
                    "waze_error": str(we),
                    "ors_error": str(oe)
                }), 502

    except KeyError as ke:
        return jsonify({"error": f"missing parameter: {ke}"}), 400
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
