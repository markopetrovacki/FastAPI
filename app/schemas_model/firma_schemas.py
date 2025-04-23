from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from . import user_schemas


class GetFirma(BaseModel):
    sifra: str
    naziv: str
    mesto: str
    adresa: str
    pib: int
    maticni_broj: int 

class GetFirmaId(BaseModel):
    sifra: str
    naziv: str
    mesto: str
    adresa: str
    pib: int
    maticni_broj: int 
    #id_user_fk: int
    #user: schemas.UserOut
    user: List[user_schemas.UserOut]

    class Config:
        orm_model = True


class CreateFirma(BaseModel):
    sifra: str
    naziv: str
    mesto: str
    adresa: str
    pib: int
    maticni_broj: int 


class UserFirmaCreate(BaseModel):
    ime: str
    prezime: str
    email: str
    naziv_firme: str
    maticni_broj: int
    
class UserFirma(BaseModel):
    id_user_fk: int
    id_firme_fk: int