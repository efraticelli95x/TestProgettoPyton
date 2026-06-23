from datetime import date
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
def registra_utente(utente: AnagraficaUtente):
    eta_calcolata = date.today().year - utente.anno_nascita
    return {
        "messaggio": f"Ciao {utente.nome}!",
        "eta": eta_calcolata,
        "status": "success",
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