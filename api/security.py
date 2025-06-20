from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import os
from dotenv import load_dotenv

load_dotenv()

security = HTTPBasic()

# Charger les credentials depuis .env ou définir ici
VALID_USERS = {
    os.getenv('API_USER', 'admin'): os.getenv('API_PASS', 'admin123')
}

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_password = VALID_USERS.get(credentials.username)
    if not (correct_password and secrets.compare_digest(credentials.password, correct_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
            headers={"WWW-Authenticate": "Basic"}
        )
    return credentials.username