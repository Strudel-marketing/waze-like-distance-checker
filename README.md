# Waze Distance API (Unofficial)

Flask API שעוטף את ספריית [pywaze](https://pypi.org/project/pywaze/) כדי לחשב **מרחק בקילומטרים** לפי Waze.

⚠️ **חשוב לדעת**: זה **לא API רשמי של Waze** – ייתכן שה־endpoints ישתנו או יישברו בעתיד. מומלץ להשתמש בזה כפתרון פנימי בלבד.

---

## 🚀 התקנה והרצה מקומית

```bash
git clone https://github.com/your-user/waze-distance-api.git
cd waze-distance-api
pip install -r requirements.txt
python app.py
```

ה־API ירוץ כברירת מחדל על `http://localhost:8080`.

---

## 🐳 Docker

```bash
docker build -t waze-distance-api .
docker run -p 8080:8080 waze-distance-api
```

---

## 🔎 שימוש

### דוגמת קריאה עם פרמטרים

```
http://localhost:8080/waze-distance?lat1=32.0853&lon1=34.7818&lat2=31.7683&lon2=35.2137
```

### תגובה לדוגמה
```json
{
  "distance_km": 61.23,
  "source": "waze"
}
```

---

## 📡 דוגמאות שימוש

### curl
```bash
curl "http://localhost:8080/waze-distance?lat1=32.0853&lon1=34.7818&lat2=31.7683&lon2=35.2137"
```

### JavaScript (fetch)
```javascript
fetch("http://localhost:8080/waze-distance?lat1=32.0853&lon1=34.7818&lat2=31.7683&lon2=35.2137")
  .then(res => res.json())
  .then(data => console.log("Distance:", data.distance_km, "km"));
```

### Python (requests)
```python
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
```

### Google Apps Script
```javascript
function testWazeApi() {
  var url = "http://your-server.com/waze-distance"
    + "?lat1=32.0853&lon1=34.7818&lat2=31.7683&lon2=35.2137";
  var response = UrlFetchApp.fetch(url);
  Logger.log(response.getContentText());
}
```

---

## 💾 קאשינג

ה־API משתמש ב־SQLite לשמירת תוצאות חישוב (ברירת מחדל: 24 שעות).  
כך נמנעים מקריאות כפולות ל־Waze עבור אותן נקודות.

---

## 📌 Roadmap / To-Do
- [ ] הוספת fallback ל־ORS או Google אם וייז נופל  
- [ ] תמיכה ב־POST JSON עם מספר יעדים  
- [ ] Docker Compose עם Redis לקאשינג במקום SQLite  

---

## 📜 רישוי
קוד זה לשימוש חופשי, אך שימוש מסחרי כפוף לתנאי השירות של Waze/Google.  
