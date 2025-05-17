from datetime import datetime, date
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func 
from typing import List, Optional
from app import models, schemas, utils, oauth2
from ..schemas_model import  user_racun_schemas, avans_schemas
from ..database import get_db

router = APIRouter(
    tags = ['Avans']
)

def formatiraj_broj_racuna(redni_broj: int, tip: str = "") -> str:
    godina = date.today().year
    broj = f"{redni_broj:04d}"  # dodaje vodeće nule: 1 → 0001
    if tip.lower() == "avans":
        return f"{broj}-A/{godina}"
    return f"{broj}/{godina}"


@router.get("/avans", response_model=List[avans_schemas.GetAvans])
async def get_avans(db: Session = Depends(get_db)):

    result = db.query(models.Racun).filter(models.Racun.tip_izdatog_racuna == "Avans").all()
    
    return result


@router.get("/avans/{id}", response_model=avans_schemas.GetAvansID)
async def get_avans_id(id: int, db: Session = Depends(get_db)):

    avans = db.query(models.Racun).filter(models.Racun.id_racuna == id).first()

    if avans.tip_izdatog_racuna != "Avans":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avansni racun nije pronađen."
        )

    return avans


@router.post("/avans", status_code=201)
def create_avans(avans: avans_schemas.CreateAvans, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    #Uzimanje predracuna
    predracun = db.query(models.Racun).filter(
        models.Racun.id_racuna == avans.id_predracuna,
        models.Racun.tip_izdatog_racuna == "Predracun"
    ).first()

    if not predracun:
        raise HTTPException (status_code= status.HTTP_404_NOT_FOUND, detail="Predracun nije pronadjen.")

    #Sabiranje već unesenih avansnih vrednosti za taj predracun
    zbir_avansa = db.query(
        func.coalesce(func.sum(models.Racun.vrednost_avansa_20), 0).label("suma20"),
        func.coalesce(func.sum(models.Racun.vrednost_avansa_10), 0).label("suma10"),
        func.coalesce(func.sum(models.Racun.vrednost_avansa_0), 0).label("suma0")
    ).filter(
        models.Racun.id_predracuna == avans.id_predracuna,
        models.Racun.tip_izdatog_racuna == "Avans"
    ).first()
    
    suma20 = zbir_avansa.suma20 + avans.vrednost_avansa_20
    suma10 = zbir_avansa.suma10 + avans.vrednost_avansa_10
    suma0 = zbir_avansa.suma0 + avans.vrednost_avansa_0

    if suma20 > (predracun.ukupna_iznos_20 or 0) or \
       suma10 > (predracun.ukupna_iznos_10 or 0) or \
       suma0 > (predracun.ukupna_osnovica_0 or 0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ukupna vrednost avansnih računa ne može premašiti predračun."
        )


    # Kreiranje novog avansnog računa
    novi_avans = models.Racun(
       # **racun.dict()
        broj_racuna = "",
        poziv_na_broj = avans.poziv_na_broj,
        napomena_na_fakturi = avans.napomena_na_fakturi,
        
        vrednost_avansa_20 = avans.vrednost_avansa_20,
        vrednost_avansa_10 = avans.vrednost_avansa_10,
        vrednost_avansa_0= avans.vrednost_avansa_0,

        tip_izdatog_racuna ="Avans",
        datum_izdavanja = datetime.utcnow(),

        id_firme_fk = avans.id_firme_fk,
        id_kupac_fk = avans.id_kupac_fk,
        id_predracuna = avans.id_predracuna,
        id_korisnik_kreirao_fk = current_user.id_user
    )
    db.add(novi_avans)
    db.flush()  # da dobijemo ID računa

    novi_avans.broj_racuna = formatiraj_broj_racuna(novi_avans.id_racuna, "avans")

    db.commit()
    db.refresh(novi_avans)

    return {"message": "Avansni račun uspešno kreiran", "id_racuna": novi_avans.id_racuna}



@router.put("/avans/{id}", status_code=200)
def update_avans(id: int, avans: avans_schemas.CreateAvans, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # Pronađi postojeći predracun
    postojeci_avans = db.query(models.Racun).filter(models.Racun.id_racuna == id).first()

    if postojeci_avans.tip_izdatog_racuna != "Avans":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avansni račun nije pronađen."
        )

    if not postojeci_avans:
        raise HTTPException(status_code=404, detail="Predračun nije pronađen.")


    #Uzimanje predracuna
    predracun = db.query(models.Racun).filter(
        models.Racun.id_racuna == avans.id_predracuna,
        models.Racun.tip_izdatog_racuna == "Predracun"
    ).first()

    if not predracun:
        raise HTTPException (status_code= status.HTTP_404_NOT_FOUND, detail="Predracun nije pronadjen.")

    #Sabiranje već unesenih avansnih vrednosti za taj predracun
    zbir_avansa = db.query(
        func.coalesce(func.sum(models.Racun.vrednost_avansa_20), 0).label("suma20"),
        func.coalesce(func.sum(models.Racun.vrednost_avansa_10), 0).label("suma10"),
        func.coalesce(func.sum(models.Racun.vrednost_avansa_0), 0).label("suma0")
    ).filter(
        models.Racun.id_predracuna == avans.id_predracuna,
        models.Racun.tip_izdatog_racuna == "Avans"
    ).first()
    
    suma20 = zbir_avansa.suma20 + avans.vrednost_avansa_20
    suma10 = zbir_avansa.suma10 + avans.vrednost_avansa_10
    suma0 = zbir_avansa.suma0 + avans.vrednost_avansa_0

    if suma20 > (predracun.ukupna_iznos_20 or 0) or \
       suma10 > (predracun.ukupna_iznos_10 or 0) or \
       suma0 > (predracun.ukupna_osnovica_0 or 0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ukupna vrednost avansnih računa ne može premašiti predračun."
        )


    #postojeci_avans.broj_racuna = avans.broj_racuna,
    postojeci_avans.poziv_na_broj = avans.poziv_na_broj,
    postojeci_avans.napomena_na_fakturi = avans.napomena_na_fakturi,
    
    postojeci_avans.vrednost_avansa_20 = avans.vrednost_avansa_20,
    postojeci_avans.vrednost_avansa_10 = avans.vrednost_avansa_10,
    postojeci_avans.vrednost_avansa_0= avans.vrednost_avansa_0,

    postojeci_avans.tip_izdatog_racuna ="Avans",
    postojeci_avans.datum_izdavanja = datetime.utcnow(),

    postojeci_avans.id_firme_fk = avans.id_firme_fk,
    postojeci_avans.id_kupac_fk = avans.id_kupac_fk,
    postojeci_avans.id_predracuna = avans.id_predracuna,
    postojeci_avans.id_korisnik_kreirao_fk = current_user.id_user

    db.commit()
    db.refresh(postojeci_avans)

    return {"message": "Avansni račun je uspešno ažuriran", "id_racuna": postojeci_avans.id_racuna}


@router.delete("/avans/{id}", status_code=200)
def delete_avans(id: int, db: Session = Depends(get_db)):
    
    # Proveri da li račun postoji
    avans = db.query(models.Racun).filter(models.Racun.id_racuna == id).first()
   
    if avans.tip_izdatog_racuna != "Avans":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"U ovoj sekciji možete brisati samo avansne račune."
        )

    if not avans:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Avansni račun sa ID-jem {id} nije pronađen."
        )

    # Na kraju brišemo sam račun
    db.delete(avans)

    db.commit()

    return {"message": f"Avansni račun sa ID-jem {id} je uspešno obrisani."}



@router.get("/avans/predracun/{id_predracun}", response_model=avans_schemas.GetPredracunAvans)
async def get_avans_za_predracun(id_predracun: int, db: Session = Depends(get_db)):

    predracun = db.query(models.Racun).filter(models.Racun.id_racuna == id_predracun).first()

    avansni_racuni = (
        db.query(models.Racun)
        .filter(
            models.Racun.id_predracuna == id_predracun, 
            models.Racun.tip_izdatog_racuna =="Avans"
        )
        .all()
    )

    if not avansni_racuni:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nisu pronađeni avansni računi za dati predračun."
        )
    
    predracun.avans = avansni_racuni

    return predracun

