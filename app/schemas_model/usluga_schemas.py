from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from .. import schemas


class GetUsluga(BaseModel):
    sifra: str
    opis: str
    jedinica_mere: str
    stopa_PDV: int
    cena_usluge: int
    id_firme_fk: int