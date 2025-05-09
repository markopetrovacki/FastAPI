from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from app import models, schemas, utils
from ..database import get_db
from ..schemas_model import user_schemas


router = APIRouter(
    tags = ['Users']
)



@router.get('/users/{id}', response_model=user_schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    
    user = db.query(models.User).filter(models.User.id_user == id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail = f"User with id: {id} dose not exist")
    
    return user


@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=user_schemas.UserOut)
def create_user(user: user_schemas.UserCreate, db: Session = Depends(get_db)):

    #hash the password - user.password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
