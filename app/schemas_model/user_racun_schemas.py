from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime



class GetUserRacun(BaseModel):
    datum_kreiranja: datetime
    datum_izmene: datetime
    datum_izdavanja: datetime
    Tip_izdatog_racuna: str
    id_user_fk: int
    id_racuna_fk: int
