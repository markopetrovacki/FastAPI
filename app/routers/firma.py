from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func 
from typing import List, Optional
from app import models, schemas, utils, oauth2
from ..schemas_model import firma_schemas
from ..database import get_db

router = APIRouter(
    tags = ['Firma']
)



@router.get("/firma", response_model=List[firma_schemas.GetFirma])
async def get_firma(db: Session = Depends(get_db)):

    result = db.query(models.Firma).all()
    
    return result



@router.get("/firma/{id}", response_model=firma_schemas.GetFirmaId)
async def get_firma_id(id: int, db: Session = Depends(get_db)):

    firma = db.query(models.Firma).filter(models.Firma.id_firme == id).first()

    users = db.query(models.UserFirma).filter(models.UserFirma.id_firme_fk == id).all()

    # Na osnovu id_user_fk uzmi sve korisnike iz tabele User
    korisnici = []
    for veza in users:
        korisnik = db.query(models.User).filter(models.User.id_user == veza.id_user_fk).first()
        if korisnik:
            korisnici.append(korisnik)

    # Dodeli korisnike firmi (ovo radi jer FastAPI koristi Pydantic model)
    firma.user = korisnici

    if not firma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= f"firma sa id-jem: {id} nije pronadjena")
    
    return firma



@router.post("/firma", status_code=status.HTTP_201_CREATED, response_model=firma_schemas.CreateFirma)
async def create_firma(firma: firma_schemas.CreateFirma, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

   # new_firma = models.Firma(id_user_fk = current_user.id_user, **firma.dict())
    new_firma = models.Firma(**firma.dict())
    
    db.add(new_firma)
    db.commit()
    db.refresh(new_firma)
   
    new_userFirma = models.UserFirma(id_user_fk= current_user.id_user, id_firme_fk = new_firma.id_firme)
    db.add(new_userFirma)
    db.commit()
    db.refresh(new_userFirma)
    
    return new_firma



@router.put("/firma/{id}", response_model=firma_schemas.GetFirma)
def update_firma(id:int, updated_firma:firma_schemas.CreateFirma, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    firma_query = db.query(models.Firma).filter(models.Firma.id_firme == id)
    firma = firma_query.first()

    if firma == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"firma sa id-jem: {id} nije pronadjena")
    
   # if firma.id_user_fk != current_user.id_user:
   #      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
   #                         detail="Not Authorized to perform requested action")

    firma_query.update(updated_firma.dict(), synchronize_session=False)
    db.commit() 

    return firma_query.first()



@router.delete("/firma/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_firma(id: int, db: Session = Depends(get_db)):

    firma_query = db.query(models.Firma).filter(models.Firma.id_firme == id)

    firma = firma_query.first()

    if firma == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} dose not exist")

  #  if post.owner_id != current_user.id_user:
  #       raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
  #                          detail="Not Authorized to perform requested action")


  # ovoj deo brise sve entitete u tabeli userFirma is ID-jem firme koja se brise
    db.query(models.UserFirma).filter(models.UserFirma.id_firme_fk == id).delete(synchronize_session=False)

    firma_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)



@router.post("/firma/user", status_code=status.HTTP_201_CREATED)
def dodaj_korisnika_u_firmu(payload: firma_schemas.UserFirmaCreate, db: Session = Depends(get_db)):
    # Pronađi korisnika po imenu, prezimenu i emailu
    korisnik = db.query(models.User).filter(
        models.User.ime_korisnika == payload.ime,
        models.User.prezime_korisnika == payload.prezime,
        models.User.email == payload.email
    ).first()

    if not korisnik:
        raise HTTPException(status_code=404, detail="Korisnik nije pronađen")

    # Pronađi firmu po nazivu i matičnom broju
    firma = db.query(models.Firma).filter(
        models.Firma.naziv == payload.naziv_firme,
        models.Firma.maticni_broj == payload.maticni_broj
    ).first()

    if not firma:
        raise HTTPException(status_code=404, detail="Firma nije pronađena")

    # Proveri da li su već povezani
   # if korisnik in firma.korisnici:
   #     raise HTTPException(status_code=400, detail="Korisnik je već član firme")

    # Poveži korisnika sa firmom
   # firma.korisnici.append(korisnik)
   # db.commit()

    new_userFirma = models.UserFirma(id_user_fk= korisnik.id_user, id_firme_fk = firma.id_firme)
    db.add(new_userFirma)
    db.commit()
    db.refresh(new_userFirma)

    return {"message": f"Korisnik {korisnik.email} uspešno dodat firmi {firma.naziv}"}