from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine
from .routers import post, user, auth, vote, firma, roba, usluga, racun, kupac
from .config import settings


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
   # allow_origins=["https://mojfrontend.netlify.app"],  # ili ["*"] za   mozes da dodas i dva servisa npr google i youtube
   #OVO JE KADA NAMESTIS FRONTEND DA DODAS NJEGOVU PUDANJU DA BI MOGLI NESMETANO DA SALJU API ZAHTEVE INACE BEZ TOGA NE BI MOGLI
   # OVO NEMA VEZE SA CLOUDOM DA NA ISTOM CLOUDU MOGU DA LOMUNICIRAJU VEĆ SA NJIHOVIM URL-om NA KOJEM SE POKRECU 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
    
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


#app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
#app.include_router(vote.router)
app.include_router(firma.router)
app.include_router(kupac.router)
app.include_router(roba.router)
app.include_router(usluga.router)
app.include_router(racun.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


