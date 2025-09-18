import sqlite3
import time

class DistanceCache:
    def __init__(self, db_file="cache.db", ttl=86400):
        self.db_file = db_file
        self.ttl = ttl
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS distances (
                origin TEXT,
                destination TEXT,
                distance REAL,
                timestamp INTEGER
            )
        """)
        conn.commit()
        conn.close()

    def _key(self, lat1, lon1, lat2, lon2):
        return f"{round(lat1,4)},{round(lon1,4)}:{round(lat2,4)},{round(lon2,4)}"

    def get(self, lat1, lon1, lat2, lon2):
        key = self._key(lat1, lon1, lat2, lon2)
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT distance, timestamp FROM distances WHERE origin=?", (key,))
        row = c.fetchone()
        conn.close()
        if row:
            dist, ts = row
            if time.time() - ts < self.ttl:
                return dist
        return None

    def set(self, lat1, lon1, lat2, lon2, distance):
        key = self._key(lat1, lon1, lat2, lon2)
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("REPLACE INTO distances(origin, destination, distance, timestamp) VALUES (?, ?, ?, ?)",
                  (key, key, distance, int(time.time())))
        conn.commit()
        conn.close()
