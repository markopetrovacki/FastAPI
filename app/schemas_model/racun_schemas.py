from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from .. import schemas
from . import firma_schemas, kupac_schemas, stavke_racuna_schemas, user_schemas, avans_schemas



class GetRacun(BaseModel):
    id_racuna: int
    broj_racuna: str
    #status_fakture: str
    status_racuna: str
    tip_izdatog_racuna: str
    datum_izdavanja: datetime
    datum_valute: datetime
    datum_prometa: datetime | None
    ukupna_osnovica: int
    ukupna_pdv: int
    ukupna_iznos: int
    valuta: str
    nacin_placanja: str
    broj_racuna_za_uplatu: str
    obaveznik_pdv: str
    
    ukupna_osnovica_20: int
    ukupna_osnovica_10: int
    ukupna_osnovica_0: int
    ukupna_pdv_20: int
    ukupna_pdv_10: int
    ukupna_iznos_20: int
    ukupna_iznos_10: int
    #id_firma_fk: int
    #id_kupac_fk: int
    #id_predracuna: int



class GetRacunId(BaseModel):
    id_racuna: int
    broj_racuna: str
    #status_fakture: str
    status_racuna: str
    tip_izdatog_racuna: str
    datum_izdavanja: datetime
    datum_valute: datetime
    datum_prometa: datetime | None
    ukupna_osnovica: int
    ukupna_pdv: int
    ukupna_iznos: int
    valuta: str
    nacin_placanja: str
    broj_racuna_za_uplatu: str
    obaveznik_pdv: str
    
    ukupna_osnovica_20: int
    ukupna_osnovica_10: int
    ukupna_osnovica_0: int
    ukupna_pdv_20: int
    ukupna_pdv_10: int
    ukupna_iznos_20: int
    ukupna_iznos_10: int

    vrednost_avansa_20: int
    vrednost_avansa_10: int
    vrednost_avansa_0: int
    
    id_korisnik_kreirao_fk: int

    id_firme_fk: int
    id_kupac_fk: int
    id_predracuna: int | None

    user: user_schemas.UserOut
    firma: firma_schemas.GetFirma
    kupac: kupac_schemas.GetKupac

    stavke_usluga: List[stavke_racuna_schemas.StavkaUsluga]
    stavke_roba: List[stavke_racuna_schemas.StavkaRoba]
    avans: List[avans_schemas.GetAvans]

    class Config:
        orm_model = True


class CreateRacun(BaseModel):
    #broj_racuna: str
    status_racuna: str
    #tip_izdatog_racuna: str
    datum_valute: datetime
    #datum_prometa: datetime | None
    valuta: str
    nacin_placanja: str
    broj_racuna_za_uplatu: str
    obaveznik_pdv: str
    
    id_firme_fk: int
    id_kupac_fk: int
    #id_predracuna: int

    stavke_usluga: List[stavke_racuna_schemas.CreateUslugaRacun] = [stavke_racuna_schemas.CreateUslugaRacun]
    stavke_roba: List[stavke_racuna_schemas.CreateRobaRacun] = [stavke_racuna_schemas.CreateRobaRacun]



class CreateRacunPredracun(BaseModel):
     id_predracuna: int