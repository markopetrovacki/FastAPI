from datetime import datetime, date
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func 
from typing import List, Optional
from app import models, schemas, utils, oauth2
from ..schemas_model import  user_racun_schemas, predracun_schemas
from ..database import get_db

router = APIRouter(
    tags = ['Predracun']
)

def formatiraj_broj_racuna(redni_broj: int, tip: str = "") -> str:
    godina = date.today().year
    broj = f"{redni_broj:04d}"  # dodaje vodeće nule: 1 → 0001
    if tip.lower() == "predracun":
        return f"{broj}-P/{godina}"
    return f"{broj}/{godina}"



@router.get("/predracun", response_model=List[predracun_schemas.GetPredracun])
async def get_predracun(db: Session = Depends(get_db)):

    result = db.query(models.Racun).filter(models.Racun.tip_izdatog_racuna == "Predracun").all()
    
    return result


@router.get("/predracun/{id}", response_model=predracun_schemas.GetPredracunId)
async def get_predracun_id(id: int, db: Session = Depends(get_db)):

    predracun = db.query(models.Racun).filter(models.Racun.id_racuna == id).first()

    # ovde mozda da stavis jedan if da ako tip racuna nije PREDRACUN da ne moze da ti izadje racun

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
            "stopa_PDVa": usluga_racun.stopa_PDVa,
            "cena_usluge_sa_PDV_om": (usluga.cena_usluge * (usluga.stopa_PDVa * 0.01 +1)),
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
            "stopa_PDVa": roba.stopa_PDVa,
            "cena_robe_sa_PDV_om": (roba.cena_robe * (roba.stopa_PDVa * 0.01 + 1)),
            "kolicina": roba_racun.kolicina,
            "ukupna_cena_robe": roba_racun.ukupna_cena_robe
            
            
        })


    predracun.stavke_usluga = stavke_usluga
    predracun.stavke_roba = stavke_roba



    user = db.query(models.UserRacun.id_user_fk).filter(models.UserRacun.id_racuna_fk == id).scalar()
    predracun.user = db.query(models.User).filter(models.User.id_user == user).first()

    if not predracun:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= f"predracun sa id-jem: {id} nije pronadjena")
    
    return predracun


@router.post("/predracun", status_code=201)
def create_predracun(predracun: predracun_schemas.CreatePredracun, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    novi_predracun = models.Racun(
       # **racun.dict()
        broj_racuna = "",
        datum_valute = predracun.datum_valute,
       # datum_prometa = predracun.datum_prometa,
        valuta = predracun.valuta,
        nacin_placanja = predracun.nacin_placanja,
        broj_racuna_za_uplatu = predracun.broj_racuna_za_uplatu,
        obaveznik_pdv = predracun.obaveznik_pdv,
        status_racuna = predracun.status_racuna,
       #
        ukupna_osnovica = 0, 
        ukupna_pdv = 0,
        ukupna_iznos = 0,  

        ukupna_osnovica_20 = 0,
        ukupna_osnovica_10 = 0,
        ukupna_osnovica_0 = 0,
        ukupna_pdv_20 = 0,
        ukupna_pdv_10 = 0,
        ukupna_iznos_20 = 0,
        ukupna_iznos_10 = 0,
   
        tip_izdatog_racuna ="Predracun",
        datum_izdavanja = datetime.utcnow(),

        id_firme_fk = predracun.id_firme_fk,
        id_kupac_fk = predracun.id_kupac_fk,
        id_korisnik_kreirao_fk = current_user.id_user
    )
    db.add(novi_predracun)
    db.flush()  # da dobijemo ID računa

   # ukupna_osnovica = 0
    if predracun.stavke_usluga:
        for stavka in predracun.stavke_usluga:
        
            #cena_usluge = db.query(models.Usluga.cena_usluge).filter(models.Usluga.id_usluge == stavka.id_usluge_fk).scalar()
            usluga = db.query(models.Usluga).filter(models.Usluga.id_usluge == stavka.id_usluge_fk).first()

            if not usluga:
                raise HTTPException(status_code=404, detail=f"Usluga sa ID {stavka.id_usluge_fk} ne postoji.")

            # PROVERA: da li usluga pripada firmi sa racuna
            if usluga.id_firme_fk != novi_predracun.id_firme_fk:
                raise HTTPException(
                    status_code=400,
                    detail=f"Usluga sa ID {usluga.id_usluge} nije dodeljena firmi sa ID {novi_predracun.id_firme_fk}."
                )
            
            db.add(models.UslugaRacun(
                id_racuna_fk=novi_predracun.id_racuna,
                id_usluge_fk=stavka.id_usluge_fk,

                kolicina=stavka.kolicina,
                osnovica_pdv_usluge = usluga.cena_usluge,
                stopa_PDVa = usluga.stopa_PDVa,

                iznos_pdv_usluge = usluga.iznos_pdv_usluge,

            #  ukupna_cena_usluge= stavka.kolicina * usluga.cena_usluge * (usluga.stopa_PDVa * 0.01 + 1),
                ukupna_cena_usluge= stavka.kolicina * usluga.iznos_usluge_sa_pdv,
            
                datum_kreiranja = datetime.utcnow()
            ))
        # ukupna_osnovica = ukupna_osnovica + (stavka.kolicina * usluga.cena_usluge * (usluga.stopa_PDVa * 0.01 +1))
            novi_predracun.ukupna_osnovica = novi_predracun.ukupna_osnovica + stavka.kolicina * usluga.cena_usluge
            novi_predracun.ukupna_pdv = novi_predracun.ukupna_pdv + stavka.kolicina  * usluga.iznos_pdv_usluge
            novi_predracun.ukupna_iznos = novi_predracun.ukupna_iznos + stavka.kolicina * usluga.iznos_usluge_sa_pdv
            #ovo je cena sa PDV-om koji je unet samo ga nisam ispisao na racunu to bi verovatno trebalo

            if usluga.stopa_PDVa == 20:
                novi_predracun.ukupna_osnovica_20 = novi_predracun.ukupna_osnovica_20 + stavka.kolicina * usluga.cena_usluge
                novi_predracun.ukupna_pdv_20 = novi_predracun.ukupna_pdv_20 + (stavka.kolicina * usluga.iznos_pdv_usluge)
                novi_predracun.ukupna_iznos_20 = novi_predracun.ukupna_iznos_20 +  stavka.kolicina * usluga.iznos_usluge_sa_pdv
            elif usluga.stopa_PDVa == 10:
                novi_predracun.ukupna_osnovica_10 = novi_predracun.ukupna_osnovica_10 + stavka.kolicina * usluga.cena_usluge
                novi_predracun.ukupna_pdv_10 = novi_predracun.ukupna_pdv_10 + (stavka.kolicina * usluga.iznos_pdv_usluge)
                novi_predracun.ukupna_iznos_10 = novi_predracun.ukupna_iznos_10 +  stavka.kolicina * usluga.iznos_usluge_sa_pdv
            elif usluga.stopa_PDVa == 0:
                novi_predracun.ukupna_osnovica_0 = novi_predracun.ukupna_osnovica_0 + stavka.kolicina * usluga.cena_usluge

    if predracun.stavke_roba:
        for stavka in predracun.stavke_roba:
            
            #cena_robe = db.query(models.Roba.cena_robe).filter(models.Roba.id_robe == stavka.id_robe_fk).scalar()
            roba = db.query(models.Roba).filter(models.Roba.id_robe == stavka.id_robe_fk).first()

            if not roba:
                raise HTTPException(status_code=404, detail=f"Roba sa ID {stavka.id_robe_fk} ne postoji.")

            # PROVERA: da li usluga pripada firmi sa racuna
            if usluga.id_firme_fk != novi_predracun.id_firme_fk:
                raise HTTPException(
                    status_code=400,
                    detail=f"Roba sa ID {roba.id_robe} nije dodeljena firmi sa ID {novi_predracun.id_firme_fk}."
                )
        
            db.add(models.RobaRacun(
                id_racuna_fk=novi_predracun.id_racuna,
                id_robe_fk=stavka.id_robe_fk,

                kolicina=stavka.kolicina,
                osnovica_pdv_robe = roba.cena_robe,
                stopa_PDVa = roba.stopa_PDVa,

                iznos_pdv_robe = roba.iznos_pdv_robe,

                #ukupna_cena_robe=stavka.kolicina * roba.cena_robe * (roba.stopa_PDVa * 0.01 + 1),
                ukupna_cena_robe=stavka.kolicina * roba.iznos_robe_sa_pdv,

                datum_kreiranja = datetime.utcnow()
            ))
            novi_predracun.ukupna_osnovica = novi_predracun.ukupna_osnovica + stavka.kolicina * roba.cena_robe 
            novi_predracun.ukupna_pdv = novi_predracun.ukupna_pdv + stavka.kolicina * roba.iznos_pdv_robe
            novi_predracun.ukupna_iznos = novi_predracun.ukupna_iznos + stavka.kolicina * roba.iznos_robe_sa_pdv

            if roba.stopa_PDVa == 20:
                novi_predracun.ukupna_osnovica_20 = novi_predracun.ukupna_osnovica_20 + stavka.kolicina * roba.cena_robe
                novi_predracun.ukupna_pdv_20 = novi_predracun.ukupna_pdv_20 + (stavka.kolicina * roba.iznos_pdv_robe)
                novi_predracun.ukupna_iznos_20 = novi_predracun.ukupna_iznos_20 +  stavka.kolicina * roba.iznos_robe_sa_pdv
            elif roba.stopa_PDVa == 10:
                novi_predracun.ukupna_osnovica_10 = novi_predracun.ukupna_osnovica_10 + stavka.kolicina * roba.cena_robe
                novi_predracun.ukupna_pdv_10 = novi_predracun.ukupna_pdv_10 + (stavka.kolicina * roba.iznos_pdv_robe)
                novi_predracun.ukupna_iznos_10 = novi_predracun.ukupna_iznos_10 +  stavka.kolicina * roba.iznos_robe_sa_pdv
            elif roba.stopa_PDVa == 0:
                novi_predracun.ukupna_osnovica_0 = novi_predracun.ukupna_osnovica_0 + stavka.kolicina * roba.cena_robe


    userRacun = models.UserRacun(
        datum_kreiranja_racuna=datetime.utcnow(),
       # datum_izmene_racuna = racun.datum_izmene_racuna,
       # datum_izdavanja_racuna = racun.datum_izdavanja_racuna,
        Tip_izdatog_racuna = "Racun normalni",
        id_user_fk = current_user.id_user,
        id_racuna_fk = novi_predracun.id_racuna 
    )
    db.add(userRacun)

    novi_predracun.broj_racuna = formatiraj_broj_racuna(novi_predracun.id_racuna, "predracun")

    db.commit()
    db.refresh(novi_predracun)

    return {"message": "Predračun uspešno kreiran", "id_racuna": novi_predracun.id_racuna}


@router.put("/predracun/{id}", status_code=200)
def update_predracun(id: int, predracun: predracun_schemas.CreatePredracun, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # Pronađi postojeći predracun
    postojeci_predracun = db.query(models.Racun).filter(models.Racun.id_racuna == id).first()

    if postojeci_predracun.tip_izdatog_racuna != "Predracun":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Predračun nije pronađen."
        )

    if not postojeci_predracun:
        raise HTTPException(status_code=404, detail="Predračun nije pronađen.")

    # Ažuriranje podataka
   # postojeci_predracun.broj_racuna = predracun.broj_racuna
    postojeci_predracun.datum_valute = predracun.datum_valute
  #  postojeci_predracun.datum_prometa = predracun.datum_prometa
    postojeci_predracun.valuta = predracun.valuta
    postojeci_predracun.nacin_placanja = predracun.nacin_placanja
    postojeci_predracun.broj_racuna_za_uplatu = predracun.broj_racuna_za_uplatu
    postojeci_predracun.obaveznik_pdv = predracun.obaveznik_pdv
    postojeci_predracun.status_racuna = predracun.status_racuna
    
    postojeci_predracun.ukupna_osnovica = 0
    postojeci_predracun.ukupna_pdv = 0
    postojeci_predracun.ukupna_iznos = 0  

    postojeci_predracun.ukupna_osnovica_20 = 0
    postojeci_predracun.ukupna_osnovica_10 = 0
    postojeci_predracun.ukupna_osnovica_0 = 0
    postojeci_predracun.ukupna_pdv_20 = 0
    postojeci_predracun.ukupna_pdv_10 = 0
    postojeci_predracun.ukupna_iznos_20 = 0
    postojeci_predracun.ukupna_iznos_10 = 0
   
    postojeci_predracun.tip_izdatog_racuna ="Predracun"
    postojeci_predracun.datum_izdavanja = datetime.utcnow()
    
    
    postojeci_predracun.id_firme_fk = predracun.id_firme_fk
    postojeci_predracun.id_kupac_fk = predracun.id_kupac_fk
    postojeci_predracun.id_korisnik_kreirao_fk = current_user.id_user


    # OBRIŠI POSTOJEĆE STAVKE
    db.query(models.UslugaRacun).filter(models.UslugaRacun.id_racuna_fk == id).delete()
    db.query(models.RobaRacun).filter(models.RobaRacun.id_racuna_fk == id).delete()


    # DODAJ NOVE STAVKE USLUGA
    if predracun.stavke_usluga:
        for stavka in predracun.stavke_usluga:
        
            usluga = db.query(models.Usluga).filter(models.Usluga.id_usluge == stavka.id_usluge_fk).first()

            if not usluga:
                raise HTTPException(status_code=404, detail=f"Usluga sa ID {stavka.id_usluge_fk} ne postoji.")

            # PROVERA: da li usluga pripada firmi sa racuna
            if usluga.id_firme_fk != postojeci_predracun.id_firme_fk:
                raise HTTPException(
                    status_code=400,
                    detail=f"Usluga sa ID {usluga.id_usluge} nije dodeljena firmi sa ID {postojeci_predracun.id_firme_fk}."
                )

            db.add(models.UslugaRacun(
                id_racuna_fk=postojeci_predracun.id_racuna,
                id_usluge_fk=stavka.id_usluge_fk,

                kolicina=stavka.kolicina,
                osnovica_pdv_usluge = usluga.cena_usluge,
                stopa_PDVa = usluga.stopa_PDVa,

                iznos_pdv_usluge = usluga.iznos_pdv_usluge,

            #  ukupna_cena_usluge= stavka.kolicina * usluga.cena_usluge * (usluga.stopa_PDVa * 0.01 + 1),
                ukupna_cena_usluge= stavka.kolicina * usluga.iznos_usluge_sa_pdv,
            
                datum_kreiranja = datetime.utcnow()
            ))
        # ukupna_osnovica = ukupna_osnovica + (stavka.kolicina * usluga.cena_usluge * (usluga.stopa_PDVa * 0.01 +1))
            postojeci_predracun.ukupna_osnovica = postojeci_predracun.ukupna_osnovica + stavka.kolicina * usluga.cena_usluge
            postojeci_predracun.ukupna_pdv = postojeci_predracun.ukupna_pdv + stavka.kolicina  * usluga.iznos_pdv_usluge
            postojeci_predracun.ukupna_iznos = postojeci_predracun.ukupna_iznos + stavka.kolicina * usluga.iznos_usluge_sa_pdv
            #ovo je cena sa PDV-om koji je unet samo ga nisam ispisao na racunu to bi verovatno trebalo

            if usluga.stopa_PDVa == 20:
                postojeci_predracun.ukupna_osnovica_20 = postojeci_predracun.ukupna_osnovica_20 + stavka.kolicina * usluga.cena_usluge
                postojeci_predracun.ukupna_pdv_20 = postojeci_predracun.ukupna_pdv_20 + (stavka.kolicina * usluga.iznos_pdv_usluge)
                postojeci_predracun.ukupna_iznos_20 = postojeci_predracun.ukupna_iznos_20 +  stavka.kolicina * usluga.iznos_usluge_sa_pdv
            elif usluga.stopa_PDVa == 10:
                postojeci_predracun.ukupna_osnovica_10 = postojeci_predracun.ukupna_osnovica_10 + stavka.kolicina * usluga.cena_usluge
                postojeci_predracun.ukupna_pdv_10 = postojeci_predracun.ukupna_pdv_10 + (stavka.kolicina * usluga.iznos_pdv_usluge)
                postojeci_predracun.ukupna_iznos_10 = postojeci_predracun.ukupna_iznos_10 +  stavka.kolicina * usluga.iznos_usluge_sa_pdv
            elif usluga.stopa_PDVa == 0:
                postojeci_predracun.ukupna_osnovica_0 = postojeci_predracun.ukupna_osnovica_0 + stavka.kolicina * usluga.cena_usluge


    # DODAJ NOVE STAVKE ROBA
    if predracun.stavke_roba:
        for stavka in predracun.stavke_roba:

            roba = db.query(models.Roba).filter(models.Roba.id_robe == stavka.id_robe_fk).first()

            if not roba:
                raise HTTPException(status_code=404, detail=f"Roba sa ID {stavka.id_robe_fk} ne postoji.")

            # PROVERA: da li usluga pripada firmi sa racuna
            if usluga.id_firme_fk != postojeci_predracun.id_firme_fk:
                raise HTTPException(
                    status_code=400,
                    detail=f"Roba sa ID {roba.id_robe} nije dodeljena firmi sa ID {postojeci_predracun.id_firme_fk}."
                )
        
            db.add(models.RobaRacun(
                id_racuna_fk=postojeci_predracun.id_racuna,
                id_robe_fk=stavka.id_robe_fk,

                kolicina=stavka.kolicina,
                osnovica_pdv_robe = roba.cena_robe,
                stopa_PDVa = roba.stopa_PDVa,
                iznos_pdv_robe = roba.iznos_pdv_robe,
                #ukupna_cena_robe=stavka.kolicina * roba.cena_robe * (roba.stopa_PDVa * 0.01 + 1),
                ukupna_cena_robe=stavka.kolicina * roba.iznos_robe_sa_pdv,
                datum_kreiranja = datetime.utcnow()
            ))

            postojeci_predracun.ukupna_osnovica = postojeci_predracun.ukupna_osnovica + stavka.kolicina * roba.cena_robe 
            postojeci_predracun.ukupna_pdv = postojeci_predracun.ukupna_pdv + stavka.kolicina * roba.iznos_pdv_robe
            postojeci_predracun.ukupna_iznos = postojeci_predracun.ukupna_iznos + stavka.kolicina * roba.iznos_robe_sa_pdv

            if roba.stopa_PDVa == 20:
                postojeci_predracun.ukupna_osnovica_20 = postojeci_predracun.ukupna_osnovica_20 + stavka.kolicina * roba.cena_robe
                postojeci_predracun.ukupna_pdv_20 = postojeci_predracun.ukupna_pdv_20 + (stavka.kolicina * roba.iznos_pdv_robe)
                postojeci_predracun.ukupna_iznos_20 = postojeci_predracun.ukupna_iznos_20 +  stavka.kolicina * roba.iznos_robe_sa_pdv
            elif roba.stopa_PDVa == 10:
                postojeci_predracun.ukupna_osnovica_10 = postojeci_predracun.ukupna_osnovica_10 + stavka.kolicina * roba.cena_robe
                postojeci_predracun.ukupna_pdv_10 = postojeci_predracun.ukupna_pdv_10 + (stavka.kolicina * roba.iznos_pdv_robe)
                postojeci_predracun.ukupna_iznos_10 = postojeci_predracun.ukupna_iznos_10 +  stavka.kolicina * roba.iznos_robe_sa_pdv
            elif roba.stopa_PDVa == 0:
                postojeci_predracun.ukupna_osnovica_0 = postojeci_predracun.ukupna_osnovica_0 + stavka.kolicina * roba.cena_robe



    # Ažuriraj i datum izmene u userRacun tabeli
    user_racun = db.query(models.UserRacun).filter(models.UserRacun.id_racuna_fk == id).first()
    if user_racun:
        user_racun.datum_izmene_racuna = datetime.utcnow(),
        user_racun.Tip_izdatog_racuna = "Predracun"

    db.commit()
    db.refresh(postojeci_predracun)

    return {"message": "Predračun je uspešno ažuriran", "id_racuna": postojeci_predracun.id_racuna}



@router.delete("/predracun/{id}", status_code=200)
def delete_predracun(id: int, db: Session = Depends(get_db)):
    
    # Proveri da li račun postoji
    predracun = db.query(models.Racun).filter(models.Racun.id_racuna == id).first()
   
    if predracun.tip_izdatog_racuna != "Predracun":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"U ovoj sekciji možete brisati samo predračune."
        )

    if not predracun:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Predracun sa ID {id} nije pronađen."
        )

    # Prvo brišemo stavke usluga
    db.query(models.UslugaRacun).filter(models.UslugaRacun.id_racuna_fk == id).delete()

    # Zatim brišemo stavke roba
    db.query(models.RobaRacun).filter(models.RobaRacun.id_racuna_fk == id).delete()

     # Zatim brišemo user racun tabelu
    db.query(models.UserRacun).filter(models.UserRacun.id_racuna_fk == id).delete()

    # Na kraju brišemo sam račun
    db.delete(predracun)

    db.commit()

    return {"message": f"Predracun sa ID {id} i povezane stavke uspešno obrisani."}