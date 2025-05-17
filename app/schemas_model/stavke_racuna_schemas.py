from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from .. import schemas
from . import firma_schemas, kupac_schemas



class GetRobaRacun(BaseModel):
    #id_roba_racun: int
    kolicina: int
    osnovica_pdv_robe: int 
    stopa_PDVa: int 
    iznos_pdv_robe: float
    ukupna_cena_robe: int
    #datum_kreiranja: datetime
    id_robe_fk: int
  #  id_racuna_fk: int


class GetUslugaRacun(BaseModel):
   # id_usluga_racun: int
    kolicina: int
    osnovica_pdv_usluge: int
    stopa_PDVa: int
    iznos_pdv_usluge: float
    ukupna_cena_usluge: int
    datum_kreiranja: datetime
    id_usluge_fk: int
  #  id_racuna_fk: int



class CreateRobaRacun(BaseModel):
    kolicina: int
    #ukupna_cena_robe: int
    id_robe_fk: int


class CreateUslugaRacun(BaseModel):
    kolicina: int
    #ukupna_cena_usluge: int
    id_usluge_fk: int




class StavkaRoba(BaseModel):
    id_robe_fk: int
    barcod: str
    naziv: str
    cena_robe: int
    stopa_PDVa: int
    cena_robe_sa_PDV_om: float 
    kolicina: int
    ukupna_cena_robe: int
   


class StavkaUsluga(BaseModel):
    id_usluge_fk: int
    sifra: str
    opis: str
    cena_usluge: int
    stopa_PDVa: int 
    cena_usluge_sa_PDV_om: float
    kolicina: int
    ukupna_cena_usluge: int
    

class StavkaRobaOtpremnica(BaseModel):
    id_robe_fk: int
    barcod: str
    naziv: str
    cena_robe: int
    #stopa_PDVa: int | None
    #cena_robe_sa_PDV_om: int | None
    kolicina: int
    ukupna_cena_robe: int
   


class StavkaUslugaOtpremnica(BaseModel):
    id_usluge_fk: int
    sifra: str
    opis: str
    cena_usluge: int
   # stopa_PDVa: int | None
   # cena_usluge_sa_PDV_om: int | None
    kolicina: int
    ukupna_cena_usluge: int


