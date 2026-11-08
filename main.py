from datetime import datetime
import json
import re
import zoneinfo
import requests

SLUG = "mosquee-de-frais-vallon-marseille-13013-france-1"
URL = f"https://mawaqit.net/fr/{SLUG}"

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def fetch_mawaqit_data():
    res = requests.get(URL, headers=headers, timeout=15)
    res.raise_for_status()
    
    # Recherche de la configuration embarquée dans le code HTML de la page
    match = re.search(r'var\s+confData\s*=\s*(\{.*?\});', res.text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    
    # Second pattern de secours si le nom de variable change
    match_alt = re.search(r'window\.frontApp\s*=\s*(\{.*?\});', res.text, re.DOTALL)
    if match_alt:
        return json.loads(match_alt.group(1))
        
    raise ValueError("Impossible de trouver les données de la mosquée dans la page.")

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
    
    # Extraction des horaires du jour
    times = data.get("times", [])
    if not times and "mosque" in data:
        times = data["mosque"].get("times", [])

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
