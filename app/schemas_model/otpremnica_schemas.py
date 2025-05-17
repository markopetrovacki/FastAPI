from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from .. import schemas
from . import firma_schemas, kupac_schemas, stavke_racuna_schemas, user_schemas, avans_schemas



class GetOtpremnica(BaseModel):
    id_racuna: int
    broj_racuna: str
    tip_izdatog_racuna: str
    datum_prometa: datetime | None
    ukupna_osnovica: int 
    ukupna_pdv: int
    ukupna_iznos: int
    valuta: str
    nacin_placanja: str
    broj_racuna_za_uplatu: str
    obaveznik_pdv: str

    napomena_na_fakturi: str
    poziv_na_broj: str | None

    mesto_isporuke: str
    nacin_transporta: str
    datum_isporuke: datetime


    id_firme_fk: int
    id_kupac_fk: int
    id_korisnik_kreirao_fk: int
    id_predracuna: int | None



class GetOtpremnicaId(BaseModel):
    id_racuna: int
    broj_racuna: str
    tip_izdatog_racuna: str
    datum_prometa: datetime | None
    ukupna_osnovica: int
    ukupna_pdv: int
    ukupna_iznos: int
    valuta: str
    nacin_placanja: str
    broj_racuna_za_uplatu: str
    obaveznik_pdv: str

    napomena_na_fakturi: str
    poziv_na_broj: str  | None

    mesto_isporuke: str
    nacin_transporta: str
    datum_isporuke: datetime

    id_firme_fk: int
    id_kupac_fk: int
    id_korisnik_kreirao_fk: int
    id_predracuna: int | None

    user: user_schemas.UserOut
    firma: firma_schemas.GetFirma
    kupac: kupac_schemas.GetKupac

    stavke_usluga: List[stavke_racuna_schemas.StavkaUslugaOtpremnica]
    stavke_roba: List[stavke_racuna_schemas.StavkaRobaOtpremnica]


    class Config:
        orm_model = True



class CreateOtpremnica(BaseModel):
   # valuta: str
   # nacin_placanja: str
   # broj_racuna_za_uplatu: str
   # obaveznik_pdv: str
    
    napomena_na_fakturi: str
   # poziv_na_broj: str

    mesto_isporuke: str
    nacin_transporta: str
    datum_isporuke: datetime

    id_firme_fk: int
    id_kupac_fk: int
    id_predracuna: int | None

    #stavke_usluga: List[stavke_racuna_schemas.CreateUslugaRacun] = [stavke_racuna_schemas.CreateUslugaRacun]
    #stavke_roba: List[stavke_racuna_schemas.CreateRobaRacun] = [stavke_racuna_schemas.CreateRobaRacun]

