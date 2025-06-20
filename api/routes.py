from fastapi import APIRouter, Depends, HTTPException
from typing import List
from api.models import User
from api.security import get_current_username
import json
import os

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# Charger les données au démarrage
DATA_PATH = os.path.join(os.path.dirname(__file__), os.pardir, 'data', 'filtered_users.json')
with open(DATA_PATH, 'r', encoding='utf-8') as f:
    _users = json.load(f)

# Conversion en objets Pydantic
_users_data = [User(**u) for u in _users]

@router.get(
    "/",
    summary="Liste des utilisateurs",
    description="Retourne la liste complète des utilisateurs filtrés",
    response_model=List[User]
)
def list_users(username: str = Depends(get_current_username)):
    return _users_data

@router.get(
    "/{login}",
    summary="Détail utilisateur",
    description="Retourne les détails d'un utilisateur spécifique",
    response_model=User
)
def get_user(login: str, username: str = Depends(get_current_username)):
    for user in _users_data:
        if user.login.lower() == login.lower():
            return user
    raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

@router.get(
    "/search",
    summary="Recherche utilisateurs",
    description="Recherche les utilisateurs dont le login contient le terme",
    response_model=List[User]
)
def search_users(q: str, username: str = Depends(get_current_username)):
    q_lower = q.lower()
    results = [user for user in _users_data if q_lower in user.login.lower()]
    return results