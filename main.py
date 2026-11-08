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

def generate_ics(data):
    tz = zoneinfo.ZoneInfo("Europe/Paris")
    now = datetime.now(tz)
    
    prayers = [
        ("Fajr", 0),
        ("Dhuhr", 1),
        ("Asr", 2),
        ("Maghrib", 3),
        ("Isha", 4)
    ]
    
    calendar_days = data.get("calendar", [])
    jumuah_time = data.get("jumuah", "12:30")

    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Mawaqit Frais Vallon Generator//FR",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Mosquée Frais Vallon - Prières",
        "X-WR-TIMEZONE:Europe/Paris"
    ]

    # Génération sur les 30 prochains jours
    for i in range(30):
        current_date = now + timedelta(days=i)
        date_str = current_date.strftime("%Y%m%d")
        
        # Index du jour dans l'année (0-365) pour récupérer les lignes du calendrier Mawaqit
        day_of_year = current_date.timetuple().tm_yday - 1
        
        if day_of_year < len(calendar_days):
            day_data = calendar_days[day_of_year]
            times = day_data if isinstance(day_data, list) else day_data.get("times", [])
            
            # 5 Prières quotidiennes
            if len(times) >= 5:
                for name, idx in prayers:
                    time_str = times[idx]
                    clean_time = time_str.replace(":", "")
                    dt_start = f"{date_str}T{clean_time}00"
                    
                    ics_lines.extend([
                        "BEGIN:VEVENT",
                        f"SUMMARY:Adhan {name}",
                        f"DTSTART;TZID=Europe/Paris:{dt_start}",
                        f"DTEND;TZID=Europe/Paris:{dt_start}",
                        f"DESCRIPTION:Prière de {name} - Mosquée de Frais Vallon",
                        "LOCATION:Mosquée de Frais Vallon, 13013 Marseille",
                        "END:VEVENT"
                    ])

            # Midnight et Last Third (souvent stockés aux index spécifiques ou dans les métadonnées journalières)
            # Si présents dans le tableau ou l'objet du jour :
            if isinstance(day_data, dict):
                midnight = day_data.get("midnight")
                last_third = day_data.get("lastThird")
                
                if midnight:
                    m_time = midnight.replace(":", "")
                    ics_lines.extend([
                        "BEGIN:VEVENT",
                        "SUMMARY:Midnight",
                        f"DTSTART;TZID=Europe/Paris:{date_str}T{m_time}00",
                        f"DTEND;TZID=Europe/Paris:{date_str}T{m_time}00",
                        "DESCRIPTION:Milieu de la nuit",
                        "LOCATION:Mosquée de Frais Vallon, 13013 Marseille",
                        "END:VEVENT"
                    ])
                    
                if last_third:
                    lt_time = last_third.replace(":", "")
                    ics_lines.extend([
                        "BEGIN:VEVENT",
                        "SUMMARY:Last Third",
                        f"DTSTART;TZID=Europe/Paris:{date_str}T{lt_time}00",
                        f"DTEND;TZID=Europe/Paris:{date_str}T{lt_time}00",
                        "DESCRIPTION:Dernier tiers de la nuit",
                        "LOCATION:Mosquée de Frais Vallon, 13013 Marseille",
                        "END:VEVENT"
                    ])

        # Prière du Vendredi (Jumu'ah)
        if current_date.weekday() == 4: # 4 = Vendredi
            clean_jumuah = jumuah_time.replace(":", "")
            jumuah_dt = f"{date_str}T{clean_jumuah}00"
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
        print("Fichier calendar.ics généré avec succès pour 30 jours !")
    except Exception as e:
        print(f"Erreur lors de la génération : {e}")
        exit(1)
