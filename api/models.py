from pydantic import BaseModel, HttpUrl
from datetime import datetime

class User(BaseModel):
    login: str
    id: int
    created_at: datetime
    avatar_url: HttpUrl
    bio: str = None