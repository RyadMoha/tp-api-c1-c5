# extract_users.py

import os
import time
import json
import argparse
import requests
import random
from dotenv import load_dotenv

# ─── 1. Chargement du token ────────────────────────────────────────────────────
load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {TOKEN}"}
if not TOKEN:
    raise RuntimeError("⚠️ Veuillez définir GITHUB_TOKEN dans votre .env")

# ─── 2. Gestion du rate limit (en option) ──────────────────────────────────────
def handle_rate_limit(response):
    remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
    reset_ts  = int(response.headers.get("X-RateLimit-Reset", 0))
    if remaining == 0:
        sleep_secs = max(reset_ts - time.time(), 0) + 5
        print(f"Quota atteint. Pause de {sleep_secs:.0f}s…")
        time.sleep(sleep_secs)
        return True
    return False

# ─── 3. Requêtes sécurisées ───────────────────────────────────────────────────
def safe_request(url, headers, params=None):
    backoff = 1
    while True:
        resp = requests.get(url, headers=headers, params=params)

        # Affiche le quota restant à chaque appel
        remaining = resp.headers.get("X-RateLimit-Remaining")
        reset_ts  = resp.headers.get("X-RateLimit-Reset")
        if remaining is not None:
            print(f"🔄 Quota restant : {remaining}  |  Reset à : {reset_ts}")

        # Gestion des réponses spécifiques
        if resp.status_code == 403 and handle_rate_limit(resp):
            continue
        if resp.status_code == 429:
            print(f"429 Too Many Requests, attente {backoff}s…")
            time.sleep(backoff)
            backoff *= 2
            continue
        if 500 <= resp.status_code < 600:
            print(f"Erreur serveur {resp.status_code}, réessai dans {backoff}s…")
            time.sleep(backoff)
            backoff = min(backoff * 2, 60)
            continue

        resp.raise_for_status()
        return resp

# ─── 4. Extraction des utilisateurs ────────────────────────────────────────────
def fetch_users(since_id=20000000):
    url    = "https://api.github.com/users"
    params = {"since": since_id, "per_page": 30}
    resp   = safe_request(url, HEADERS, params)
    users  = resp.json()
    return [(u["login"], u["id"]) for u in users]

def fetch_user_details(login):
    url  = f"https://api.github.com/users/{login}"
    resp = safe_request(url, HEADERS)
    data = resp.json()
    return {
        "login":      data["login"],
        "id":         data["id"],
        "created_at": data["created_at"],
        "avatar_url": data["avatar_url"],
        "bio":        data.get("bio")
    }

# ─── 5. Boucle principale et JSON ─────────────────────────────────────────────
def main(max_users, since_id):
    users = []
    since = since_id

    while len(users) < max_users:
        batch = fetch_users(since)
        if not batch:
            print("Plus aucun utilisateur à récupérer.")
            break

        for login, uid in batch:
            if len(users) >= max_users:
                break
            try:
                users.append(fetch_user_details(login))
            except requests.HTTPError as e:
                if e.response.status_code == 404:
                    print(f"Utilisateur {login} introuvable, ignoré.")
                    continue
                else:
                    raise
            users.append(fetch_user_details(login))
        since = batch[-1][1]
        print(f"→ {len(users)}/{max_users} utilisateurs collectés.")

    os.makedirs("data", exist_ok=True)
    print(f"🚀 Écriture de {len(users)} utilisateurs dans data/users.json…")
    with open("data/users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    print(f"✅ Terminé : {len(users)} utilisateurs enregistrés dans data/users.json")

# ─── 6. Point d’entrée unique ─────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extraire des utilisateurs GitHub via l’API publique"
    )
    parser.add_argument(
        "--max-users", type=int, default=120,
        help="Nombre maximal d’utilisateurs à extraire"
    )
    parser.add_argument(
        "--since", default="random",
        help="ID GitHub de départ ; ou 'random' pour un démarrage aléatoire"
    )
    args = parser.parse_args()

    # Détermine since_id
    if args.since.lower() == "random":
        since_id = random.randint(1, 50_000_000)
        print(f"⚡ Lancement aléatoire : since = {since_id}")
    else:
        since_id = int(args.since)

    main(args.max_users, since_id)
