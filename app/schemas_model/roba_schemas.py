from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from .. import schemas


class GetRoba(BaseModel):
    id_robe: int
    barcod: str 
    naziv: str
    jedinica_mere: str
    cena_robe: int 
    stopa_PDVa: int
    iznos_pdv_robe: int
    iznos_robe_sa_pdv: int 
    valuta: str
    
    id_firme_fk: int 
    


class CreateRoba(BaseModel):
    barcod: str 
    naziv: str
    jedinica_mere: str
    cena_robe: int 
    stopa_PDVa: int
    valuta: str
    
    id_firme_fk: int 