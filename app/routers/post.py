from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app import models, schemas, utils, oauth2
from ..database import get_db


router = APIRouter(
    tags = ['Posts']
)



@router.get("/posts", response_model=List[schemas.PostOut])
async def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user),
                    limit: int = 20, skip: int = 0, search: Optional[str] = ""):
 
    #cursor.execute("""SELECT * FROM posts """)
    #posts = cursor.fetchall()

   # posts = db.query(models.Post).all()
    #posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter = True).group_by(models.Post.id).filter(
            models.Post.title.contains(search)).limit(limit).offset(skip).all()   
    
    print(results)

    return results


@router.get("/posts/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    #cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id),))
    #post = cursor.fetchone()

    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} was not found")
      #  response.status_code = status.HTTP_404_NOT_FOUND
      #  return{'message': f"post with id: {id} was not found"}
    return post


@router.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

   # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
   #                (post.title, post.content, post.published))

   # new_post = cursor.fetchone()
   # conn.commit()

    
    #new_post = models.Post(title=post.title, content=post.content, published = post.published)
    ### **post.dict() - menja ovaj kod iznad odnosno sam uzima vrednosti koje prosledjuje korisnik!!!!!!!!!!!
    print(current_user.id)
    new_post = models.Post(owner_id = current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.put("/posts/{id}", response_model=schemas.Post)
def update_post(id:int, updated_post:schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    #cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """, 
    #               (post.title, post.content, post.published, str(id)))
    
    #updated_post = cursor.fetchone()
    #conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} dose not exist")
    
    if post.owner_id != current_user.id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not Authorized to perform requested action")

    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit() 

    return post_query.first()


@router.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    #cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, (str(id),))
    #deleted_post = cursor.fetchone()
    #conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} dose not exist")

    if post.owner_id != current_user.id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not Authorized to perform requested action")


    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


