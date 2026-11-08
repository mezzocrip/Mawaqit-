from datetime import datetime
import json
import zoneinfo
import requests

# Utilisation de l'API Mawaqit officielle pour la mosquée de Frais Vallon (ID: 10255)
MOSQUE_ID = "10255"
API_URL = f"https://mawaqit.net/api/minifiedPrayerTimes/{MOSQUE_ID}"

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Referer": "https://mawaqit.net/"
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
    
    # L'API minified renvoie directement un tableau des horaires du jour dans 'times'
    times = data.get("times", [])
    jumuah = data.get("jumuah", "12:30")

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

    # Événement Jumu'ah le vendredi
    if datetime.now(tz).weekday() == 4:
        clean_jumuah = jumuah.replace(":", "")
        jumuah_dt = f"{today}T{clean_jumuah}00"
        ics_lines.extend([
            "BEGIN:VEVENT",
            "SUMMARY:Jumu'ah (Prière du Vendredi)",
            f"DTSTART;TZID=Europe/Paris:{jumuah_dt}",
            f"DTEND;TZID=Europe/Paris:{jumuah_dt}",
            "DESCRIPTION:Grande prière du vendredi à la mosquée",
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
