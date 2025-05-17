from datetime import datetime, date
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func 
from typing import List, Optional
from app import models, schemas, utils, oauth2
from ..schemas_model import racun_schemas, user_racun_schemas, otpremnica_schemas
from ..database import get_db

router = APIRouter(
    tags = ['Otpremnica']
)

def formatiraj_broj_racuna(redni_broj: int, tip: str = "") -> str:
    godina = date.today().year
    broj = f"{redni_broj:04d}"  # dodaje vodeće nule: 1 → 0001
    if tip.lower() == "otpremnica":
        return f"{broj}-O/{godina}"
    return f"{broj}/{godina}"


@router.get("/otpremnica", response_model=List[otpremnica_schemas.GetOtpremnica])
async def get_otpremnica(db: Session = Depends(get_db)):

    result = db.query(models.Racun).filter(models.Racun.tip_izdatog_racuna == "Otpremnica").all()
    
    return result


@router.get("/otpremnica/{id}", response_model=otpremnica_schemas.GetOtpremnicaId)
async def get_otpremnica_id(id: int, db: Session = Depends(get_db)):

    otpremnica = db.query(models.Racun).filter(models.Racun.id_racuna == id).first()

    if otpremnica.tip_izdatog_racuna != "Otpremnica":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Otpremnica nije pronađen."
        )

    # Ako racun ima povezani predračun, koristi njegov ID za pretragu usluga i robe
    id_za_pretragu = otpremnica.id_predracuna #if otpremnica.id_predracuna else id


    usluge_racun  = (
        db.query(models.UslugaRacun, models.Usluga)
        .join(models.Usluga, models.Usluga.id_usluge == models.UslugaRacun.id_usluge_fk)
        .filter(models.UslugaRacun.id_racuna_fk == id_za_pretragu)
        .all()
    )

    stavke_usluga = []
    for usluga_racun, usluga in usluge_racun:
        stavke_usluga.append({
            "id_usluge_fk": usluga.id_usluge,
            "sifra": usluga.sifra,
            "opis": usluga.opis,
            "cena_usluge": usluga.cena_usluge,
          #  "stopa_PDVa": usluga_racun.stopa_PDVa,
          #  "cena_usluge_sa_PDV_om": (usluga.cena_usluge * (usluga.stopa_PDVa * 0.01 +1)),
            "kolicina": usluga_racun.kolicina,
            "ukupna_cena_usluge": usluga_racun.ukupna_cena_usluge    
        })


    usluge_robe = ( 
        db.query(models.RobaRacun, models.Roba)
        .join(models.Roba, models.Roba.id_robe == models.RobaRacun.id_robe_fk)
        .filter(models.RobaRacun.id_racuna_fk == id_za_pretragu)
        .all()
    )

    stavke_roba = []
    for roba_racun, roba in usluge_robe:
        stavke_roba.append({
            "id_robe_fk": roba.id_robe,
            "barcod": roba.barcod,
            "naziv": roba.naziv,           
            "cena_robe": roba.cena_robe,
           # "stopa_PDVa": roba.stopa_PDVa,
           # "cena_robe_sa_PDV_om": (roba.cena_robe * (roba.stopa_PDVa * 0.01 + 1)),
            "kolicina": roba_racun.kolicina,
            "ukupna_cena_robe": roba_racun.ukupna_cena_robe       
        })

    otpremnica.stavke_usluga = stavke_usluga
    otpremnica.stavke_roba = stavke_roba


   # avansni_racuni = (
   #     db.query(models.Racun)
   #     .filter(
   #         models.Racun.id_predracuna == otpremnica.id_predracuna, 
   #         models.Racun.tip_izdatog_racuna =="Avans"
   #     )
   #     .all()
   # )
   # otpremnica.avans = avansni_racuni

    #user = db.query(models.UserRacun.id_user_fk).filter(models.UserRacun.id_racuna_fk == id).scalar()
    otpremnica.user = db.query(models.User).filter(models.User.id_user == otpremnica.id_korisnik_kreirao_fk).first()


    return otpremnica



@router.post("/otpremnica", status_code=201)
def create_otpremnica(otpremnica: otpremnica_schemas.CreateOtpremnica, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
   
    racun = db.query(models.Racun).filter(models.Racun.id_racuna == otpremnica.id_predracuna).first()

    if not racun:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prilikom kreiranja otpremnice morate dodati Id_predracuna sto je ili Id_predracuna ili Id_racuna za koji se kreira otpremnica"
        )


    nova_otpremnica = models.Racun(
        broj_racuna="",
        tip_izdatog_racuna = "Otpremnica",
        datum_prometa = datetime.utcnow(),
        ukupna_osnovica = racun.ukupna_osnovica,
        ukupna_pdv = racun.ukupna_pdv,
        ukupna_iznos = racun.ukupna_iznos,

        valuta = racun.valuta,
        nacin_placanja = racun.nacin_placanja,
        broj_racuna_za_uplatu = racun.broj_racuna_za_uplatu,
        obaveznik_pdv = racun.obaveznik_pdv,
       
        napomena_na_fakturi = otpremnica.napomena_na_fakturi,
        poziv_na_broj = racun.poziv_na_broj,

        mesto_isporuke = otpremnica.mesto_isporuke,
        nacin_transporta = otpremnica.nacin_transporta,
        datum_isporuke  = otpremnica.datum_isporuke,
        
        id_firme_fk=otpremnica.id_firme_fk,
        id_kupac_fk=otpremnica.id_kupac_fk,
        id_korisnik_kreirao_fk=current_user.id_user,
        
        id_predracuna = racun.id_predracuna,
        
    )
    db.add(nova_otpremnica)
    db.flush()  # dobijanje ID otpremnice
    db.commit()

    if racun.id_predracuna is None:
        nova_otpremnica.id_predracuna = racun.id_racuna
    

    nova_otpremnica.broj_racuna = formatiraj_broj_racuna(nova_otpremnica.id_racuna, "otpremnica")
    db.commit()
    db.refresh(nova_otpremnica)

    return {"message": "Otpremnica uspešno kreirana", "id_otpremnice": nova_otpremnica.id_racuna}



@router.delete("/otpremnica/{id}", status_code=200)
def delete_otpremnica(id: int, db: Session = Depends(get_db)):
    
    # Proveri da li račun postoji
    racun = db.query(models.Racun).filter(models.Racun.id_racuna == id).first()
      
    if racun.tip_izdatog_racuna != "Otpremnica":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"U ovoj sekciji možete brisati samo otpremnice."
        )

    if not racun:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Otpremnica sa ID {id} nije pronađen."
        )

    # Na kraju brišemo sam račun
    db.delete(racun)

    db.commit()

    return {"message": f"Otpremnica sa ID {id} i povezane stavke uspešno obrisani."}

