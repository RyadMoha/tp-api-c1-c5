# GitHub Fast API

## Description

Ce projet vise à extraire, nettoyer et exposer des profils utilisateurs GitHub via une API REST sécurisée.

**Étapes principales :**

1. **Extraction** des utilisateurs GitHub (`extract_users.py`) via l’API publique.
2. **Nettoyage et filtrage** (`step2_pipeline.py`) pour ne conserver que les profils pertinents (bio renseignée, avatar, créés après 2015).
3. **Exposition** des données filtrées via une **API FastAPI** sécurisée (Basic Auth).

---

## Scripts Python

### 1. `extract_users.py`

* Interroge l’API publique GitHub pour récupérer un échantillon d’utilisateurs (30 par appel).
* Gère la pagination, le rate limit et les erreurs HTTP.
* **Options** :

  * `--max-users` : nombre maximal d’utilisateurs à extraire (par défaut 120).
  * `--no-random` : désactive le démarrage aléatoire (sinon démarre à un ID aléatoire).
  * `--since` : ID GitHub de départ pour la pagination (ignoré si `--no-random`).
* Génère le fichier `data/users.json`.

### 2. `step2_pipeline.py`

* Lit `data/users.json` et vérifie la structure.
* Supprime les doublons (basés sur `id`).
* Filtre selon :

  * Bio non vide.
  * Avatar non vide.
  * `created_at` postérieur au 1er janvier 2015.
* **Options** :

  * `--sample-size` : taille d’un échantillon aléatoire à prélever avant nettoyage.
* Sauvegarde le résultat dans `data/filtered_users.json`.

### 3. API FastAPI (`api/`)

* **Fichiers** :

  * `api/main.py` : lancement de l’application.
  * `api/routes.py` : endpoints pour lister, rechercher et obtenir un utilisateur.
  * `api/models.py` : schéma Pydantic `User`.
  * `api/security.py` : Basic Auth (lecture de `API_USER` et `API_PASS` depuis `.env`).

---

## Installation

1. **Cloner le dépôt** :

   ```bash
   git clone <url-du-projet>
   cd GitHub-Fast-API
   ```
2. **Créer et activer un environnement virtuel** :

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. **Installer les dépendances** :

   ```bash
   pip install -r requirements.txt
   ```
4. **Créer un fichier `.env` à la racine** :

   ```dotenv
   GITHUB_TOKEN=<votre_token_GitHub>
   API_USER=admin
   API_PASS=admin123
   ```

---

## Exécution

### 1. Extraction des utilisateurs

```bash
python extract_users.py --max-users 500
```
### 2. Nettoyage et filtrage

```bash
python step2_pipeline.py
```

Pour un échantillon de 200 utilisateurs :

```bash
python step2_pipeline.py --sample-size 200
```

### 3. Lancement de l’API

```bash
uvicorn api.main:app --reload
```

> L’API sera disponible sur `http://localhost:8000`.
> La documentation Swagger se trouve sur `http://localhost:8000/docs`.

---

## Exemples de requêtes

* **Lister tous les utilisateurs**

  ```bash
  curl -u admin:admin123 http://localhost:8000/users/
  ```

* **Détail d’un utilisateur**

  ```bash
  curl -u admin:admin123 http://localhost:8000/users/mojombo
  ```

* **Recherche par mot-clé**

  ```bash
  curl -u admin:admin123 "http://localhost:8000/users/search?q=dev"
  ```

---

## Format des réponses

* **Liste** (`GET /users/`)

  ```json
  [
    {
      "login": "username",
      "id": 123,
      "created_at": "2020-05-10T12:34:56Z",
      "avatar_url": "https://...",
      "bio": "Bio de l'utilisateur"
    },
    ...
  ]
  ```

* **Détail** (`GET /users/{login}`)

  ```json
  {
    "login": "mojombo",
    "id": 1,
    "created_at": "2007-10-20T05:24:19Z",
    "avatar_url": "https://...",
    "bio": null
  }
  ```

* **Recherche** (`GET /users/search?q=ai`)

  ```json
  [
    {
      "log
  ```
