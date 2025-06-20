import json
from datetime import datetime
import os

def load_users(filepath):
    """
    Charge les utilisateurs depuis un fichier JSON.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        users = json.load(f)
    required_fields = {'login', 'id', 'created_at', 'avatar_url', 'bio'}
    for u in users:
        if not required_fields.issubset(u.keys()):
            raise ValueError(f"Utilisateur manquant des champs requis: {u}")
    return users


def remove_duplicates(users):
    """
    Supprime les doublons basés sur l'id GitHub.
    Renvoie (liste_sans_doublons, nombre_de_doublons)
    """
    seen = set()
    unique = []
    duplicates = 0
    for u in users:
        if u['id'] in seen:
            duplicates += 1
            continue
        seen.add(u['id'])
        unique.append(u)
    return unique, duplicates


def filter_users(users, created_after='2015-01-01T00:00:00Z'):
    """
    Filtre les utilisateurs selon:
      - bio non nulle et non vide
      - avatar_url non vide
      - created_at postérieur à la date spécifiée

    Renvoie la liste filtrée et des statistiques sur les exclusions.
    """
    cutoff = datetime.strptime(created_after, "%Y-%m-%dT%H:%M:%SZ")
    filtered = []
    stats = {
        'no_bio': 0,
        'no_avatar': 0,
        'too_old': 0,
        'malformed_date': 0
    }
    for u in users:
        if not u.get('bio'):
            stats['no_bio'] += 1
            continue
        if not u.get('avatar_url'):
            stats['no_avatar'] += 1
            continue
        try:
            created = datetime.strptime(u['created_at'], "%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            stats['malformed_date'] += 1
            continue
        if created <= cutoff:
            stats['too_old'] += 1
            continue
        filtered.append(u)
    return filtered, stats


def save_filtered_users(users, output_path):
    """
    Sauvegarde la liste d'utilisateurs dans output_path en JSON indenté.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def print_report(total, duplicates, stats, kept, cutoff_date):
    print(f"Utilisateurs chargés         : {total}")
    print(f"Doublons supprimés          : {duplicates}")
    print(f"Exclu·e·s (pas de bio)      : {stats['no_bio']}")
    print(f"Exclu·e·s (pas d'avatar)    : {stats['no_avatar']}")
    print(f"Exclu·e·s (date <= {cutoff_date}) : {stats['too_old']}")
    print(f"Exclu·e·s (date mal formée) : {stats['malformed_date']}")
    print(f"Utilisateurs conservés       : {kept}")


def main():
    input_path = 'data/users.json'
    output_path = 'data/filtered_users.json'
    cutoff_date = '2015-01-01T00:00:00Z'

    users = load_users(input_path)
    total = len(users)

    unique_users, duplicates = remove_duplicates(users)
    filtered, stats = filter_users(unique_users, created_after=cutoff_date)
    kept = len(filtered)

    save_filtered_users(filtered, output_path)
    print_report(total, duplicates, stats, kept, cutoff_date)

if __name__ == '__main__':
    main()
