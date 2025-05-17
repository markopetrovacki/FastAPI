from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from .. import schemas


class GetKupac(BaseModel):
    id_kupac: int
    sifra: str
    naziv: str
    mesto: str
    adresa: str
    pib: int
    maticni_broj: int 
    kontatkt: str
    id_firme_fk: int
    


class CreateKupac(BaseModel):
    sifra: str
    naziv: str
    mesto: str
    adresa: str
    pib: int
    maticni_broj: int 
    kontatkt: str
    id_firme_fk: int
    