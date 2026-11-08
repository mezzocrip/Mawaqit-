import json
import re
from datetime import datetime
import zoneinfo
import requests

# Information mosquée Frais Vallon (Marseille 13013)
SLUG = "mosquee-de-frais-vallon-marseille-13013-france-1"
URL = f"https://mawaqit.net/fr/{SLUG}"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_mawaqit_data():
    res = requests.get(URL, headers=headers, timeout=15)
    res.raise_for_status()
    
    # Extraction de la variable Javascript confData présente sur la page
    match = re.search(r'var\s+confData\s*=\s*(\{.*?\});', res.text, re.DOTALL)
    if not match:
        raise ValueError("Impossible de trouver confData sur la page Mawaqit.")
    
    return json.loads(match.group(1))

def generate_ics(data):
    tz = zoneinfo.ZoneInfo("Europe/Paris")
    today = datetime.now(tz).strftime("%Y%m%d")
    
    # Mapping des noms de prières
    prayers = [
        ("Fajr", 0),
        ("Dhuhr", 1),
        ("Asr", 2),
        ("Maghrib", 3),
        ("Isha", 4)
    ]
    
    times = data.get("times", [])
    iqama_times = data.get("iqamaCalendar", {})
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

    # Génération des 5 prières du jour
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

    # Événement Jumu'ah (Vendredi)
    if datetime.now(tz).weekday() == 4: # 4 = Vendredi
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
