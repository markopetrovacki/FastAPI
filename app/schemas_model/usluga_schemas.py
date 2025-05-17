from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from .. import schemas


class GetUsluga(BaseModel):
    id_usluge: int
    sifra: str
    opis: str
    jedinica_mere: str
    cena_usluge: int
    stopa_PDVa: int
    iznos_pdv_usluge: int
    iznos_usluge_sa_pdv: int
    valuta: str

    id_firme_fk: int


class CreateUsluga(BaseModel):
    sifra: str
    opis: str
    jedinica_mere: str
    cena_usluge: int
    stopa_PDVa: int
    valuta: str

    id_firme_fk: int