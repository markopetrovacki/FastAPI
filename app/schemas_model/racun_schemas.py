from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from .. import schemas
from . import firma_schemas, kupac_schemas, stavke_racuna_schemas, user_schemas



class GetRacun(BaseModel):
    broj_racuna: str
    ukupna_cena_racuna: int
    valuta: str
    obaveznik_pdv: str
    #id_firma_fk: int
    #id_kupac_fk: int


class GetRacunId(BaseModel):
    broj_racuna: str
    ukupna_cena_racuna: int
    valuta: str
    obaveznik_pdv: str
    id_firme_fk: int
    id_kupac_fk: int

    user: user_schemas.UserOut
    firma: firma_schemas.GetFirma
    kupac: kupac_schemas.GetKupac

    stavke_usluga: List[stavke_racuna_schemas.StavkaUsluga]
    stavke_roba: List[stavke_racuna_schemas.StavkaRoba]

    class Config:
        orm_model = True


class CreateRacun(BaseModel):
    broj_racuna: str
    #ukupna_cena_racuna: int
    valuta: str
    obaveznik_pdv: str
    id_firme_fk: int
    id_kupac_fk: int

    stavke_usluga: List[stavke_racuna_schemas.CreateUslugaRacun] = [stavke_racuna_schemas.CreateUslugaRacun]
    stavke_roba: List[stavke_racuna_schemas.CreateRobaRacun] = [stavke_racuna_schemas.CreateRobaRacun]
