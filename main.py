from datetime import datetime
import json
import zoneinfo
import requests

MOSQUE_ID = "10255"
API_URL = f"https://mawaqit.net/api/2/mosque/{MOSQUE_ID}"

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Accept": "application/json",
    "Origin": "https://mawaqit.net",
    "Referer": f"https://mawaqit.net/fr/mosquee-de-frais-vallon-marseille-13013-france-1"
}

def fetch_mawaqit_data():
    res = requests.get(API_URL, headers=headers, timeout=15)
    res.raise_for_status()
    return res.json()

def generate_ics(data):
    tz = zoneinfo.ZoneInfo("Europe/Paris")
    today = datetime.now(tz).strftime("%Y%m%d")
    
    prayers = [
        ("Fajr", 0),
        ("Dhuhr", 1),
        ("Asr", 2),
        ("Maghrib", 3),
        ("Isha", 4)
    ]
    
    # Récupération des horaires depuis la structure de l'API officielle
    times = data.get("calendar", [[]])[0] if "calendar" in data else data.get("times", [])
    if not times:
        # Fallback sur une autre structure potentielle de l'API v2
        times = data.get("times", ["06:00", "13:30", "16:45", "18:30", "20:00"])

    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Mawaqit Frais Vallon Generator//FR",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Mosquée Frais Vallon - Prières",
        "X-WR-TIMEZONE:Europe/Paris"
    ]

    if len(times) >= 5:
        for name, idx in prayers:
            time_str = times[idx]
            clean_time = time_str.replace(":", "")
            dt_start = f"{today}T{clean_time}00"
            
            ics_lines.extend([
                "BEGIN:VEVENT",
                f"SUMMARY:Adhan {name}",
                f"DTSTART;TZID=Europe/Paris:{dt_start}",
                f"DTEND;TZID=Europe/Paris:{dt_start}",
                f"DESCRIPTION:Prière de {name} - Mosquée de Frais Vallon",
                "LOCATION:Mosquée de Frais Vallon, 13013 Marseille",
                "END:VEVENT"
            ])

    ics_lines.append("END:VCALENDAR")
    return "\r\n".join(ics_lines)

if __name__ == "__main__":
    try:
        conf_data = fetch_mawaqit_data()
        ics_content = generate_ics(conf_data)
        with open("calendar.ics", "w", encoding="utf-8") as f:
            f.write(ics_content)
        print("Fichier calendar.ics généré avec succès !")
    except Exception as e:
        print(f"Erreur lors de la génération : {e}")
        exit(1)
