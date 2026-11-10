from datetime import datetime
import os

def process_ics_subscription(input_path, output_path):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Le fichier source '{input_path}' est introuvable. Veuillez le placer dans le même dossier.")

    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    lines = content.splitlines()
    new_lines = []
    
    # Personnalisation des métadonnées pour l'abonnement
    for line in lines:
        if line.startswith("X-WR-CALNAME:"):
            line = "X-WR-CALNAME:Mon Abonnement Calendrier Personnalisé"
        elif line.startswith("PRODID:"):
            line = "PRODID:-//Mon Convertisseur ICS Personnel//FR"
        
        new_lines.append(line)

    # Écriture du fichier final de sortie pour l'abonnement
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\r\n".join(new_lines))

    print(f"Le fichier d'abonnement '{output_path}' a été généré avec succès à partir de '{input_path}'.")

if __name__ == "__main__":
    # Nom du fichier .ics que tu fournis
    FICHIER_SOURCE = "input.ics"
    # Nom du fichier généré pour l'abonnement
    FICHIER_SORTIE = "calendar.ics"
    
    try:
        process_ics_subscription(FICHIER_SOURCE, FICHIER_SORTIE)
    except Exception as e:
        print(f"Erreur lors du traitement du fichier : {e}")
        exit(1)
