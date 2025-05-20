from datetime import datetime, date
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

def formatiraj_broj_racuna(redni_broj: int, tip: str = "") -> str:
    godina = date.today().year
    broj = f"{redni_broj:04d}"  # dodaje vodeće nule: 1 → 0001
    if tip.lower() == "racun":
        return f"{broj}/{godina}"
    return f"{broj}/{godina}"


@router.get("/racun", response_model=List[racun_schemas.GetRacun])
async def get_racun(db: Session = Depends(get_db)):

    result = db.query(models.Racun).filter(models.Racun.tip_izdatog_racuna == "Racun").all()
    
    return result


@router.get("/racun/{id}", response_model=racun_schemas.GetRacunId)
async def get_racun_id(id: int, db: Session = Depends(get_db)):

    racun = db.query(models.Racun).filter(models.Racun.id_racuna == id).first()
   # uslugeRacun = db.query(models.UslugaRacun).filter(models.UslugaRacun.id_racun_fk == id).all()
    
    if racun.tip_izdatog_racuna != "Racun":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Racun nije pronađen."
        )
    
    if not racun:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= f"firma sa id-jem: {id} nije pronadjena")
    
    # Ako racun ima povezani predračun, koristi njegov ID za pretragu usluga i robe
    id_za_pretragu = racun.id_predracuna if racun.id_predracuna else id


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
            "stopa_PDVa": usluga_racun.stopa_PDVa,
            "cena_usluge_sa_PDV_om": (usluga.cena_usluge * (usluga.stopa_PDVa * 0.01 +1)),
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
            "stopa_PDVa": roba.stopa_PDVa,
            "cena_robe_sa_PDV_om": (roba.cena_robe * (roba.stopa_PDVa * 0.01 + 1)),
            "kolicina": roba_racun.kolicina,
            "ukupna_cena_robe": roba_racun.ukupna_cena_robe       
        })

    racun.stavke_usluga = stavke_usluga
    racun.stavke_roba = stavke_roba


    avansni_racuni = (
        db.query(models.Racun)
        .filter(
            models.Racun.id_predracuna == racun.id_predracuna, 
            models.Racun.tip_izdatog_racuna =="Avans"
        )
        .all()
    )
    racun.avans = avansni_racuni

    user = db.query(models.UserRacun.id_user_fk).filter(models.UserRacun.id_racuna_fk == id).scalar()
    racun.user = db.query(models.User).filter(models.User.id_user == user).first()


    
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
        broj_racuna = "",
        datum_valute = racun.datum_valute,
     #   datum_prometa = racun.datum_prometa,
        valuta = racun.valuta,
        nacin_placanja = racun.nacin_placanja,
        broj_racuna_za_uplatu = racun.broj_racuna_za_uplatu,
        obaveznik_pdv = racun.obaveznik_pdv,
        status_racuna = racun.status_racuna,
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

        vrednost_avansa_20 = 0,
        vrednost_avansa_10 = 0,
        vrednost_avansa_0 = 0,
   
        tip_izdatog_racuna ="Racun",
        datum_izdavanja = datetime.utcnow(),

        id_firme_fk = racun.id_firme_fk,
        id_kupac_fk = racun.id_kupac_fk,
        id_korisnik_kreirao_fk = current_user.id_user
    )
    db.add(novi_racun)
    db.flush()  # da dobijemo ID računa

   # ukupna_osnovica = 0
    if racun.stavke_usluga:
        for stavka in racun.stavke_usluga:
        
            #cena_usluge = db.query(models.Usluga.cena_usluge).filter(models.Usluga.id_usluge == stavka.id_usluge_fk).scalar()
            usluga = db.query(models.Usluga).filter(models.Usluga.id_usluge == stavka.id_usluge_fk).first()

            if not usluga:
                raise HTTPException(status_code=404, detail=f"Usluga sa ID {stavka.id_usluge_fk} ne postoji.")

            # PROVERA: da li usluga pripada firmi sa racuna
            if usluga.id_firme_fk != novi_racun.id_firme_fk:
                raise HTTPException(
                    status_code=400,
                    detail=f"Usluga sa ID {usluga.id_usluge} nije dodeljena firmi sa ID {novi_racun.id_firme_fk}."
                )

            db.add(models.UslugaRacun(
                id_racuna_fk=novi_racun.id_racuna,
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
            novi_racun.ukupna_osnovica = novi_racun.ukupna_osnovica + stavka.kolicina * usluga.cena_usluge
            novi_racun.ukupna_pdv = novi_racun.ukupna_pdv + stavka.kolicina  * usluga.iznos_pdv_usluge
            novi_racun.ukupna_iznos = novi_racun.ukupna_iznos + stavka.kolicina * usluga.iznos_usluge_sa_pdv
            #ovo je cena sa PDV-om koji je unet samo ga nisam ispisao na racunu to bi verovatno trebalo

            if usluga.stopa_PDVa == 20:
                novi_racun.ukupna_osnovica_20 = novi_racun.ukupna_osnovica_20 + stavka.kolicina * usluga.cena_usluge
                novi_racun.ukupna_pdv_20 = novi_racun.ukupna_pdv_20 + (stavka.kolicina * usluga.iznos_pdv_usluge)
                novi_racun.ukupna_iznos_20 = novi_racun.ukupna_iznos_20 +  stavka.kolicina * usluga.iznos_usluge_sa_pdv
            elif usluga.stopa_PDVa == 10:
                novi_racun.ukupna_osnovica_10 = novi_racun.ukupna_osnovica_10 + stavka.kolicina * usluga.cena_usluge
                novi_racun.ukupna_pdv_10 = novi_racun.ukupna_pdv_10 + (stavka.kolicina * usluga.iznos_pdv_usluge)
                novi_racun.ukupna_iznos_10 = novi_racun.ukupna_iznos_10 +  stavka.kolicina * usluga.iznos_usluge_sa_pdv
            elif usluga.stopa_PDVa == 0:
                novi_racun.ukupna_osnovica_0 = novi_racun.ukupna_osnovica_0 + stavka.kolicina * usluga.cena_usluge

    if racun.stavke_roba:
        for stavka in racun.stavke_roba:
            
            #cena_robe = db.query(models.Roba.cena_robe).filter(models.Roba.id_robe == stavka.id_robe_fk).scalar()
            roba = db.query(models.Roba).filter(models.Roba.id_robe == stavka.id_robe_fk).first()

            if not roba:
                raise HTTPException(status_code=404, detail=f"Roba sa ID {stavka.id_robe_fk} ne postoji.")

            # PROVERA: da li usluga pripada firmi sa racuna
            if usluga.id_firme_fk != novi_racun.id_firme_fk:
                raise HTTPException(
                    status_code=400,
                    detail=f"Roba sa ID {roba.id_robe} nije dodeljena firmi sa ID {novi_racun.id_firme_fk}."
                )

            db.add(models.RobaRacun(
                id_racuna_fk=novi_racun.id_racuna,
                id_robe_fk=stavka.id_robe_fk,

                kolicina=stavka.kolicina,
                osnovica_pdv_robe = roba.cena_robe,
                stopa_PDVa = roba.stopa_PDVa,

                iznos_pdv_robe = roba.iznos_pdv_robe,

                #ukupna_cena_robe=stavka.kolicina * roba.cena_robe * (roba.stopa_PDVa * 0.01 + 1),
                ukupna_cena_robe=stavka.kolicina * roba.iznos_robe_sa_pdv,

                datum_kreiranja = datetime.utcnow()
            ))
            novi_racun.ukupna_osnovica = novi_racun.ukupna_osnovica + stavka.kolicina * roba.cena_robe 
            novi_racun.ukupna_pdv = novi_racun.ukupna_pdv + stavka.kolicina * roba.iznos_pdv_robe
            novi_racun.ukupna_iznos = novi_racun.ukupna_iznos + stavka.kolicina * roba.iznos_robe_sa_pdv

            if roba.stopa_PDVa == 20:
                novi_racun.ukupna_osnovica_20 = novi_racun.ukupna_osnovica_20 + stavka.kolicina * roba.cena_robe
                novi_racun.ukupna_pdv_20 = novi_racun.ukupna_pdv_20 + (stavka.kolicina * roba.iznos_pdv_robe)
                novi_racun.ukupna_iznos_20 = novi_racun.ukupna_iznos_20 +  stavka.kolicina * roba.iznos_robe_sa_pdv
            elif roba.stopa_PDVa == 10:
                novi_racun.ukupna_osnovica_10 = novi_racun.ukupna_osnovica_10 + stavka.kolicina * roba.cena_robe
                novi_racun.ukupna_pdv_10 = novi_racun.ukupna_pdv_10 + (stavka.kolicina * roba.iznos_pdv_robe)
                novi_racun.ukupna_iznos_10 = novi_racun.ukupna_iznos_10 +  stavka.kolicina * roba.iznos_robe_sa_pdv
            elif roba.stopa_PDVa == 0:
                novi_racun.ukupna_osnovica_0 = novi_racun.ukupna_osnovica_0 + stavka.kolicina * roba.cena_robe


    userRacun = models.UserRacun(
        datum_kreiranja_racuna=datetime.utcnow(),
       # datum_izmene_racuna = racun.datum_izmene_racuna,
       # datum_izdavanja_racuna = racun.datum_izdavanja_racuna,
        Tip_izdatog_racuna = "Racun",
        id_user_fk = current_user.id_user,
        id_racuna_fk = novi_racun.id_racuna 
    )
    db.add(userRacun)

    novi_racun.broj_racuna = formatiraj_broj_racuna(novi_racun.id_racuna, "racun")

    #novi_racun.ukupna_osnovica = ukupna_osnovica
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
    #postojeci_racun.broj_racuna = racun.broj_racuna
    #postojeci_racun.ukupna_cena_racuna = racun.ukupna_cena_racuna
    postojeci_racun.valuta = racun.valuta
    postojeci_racun.obaveznik_pdv = racun.obaveznik_pdv
    postojeci_racun.id_firme_fk = racun.id_firme_fk
    postojeci_racun.id_kupac_fk = racun.id_kupac_fk

    postojeci_racun.datum_valute = racun.datum_valute
   # postojeci_racun.datum_prometa = racun.datum_prometa
    postojeci_racun.nacin_placanja = racun.nacin_placanja
    postojeci_racun.broj_racuna_za_uplatu = racun.broj_racuna_za_uplatu


    # OBRIŠI POSTOJEĆE STAVKE
    db.query(models.UslugaRacun).filter(models.UslugaRacun.id_racuna_fk == id).delete()
    db.query(models.RobaRacun).filter(models.RobaRacun.id_racuna_fk == id).delete()

    ukupna_osnovica = 0

    # DODAJ NOVE STAVKE USLUGA
    for stavka in racun.stavke_usluga:
        
        #cena_usluge = db.query(models.Usluga.cena_usluge).filter(models.Usluga.id_usluge == stavka.id_usluge_fk).scalar()
        usluga = db.query(models.Usluga).filter(models.Usluga.id_usluge == stavka.id_usluge_fk).first()
        
        if not usluga:
                raise HTTPException(status_code=404, detail=f"Usluga sa ID {stavka.id_usluge_fk} ne postoji.")

        # PROVERA: da li usluga pripada firmi sa racuna
        if usluga.id_firme_fk != postojeci_racun.id_firme_fk:
            raise HTTPException(
                status_code=400,
                detail=f"Usluga sa ID {usluga.id_usluge} nije dodeljena firmi sa ID {postojeci_racun.id_firme_fk}."
            )


        db.add(models.UslugaRacun(
            id_racuna_fk=id,
            id_usluge_fk=stavka.id_usluge_fk,
            kolicina=stavka.kolicina,
            osnovica_pdv_usluge = usluga.cena_usluge,
            stopa_PDVa = usluga.stopa_PDVa,
            iznos_pdv_usluge = usluga.iznos_pdv_usluge,
            ukupna_cena_usluge= stavka.kolicina * usluga.cena_usluge * (usluga.stopa_PDVa * 0.01 + 1),
            datum_kreiranja = datetime.utcnow()
        ))
        ukupna_osnovica = ukupna_osnovica + (stavka.kolicina * usluga.cena_usluge * (usluga.stopa_PDVa * 0.01 +1))
    

    # DODAJ NOVE STAVKE ROBA
    for stavka in racun.stavke_roba:

        #cena_robe = db.query(models.Roba.cena_robe).filter(models.Roba.id_robe == stavka.id_robe_fk).scalar()
        roba = db.query(models.Roba).filter(models.Roba.id_robe == stavka.id_robe_fk).first()
       
        if not roba:
            raise HTTPException(status_code=404, detail=f"Roba sa ID {stavka.id_robe_fk} ne postoji.")

        # PROVERA: da li usluga pripada firmi sa racuna
        if usluga.id_firme_fk != postojeci_racun.id_firme_fk:
            raise HTTPException(
                status_code=400,
                detail=f"Roba sa ID {roba.id_robe} nije dodeljena firmi sa ID {postojeci_racun.id_firme_fk}."
            )

        db.add(models.RobaRacun(
            id_racuna_fk=id,
            id_robe_fk=stavka.id_robe_fk,
            kolicina=stavka.kolicina,
            osnovica_pdv_robe = roba.cena_robe,
            stopa_PDVa = roba.stopa_PDVa,
            iznos_pdv_robe = roba.iznos_pdv_robe,
            ukupna_cena_robe=stavka.kolicina * roba.cena_robe * (roba.stopa_PDVa * 0.01 + 1),
            datum_kreiranja = datetime.utcnow()
        ))
        ukupna_osnovica = ukupna_osnovica + (stavka.kolicina * roba.cena_robe * (roba.stopa_PDVa * 0.01 + 1))


    # Ažuriraj i datum izmene u userRacun tabeli
    user_racun = db.query(models.UserRacun).filter(models.UserRacun.id_racuna_fk == id).first()
    if user_racun:
        user_racun.datum_izmene_racuna = datetime.utcnow(),
        user_racun.Tip_izdatog_racuna = "Racun normalni izmenjen"

    postojeci_racun.ukupna_osnovica = ukupna_osnovica

    db.commit()
    db.refresh(postojeci_racun)

    return {"message": "Račun uspešno ažuriran", "id_racuna": postojeci_racun.id_racuna}


@router.delete("/racun/{id}", status_code=200)
def delete_racun(id: int, db: Session = Depends(get_db)):
    
    # Proveri da li račun postoji
    racun = db.query(models.Racun).filter(models.Racun.id_racuna == id).first()
   
    if racun.tip_izdatog_racuna != "Racun":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"U ovoj sekciji možete brisati samo racune."
        )

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


@router.post("/racun/predracun", status_code=201)
def create_racun_predracun(racun: racun_schemas.CreateRacunPredracun, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    #Uzimanje predracuna
    predracun = db.query(models.Racun).filter(
        models.Racun.id_racuna == racun.id_predracuna,
        models.Racun.tip_izdatog_racuna == "Predracun"
    ).first()

    if not predracun:
        raise HTTPException (status_code= status.HTTP_404_NOT_FOUND, detail="Predracun nije pronadjen.")


    novi_racun = models.Racun(
        broj_racuna = "",
        datum_valute = predracun.datum_valute,
      #  datum_prometa = predracun.datum_prometa,
        valuta = predracun.valuta,
        nacin_placanja = predracun.nacin_placanja,
        broj_racuna_za_uplatu = predracun.broj_racuna_za_uplatu,
        obaveznik_pdv = predracun.obaveznik_pdv,
        status_racuna = predracun.status_racuna,
       
        ukupna_osnovica = predracun.ukupna_osnovica, 
        ukupna_pdv = predracun.ukupna_pdv,
        ukupna_iznos = predracun.ukupna_iznos,  

        ukupna_osnovica_20 = predracun.ukupna_osnovica_20,
        ukupna_osnovica_10 = predracun.ukupna_osnovica_10,
        ukupna_osnovica_0 = predracun.ukupna_osnovica_0,
        ukupna_pdv_20 = predracun.ukupna_pdv_20,
        ukupna_pdv_10 = predracun.ukupna_pdv_10,
        ukupna_iznos_20 = predracun.ukupna_iznos_20,
        ukupna_iznos_10 = predracun.ukupna_iznos_10,

        vrednost_avansa_20 = 0,
        vrednost_avansa_10 = 0,
        vrednost_avansa_0 = 0,
   
        tip_izdatog_racuna ="Racun",
        datum_izdavanja = datetime.utcnow(),

        id_firme_fk = predracun.id_firme_fk,
        id_kupac_fk = predracun.id_kupac_fk,
        id_predracuna = racun.id_predracuna,
        id_korisnik_kreirao_fk = current_user.id_user
    )
    db.add(novi_racun)
    db.flush()  # da dobijemo ID računa


    #Sabiranje već unesenih avansnih vrednosti za taj predracun
    zbir_avansa = db.query(
        func.coalesce(func.sum(models.Racun.vrednost_avansa_20), 0).label("suma20"),
        func.coalesce(func.sum(models.Racun.vrednost_avansa_10), 0).label("suma10"),
        func.coalesce(func.sum(models.Racun.vrednost_avansa_0), 0).label("suma0")
    ).filter(
        models.Racun.id_predracuna == racun.id_predracuna,
        models.Racun.tip_izdatog_racuna == "Avans"
    ).first()


    novi_racun.ukupna_iznos = predracun.ukupna_iznos - zbir_avansa.suma20 - zbir_avansa.suma10 - zbir_avansa.suma0

    novi_racun.vrednost_avansa_20 = zbir_avansa.suma20
    novi_racun.vrednost_avansa_10 = zbir_avansa.suma10
    novi_racun.vrednost_avansa_0 = zbir_avansa.suma0


    novi_racun.broj_racuna = formatiraj_broj_racuna(novi_racun.id_racuna, "racun")

    userRacun = models.UserRacun(
        datum_kreiranja_racuna=datetime.utcnow(),
       # datum_izmene_racuna = racun.datum_izmene_racuna,
       # datum_izdavanja_racuna = racun.datum_izdavanja_racuna,
        Tip_izdatog_racuna = "Racun",
        id_user_fk = current_user.id_user,
        id_racuna_fk = novi_racun.id_racuna 
    )
    db.add(userRacun)

    db.commit()
    db.refresh(novi_racun)

    return {"message": "Račun uspešno kreiran", "id_racuna": novi_racun.id_racuna}