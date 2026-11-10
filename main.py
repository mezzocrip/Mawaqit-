from datetime import datetime, timedelta
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
    
    match = re.search(r'var\s+confData\s*=\s*(\{.*?\});', res.text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
        
    match_alt = re.search(r'window\.frontApp\s*=\s*(\{.*?\});', res.text, res.DOTALL)
    if match_alt:
        return json.loads(match_alt.group(1))
        
    raise ValueError("Impossible de trouver les données de la mosquée dans la page.")

def generate_jumuah_ics(data):
    tz = zoneinfo.ZoneInfo("Europe/Paris")
    now = datetime.now(tz)
    
    calendar_days = data.get("calendar", [])
    jumuah_time = data.get("jumuah")
    if not jumuah_time and "mosque" in data:
        jumuah_time = data["mosque"].get("jumuah")

    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Mawaqit Frais Vallon Jumuah Generator//FR",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Jumu'ah - Mosquée Frais Vallon",
        "X-WR-TIMEZONE:Europe/Paris"
    ]

    for i in range(180):
        current_date = now + timedelta(days=i)
        if current_date.year != now.year:
            break

        if current_date.weekday() == 4: # Vendredi
            date_str = current_date.strftime("%Y%m%d")
            day_idx = current_date.timetuple().tm_yday - 1
            
            if day_idx < len(calendar_days):
                day_data = calendar_days[day_idx]
                times = day_data if isinstance(day_data, list) else day_data.get("times", [])
                
                j_time = jumuah_time if jumuah_time else (times[1] if len(times) > 1 else "13:00")
                clean_jumuah = j_time.replace(":", "")
                jumuah_dt = f"{date_str}T{clean_jumuah}00"
                
                ics_lines.extend([
                    "BEGIN:VEVENT",
                    "SUMMARY:Jumu'ah",
                    f"DTSTART;TZID=Europe/Paris:{jumuah_dt}",
                    f"DTEND;TZID=Europe/Paris:{jumuah_dt}",
                    "DESCRIPTION:Grande prière du vendredi - Mosquée de Frais Vallon",
                    "LOCATION:Mosquée de Frais Vallon, 13013 Marseille",
                    "END:VEVENT"
                ])

    ics_lines.append("END:VCALENDAR")
    return "\r\n".join(ics_lines)

if __name__ == "__main__":
    conf_data = fetch_mawaqit_data()
    ics_content = generate_jumuah_ics(conf_data)
    with open("jumuah.ics", "w", encoding="utf-8") as f:
        f.write(ics_content)
    print("Fichier jumuah.ics généré avec succès !")
