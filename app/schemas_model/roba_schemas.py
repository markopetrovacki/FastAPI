from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from .. import schemas


class GetRoba(BaseModel):
    barcod: str 
    naziv: str
    jedinica_mere: str
    stopa_PDV: int
    cena_robe: int 
    id_firme_fk: int 
    