from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func 
from typing import List, Optional
from app import models, schemas, utils, oauth2
from ..schemas_model import usluga_schemas
from ..database import get_db

router = APIRouter(
    tags = ['Usluga']
)



@router.get("/usluga", response_model=List[usluga_schemas.GetUsluga])
async def get_usluga(db: Session = Depends(get_db)):

    result = db.query(models.Usluga).all()
    
    return result



@router.get("/usluga/{id}", response_model = usluga_schemas.GetUsluga)
async def get_usluga_id(id: int, db: Session = Depends(get_db)):

    usluga = db.query(models.Usluga).filter(models.Usluga.id_usluge == id).first()

    if not usluga:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= f"Usluga sa id-jem: {id} nije pronadjena")
    
    return usluga



@router.post("/usluga", status_code=status.HTTP_201_CREATED, response_model = usluga_schemas.GetUsluga)
async def create_usluga(usluga: usluga_schemas.GetUsluga, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    new_usluga = models.Usluga(**usluga.dict())
    
    db.add(new_usluga)
    db.commit()
    db.refresh(new_usluga)
    
    return new_usluga



@router.put("/usluga/{id}", response_model = usluga_schemas.GetUsluga)
def update_usluga(id:int, updated_usluga: usluga_schemas.GetUsluga, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    usluga_query = db.query(models.Usluga).filter(models.Usluga.id_usluge == id)
    usluga = usluga_query.first()

    if usluga == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Usluga sa id-jem: {id} nije pronadjena")
    
   # if firma.id_user_fk != current_user.id_user:
   #      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
   #                         detail="Not Authorized to perform requested action")

    usluga_query.update(updated_usluga.dict(), synchronize_session=False)
    db.commit() 

    return usluga_query.first()



@router.delete("/usluga/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usluga(id: int, db: Session = Depends(get_db)):

    usluga_query = db.query(models.Usluga).filter(models.Usluga.id_usluge == id)

    usluga = usluga_query.first()

    if usluga == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Usluga with id: {id} dose not exist")

  #  if post.owner_id != current_user.id_user:
  #       raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
  #                          detail="Not Authorized to perform requested action")

    usluga_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

