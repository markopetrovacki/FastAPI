from datetime import datetime
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func 
from typing import List, Optional
from app import models, schemas, utils, oauth2
from ..schemas_model import racun_schemas, user_racun_schemas
from ..database import get_db

router = APIRouter(
    tags = ['Racun']
)



@router.get("/racun", response_model=List[racun_schemas.GetRacun])
async def get_racun(db: Session = Depends(get_db)):

    result = db.query(models.Racun).all()
    
    return result


@router.get("/racun/{id}", response_model=racun_schemas.GetRacunId)
async def get_racun_id(id: int, db: Session = Depends(get_db)):

    racun = db.query(models.Racun).filter(models.Racun.id_racuna == id).first()

   # uslugeRacun = db.query(models.UslugaRacun).filter(models.UslugaRacun.id_racun_fk == id).all()

    usluge_racun  = (
        db.query(models.UslugaRacun, models.Usluga)
        .join(models.Usluga, models.Usluga.id_usluge == models.UslugaRacun.id_usluge_fk)
        .filter(models.UslugaRacun.id_racuna_fk == id)
        .all()
    )

    stavke_usluga = []
    for usluga_racun, usluga in usluge_racun:
        stavke_usluga.append({
            "id_usluge_fk": usluga.id_usluge,
            "sifra": usluga.sifra,
            "opis": usluga.opis,
            "cena_usluge": usluga.cena_usluge,
            "stopa_PDV": usluga.stopa_PDV,
            "cena_usluge_sa_PDV_om": (usluga.cena_usluge * (usluga.stopa_PDV * 0.01 +1)),
            "kolicina": usluga_racun.kolicina,
            "ukupna_cena_usluge": usluga_racun.ukupna_cena_usluge
            
            
        })

    usluge_robe = ( 
        db.query(models.RobaRacun, models.Roba)
        .join(models.Roba, models.Roba.id_robe == models.RobaRacun.id_robe_fk)
        .filter(models.RobaRacun.id_racuna_fk == id)
        .all()
    )

    stavke_roba = []
    for roba_racun, roba in usluge_robe:
        stavke_roba.append({
            "id_robe_fk": roba.id_robe,
            "barcod": roba.barcod,
            "naziv": roba.naziv,           
            "cena_robe": roba.cena_robe,
            "stopa_PDV": roba.stopa_PDV,
            "cena_robe_sa_PDV_om": (roba.cena_robe * (roba.stopa_PDV * 0.01 + 1)),
            "kolicina": roba_racun.kolicina,
            "ukupna_cena_robe": roba_racun.ukupna_cena_robe
            
            
        })


    racun.stavke_usluga = stavke_usluga
    racun.stavke_roba = stavke_roba



    user = db.query(models.UserRacun.id_user_fk).filter(models.UserRacun.id_racuna_fk == id).scalar()
    racun.user = db.query(models.User).filter(models.User.id_user == user).first()

    if not racun:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= f"firma sa id-jem: {id} nije pronadjena")
    
    return racun


#@router.post("/racun", status_code=status.HTTP_201_CREATED, response_model= racun_schemas.GetRacun)
#def create_racun(post: racun_schemas.CreateRacun, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

 #   new_racun = models.Racun(**post.dict())

   # db.add(new_racun)
  #  db.commit()
 #   db.refresh(new_racun)
#
 #   return new_racun


@router.post("/racun", status_code=201)
def create_racun(racun: racun_schemas.CreateRacun, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    novi_racun = models.Racun(
       # **racun.dict()
        broj_racuna=racun.broj_racuna,
        ukupna_cena_racuna = 0,
        valuta = racun.valuta,
        obaveznik_pdv = racun.obaveznik_pdv,
        id_firme_fk = racun.id_firme_fk,
        id_kupac_fk = racun.id_kupac_fk
    )
    db.add(novi_racun)
    db.flush()  # da dobijemo ID računa

    ukupna_cena_racuna = 0

    for stavka in racun.stavke_usluga:

        #cena_usluge = db.query(models.Usluga.cena_usluge).filter(models.Usluga.id_usluge == stavka.id_usluge_fk).scalar()
        usluga = db.query(models.Usluga).filter(models.Usluga.id_usluge == stavka.id_usluge_fk).first()

        db.add(models.UslugaRacun(
            id_racuna_fk=novi_racun.id_racuna,
            id_usluge_fk=stavka.id_usluge_fk,
            kolicina=stavka.kolicina,
            ukupna_cena_usluge= stavka.kolicina * usluga.cena_usluge * (usluga.stopa_PDV * 0.01 + 1)
        ))
        ukupna_cena_racuna = ukupna_cena_racuna + (stavka.kolicina * usluga.cena_usluge * (usluga.stopa_PDV * 0.01 +1))
        #ovo je cena sa PDV-om koji je unet samo ga nisam ispisao na racunu to bi verovatno trebalo


    for stavka in racun.stavke_roba:
        
        #cena_robe = db.query(models.Roba.cena_robe).filter(models.Roba.id_robe == stavka.id_robe_fk).scalar()
        roba = db.query(models.Roba).filter(models.Roba.id_robe == stavka.id_robe_fk).first()

        db.add(models.RobaRacun(
            id_racuna_fk=novi_racun.id_racuna,
            id_robe_fk=stavka.id_robe_fk,
            kolicina=stavka.kolicina,
            ukupna_cena_robe=stavka.kolicina * roba.cena_robe * (roba.stopa_PDV * 0.01 + 1)
        ))
        ukupna_cena_racuna = ukupna_cena_racuna + (stavka.kolicina * roba.cena_robe * (roba.stopa_PDV * 0.01 + 1))

    userRacun = models.UserRacun(
        datum_kreiranja_racuna=datetime.utcnow(),
       # datum_izmene_racuna = racun.datum_izmene_racuna,
       # datum_izdavanja_racuna = racun.datum_izdavanja_racuna,
        Tip_izdatog_racuna = "Racun normalni",
        id_user_fk = current_user.id_user,
        id_racuna_fk = novi_racun.id_racuna 
    )
    db.add(userRacun)

    novi_racun.ukupna_cena_racuna = ukupna_cena_racuna
    db.commit()
    db.refresh(novi_racun)

    return {"message": "Račun uspešno kreiran", "id_racuna": novi_racun.id_racuna}



@router.put("/racun/{id}", status_code=200)
def update_racun(id: int, racun: racun_schemas.CreateRacun, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # Pronađi postojeći račun
    postojeci_racun = db.query(models.Racun).filter(models.Racun.id_racuna == id).first()

    if not postojeci_racun:
        raise HTTPException(status_code=404, detail="Račun nije pronađen.")

    # Ažuriranje podataka
    postojeci_racun.broj_racuna = racun.broj_racuna
    #postojeci_racun.ukupna_cena_racuna = racun.ukupna_cena_racuna
    postojeci_racun.valuta = racun.valuta
    postojeci_racun.obaveznik_pdv = racun.obaveznik_pdv
    postojeci_racun.id_firme_fk = racun.id_firme_fk
    postojeci_racun.id_kupac_fk = racun.id_kupac_fk

    # OBRIŠI POSTOJEĆE STAVKE
    db.query(models.UslugaRacun).filter(models.UslugaRacun.id_racuna_fk == id).delete()
    db.query(models.RobaRacun).filter(models.RobaRacun.id_racuna_fk == id).delete()

    ukupna_cena_racuna = 0

    # DODAJ NOVE STAVKE USLUGA
    for stavka in racun.stavke_usluga:
        
        #cena_usluge = db.query(models.Usluga.cena_usluge).filter(models.Usluga.id_usluge == stavka.id_usluge_fk).scalar()
        usluga = db.query(models.Usluga).filter(models.Usluga.id_usluge == stavka.id_usluge_fk).first()
        
        db.add(models.UslugaRacun(
            id_racuna_fk=id,
            id_usluge_fk=stavka.id_usluge_fk,
            kolicina=stavka.kolicina,
            ukupna_cena_usluge= stavka.kolicina * usluga.cena_usluge * (usluga.stopa_PDV * 0.01 + 1)
        ))
        ukupna_cena_racuna = ukupna_cena_racuna + (stavka.kolicina * usluga.cena_usluge * (usluga.stopa_PDV * 0.01 +1))
    

    # DODAJ NOVE STAVKE ROBA
    for stavka in racun.stavke_roba:

        #cena_robe = db.query(models.Roba.cena_robe).filter(models.Roba.id_robe == stavka.id_robe_fk).scalar()
        roba = db.query(models.Roba).filter(models.Roba.id_robe == stavka.id_robe_fk).first()
       
        db.add(models.RobaRacun(
            id_racuna_fk=id,
            id_robe_fk=stavka.id_robe_fk,
            kolicina=stavka.kolicina,
            ukupna_cena_robe=stavka.kolicina * roba.cena_robe * (roba.stopa_PDV * 0.01 + 1)
        ))
        ukupna_cena_racuna = ukupna_cena_racuna + (stavka.kolicina * roba.cena_robe * (roba.stopa_PDV * 0.01 + 1))


    # Ažuriraj i datum izmene u userRacun tabeli
    user_racun = db.query(models.UserRacun).filter(models.UserRacun.id_racuna_fk == id).first()
    if user_racun:
        user_racun.datum_izmene_racuna = datetime.utcnow(),
        user_racun.Tip_izdatog_racuna = "Racun normalni izmenjen"

    postojeci_racun.ukupna_cena_racuna = ukupna_cena_racuna

    db.commit()
    db.refresh(postojeci_racun)

    return {"message": "Račun uspešno ažuriran", "id_racuna": postojeci_racun.id_racuna}


@router.delete("/racun/{id}", status_code=200)
def delete_racun(id: int, db: Session = Depends(get_db)):
    
    # Proveri da li račun postoji
    racun = db.query(models.Racun).filter(models.Racun.id_racuna == id).first()
   
    if not racun:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Račun sa ID {id} nije pronađen."
        )

    # Prvo brišemo stavke usluga
    db.query(models.UslugaRacun).filter(models.UslugaRacun.id_racuna_fk == id).delete()

    # Zatim brišemo stavke roba
    db.query(models.RobaRacun).filter(models.RobaRacun.id_racuna_fk == id).delete()

     # Zatim brišemo user racun tabelu
    db.query(models.UserRacun).filter(models.UserRacun.id_racuna_fk == id).delete()

    # Na kraju brišemo sam račun
    db.delete(racun)

    db.commit()

    return {"message": f"Račun sa ID {id} i povezane stavke uspešno obrisani."}
