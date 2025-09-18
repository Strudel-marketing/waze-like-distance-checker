Waze Distance API (Unofficial)

Flask API שעוטף את ספריית WazeRouteCalculator כדי לחשב מרחק בקילומטרים לפי Waze, עם fallback ל־OpenRouteService (ORS) במקרה של כשל.

⚠️ חשוב לדעת: זה לא API רשמי של Waze – ייתכן שה־endpoints ישתנו או יישברו בעתיד. מומלץ להשתמש בזה כפתרון פנימי בלבד.

⸻

🚀 התקנה והרצה מקומית

git clone https://github.com/your-user/waze-distance-api.git
cd waze-distance-api
pip install -r requirements.txt
python app.py

ה־API ירוץ כברירת מחדל על http://localhost:8080.

⸻

🐳 Docker

docker build -t waze-distance-api .
docker run -p 8080:8080 waze-distance-api


⸻

🔎 שימוש

דוגמת קריאה עם פרמטרים

http://localhost:8080/waze-distance?lat1=32.0853&lon1=34.7818&lat2=31.7683&lon2=35.2137

תגובה לדוגמה

{
  "distance_km": 61.23,
  "route": "Route 1",
  "source": "waze",
  "alternatives": {
    "Route 1": {
      "distance_km": 61.23,
      "duration_min": 45.7
    },
    "Route 2": {
      "distance_km": 64.5,
      "duration_min": 47.2
    }
  }
}


⸻

📡 דוגמאות שימוש

curl

curl "http://localhost:8080/waze-distance?lat1=32.0853&lon1=34.7818&lat2=31.7683&lon2=35.2137"

JavaScript (fetch)

fetch("http://localhost:8080/waze-distance?lat1=32.0853&lon1=34.7818&lat2=31.7683&lon2=35.2137")
  .then(res => res.json())
  .then(data => console.log("Best distance:", data.distance_km, "km"));

Python (requests)

import requests

url = "http://localhost:8080/waze-distance"
params = {
    "lat1": 32.0853,
    "lon1": 34.7818,
    "lat2": 31.7683,
    "lon2": 35.2137
}
r = requests.get(url, params=params)
print(r.json())

Google Apps Script

function testWazeApi() {
  var url = "http://your-server.com/waze-distance"
    + "?lat1=32.0853&lon1=34.7818&lat2=31.7683&lon2=35.2137";
  var response = UrlFetchApp.fetch(url);
  Logger.log(response.getContentText());
}


⸻

💡 יתרונות
	•	מחזיר את כל המסלולים האפשריים מ־Waze ומחשב את הקצר ביותר.
	•	כולל fallback ל־ORS (במקרה של שגיאות 500/502 או תוצאות ריקות).
	•	ניתן להרחבה לתמיכה במסלולים מרובי תחנות.

⸻

📌 Roadmap / To-Do
	•	תמיכה ב־POST JSON עם מספר יעדים
	•	Docker Compose עם Redis לקאשינג
	•	החזרת זמני נסיעה (לא רק מרחקים)

⸻

📜 רישוי

קוד זה לשימוש חופשי, אך שימוש מסחרי כפוף לתנאי השירות של Waze ו־ORS.
