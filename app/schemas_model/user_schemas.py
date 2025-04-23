from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime



class UserOut(BaseModel):
    id_user: int
    email: EmailStr
    datum_kreiranja_naloga: datetime

    class Config:
        orm_model = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    ime_korisnika: str
    prezime_korisnika: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str

