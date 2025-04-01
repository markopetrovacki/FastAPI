from fastapi import FastAPI
from . import models
from .database import engine
from .routers import post, user, auth, vote
from .config import settings


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

    
#while True:
#    try:
#        conn = psycopg2.connect(host='localhost', database='fastApi', user='postgres', password='postgres', cursor_factory=RealDictCursor)
#        cursor = conn.cursor()
#        print("Database connection was succesfull!")
#        break
#    except Exception as error:
#        print("Connecting to database failed")
#        print("Error: ",  error)
#        time.sleep(2)


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


