from datetime import date
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Cattura la stringa da Render (se avvii il file sul tuo PC, userà un file SQLite locale di scorta!)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sqlite_locale.db")

# Fix fondamentale: Render genera URL con 'postgres://', ma SQLAlchemy esige 'postgresql://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# 2. La Tabella SQL descritta come una normale classe Python
class UtenteDB(Base):
    __tablename__ = "utenti"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    anno_nascita = Column(Integer)


# Ordina a Postgres di creare la tabella 'utenti' se non esiste già
Base.metadata.create_all(bind=engine)


# 3. Il "Cameriere" che apre la connessione quando arriva l'utente e la chiude appena ha finito
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()

# Configurazione CORS per permettere le chiamate dal front-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permette l'accesso da qualsiasi origine per il test
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnagraficaUtente(BaseModel):
    nome: str
    anno_nascita: int

class CredenzialiLogin(BaseModel):
    username: str
    password: str

@app.post("/registra")
def registra_utente(utente: AnagraficaUtente, db: Session = Depends(get_db)):
    eta_calcolata = date.today().year - utente.anno_nascita
    nuovo_utente = UtenteDB(nome = utente.nome, anno_nascita = utente.anno_nascita)
    db.add(nuovo_utente)
    db.commit()
    db.refresh(nuovo_utente)

    return {
        "messaggio": f"Ciao {utente.nome}!",
        "eta": eta_calcolata,
        "status": "success",
        "id_database": nuovo_utente.id  # Ora possiamo restituire l'ID reale!
    }

@app.post("/login")
def login_utente(utente: CredenzialiLogin):
    if utente.username == "admin" and utente.password == "password":
        return {
            "messaggio": "Benvenuto!",
            "status": "success",
            "x-token": "token123",
        }
    else:
        return {
            "messaggio": "Username o password errati!",
            "status": "error",
        }


@app.get("/dati-protetti")
def get_dati_db(x_token: str = Header(None)):
    if x_token == "token123":
        return {
            "messaggio": "Accesso consentito!",
            "dati": ["dato1", "dato2", "dati3"],
            "status": "success",
        }
    else:
        raise HTTPException(
            status_code=401, detail="Braccialetto mancante o contraffatto!"
        )