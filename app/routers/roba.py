from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func 
from typing import List, Optional
from app import models, schemas, utils, oauth2
from ..schemas_model import roba_schemas
from ..database import get_db

router = APIRouter(
    tags = ['Roba']
)



@router.get("/roba", response_model=List[roba_schemas.GetRoba])
async def get_roba(db: Session = Depends(get_db)):

    result = db.query(models.Roba).all()
    
    return result



@router.get("/roba/{id}", response_model = roba_schemas.GetRoba)
async def get_roba_id(id: int, db: Session = Depends(get_db)):

    roba = db.query(models.Roba).filter(models.Roba.id_robe == id).first()

    if not roba:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= f"Roba sa id-jem: {id} nije pronadjena")
    
    return roba



@router.post("/roba", status_code=status.HTTP_201_CREATED, response_model = roba_schemas.GetRoba)
async def create_roba(roba:  roba_schemas.CreateRoba, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    new_roba = models.Roba(
        **roba.dict(),
        iznos_pdv_robe = roba.cena_robe * roba.stopa_PDVa * 0.01,
        iznos_robe_sa_pdv = roba.cena_robe * (roba.stopa_PDVa * 0.01 + 1)
        )
    
    db.add(new_roba)
    db.commit()
    db.refresh(new_roba)
    
    return new_roba



@router.put("/roba/{id}", response_model = roba_schemas.GetRoba)
def update_roba(id:int, updated_roba: roba_schemas.CreateRoba, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    roba_query = db.query(models.Roba).filter(models.Roba.id_robe == id)
    roba = roba_query.first()

    if roba == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Roba sa id-jem: {id} nije pronadjena")
    
   # if firma.id_user_fk != current_user.id_user:
   #      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
   #                         detail="Not Authorized to perform requested action")

    roba_query.update(
        updated_roba.dict(),
        iznos_pdv_robe = roba.cena_robe * roba.stopa_PDVa * 0.01,
        iznos_robe_sa_pdv = roba.cena_robe * (roba.stopa_PDVa * 0.01 + 1),
        synchronize_session=False
        )
    db.commit() 

    return roba_query.first()



@router.delete("/roba/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_roba(id: int, db: Session = Depends(get_db)):

    roba_query = db.query(models.Roba).filter(models.Roba.id_robe == id)

    roba = roba_query.first()

    if roba == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"roba with id: {id} dose not exist")

  #  if post.owner_id != current_user.id_user:
  #       raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
  #                          detail="Not Authorized to perform requested action")

    roba_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)



@router.get("/roba/firma/{id_firme}", response_model = List[roba_schemas.GetRoba])
async def get_roba_firma(id_firme: int, db: Session = Depends(get_db)):

    roba = db.query(models.Roba).filter(models.Roba.id_firme_fk == id_firme).all()

    if not roba:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= f"Roba sa id-jem firme: {id_firme} nije pronadjena")
    
    return roba