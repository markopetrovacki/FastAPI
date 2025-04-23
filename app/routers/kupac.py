from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func 
from typing import List, Optional
from app import models, schemas, utils, oauth2
from ..schemas_model import kupac_schemas
from ..database import get_db

router = APIRouter(
    tags = ['Kupac']
)



@router.get("/kupac", response_model=List[kupac_schemas.GetKupac])
async def get_kupac(db: Session = Depends(get_db)):

    result = db.query(models.Kupac).all()
    
    return result



@router.get("/kupac/{id}", response_model = kupac_schemas.GetKupac)
async def get_kupac_id(id: int, db: Session = Depends(get_db)):

    kupac = db.query(models.Kupac).filter(models.Kupac.id_kupac == id).first()

    if not kupac:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= f"Kupac sa id-jem: {id} nije pronadjena")
    
    return kupac



@router.post("/kupac", status_code=status.HTTP_201_CREATED, response_model = kupac_schemas.GetKupac)
async def create_kupac(kupac:  kupac_schemas.GetKupac, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    new_kupac = models.Kupac(**kupac.dict())
    
    db.add(new_kupac)
    db.commit()
    db.refresh(new_kupac)
    
    return new_kupac



@router.put("/kupac/{id}", response_model = kupac_schemas.GetKupac)
def update_kupac(id:int, updated_kupac:kupac_schemas.GetKupac, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    kupac_query = db.query(models.Kupac).filter(models.Kupac.id_kupac == id)
    kupac = kupac_query.first()

    if kupac == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"kupac sa id-jem: {id} nije pronadjena")
    
   # if firma.id_user_fk != current_user.id_user:
   #      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
   #                         detail="Not Authorized to perform requested action")

    kupac_query.update(updated_kupac.dict(), synchronize_session=False)
    db.commit() 

    return kupac_query.first()



@router.delete("/kupac/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_kupac(id: int, db: Session = Depends(get_db)):

    kupac_query = db.query(models.Kupac).filter(models.Kupac.id_kupac == id)

    kupac = kupac_query.first()

    if kupac == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} dose not exist")

  #  if post.owner_id != current_user.id_user:
  #       raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
  #                          detail="Not Authorized to perform requested action")

    kupac_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
