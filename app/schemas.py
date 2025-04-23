from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass



class UserOut(BaseModel):
    id_user: int
    email: EmailStr
    datum_kreiranja_naloga: datetime

    class Config:
        orm_model = True


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    class Config:
        orm_model = True


class PostOut(BaseModel):
    Post: Post
    votes: int

    class Config:
        orm_model = True



class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    #id: Optional[str] = None
    id: Optional[int] = None


class Vote(BaseModel):
    post_id: int
    #dir: conint(le=1) 
    #dir: int = Field(..., le=1)
    dir: int