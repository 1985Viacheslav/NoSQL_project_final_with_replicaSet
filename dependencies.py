from pymongo import MongoClient
from elasticsearch import Elasticsearch
from fastapi import APIRouter, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.session_verifier import SessionVerifier
from uuid import UUID
import logging
from pydantic import BaseModel

DATABASE_RESET = True

MONGO_URL = "mongodb://mongo1:27017,mongo2:27018,mongo3:27019/?replicaSet=rs0"
MONGO_DB = "booking_db"

def get_db():
    client = MongoClient(MONGO_URL)
    return client[MONGO_DB]


es = Elasticsearch(["http://elasticsearch:9200"])

def create_es_index(es: Elasticsearch):
    if not es.indices.exists(index="rooms"):
        es.indices.create(index="rooms", body={
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1
            },
            "mappings": {
                "properties": {
                    "name": {"type": "text"},
                    "neighbourhood": {"type": "text"},
                    "latitude": {"type": "float"},
                    "longitude": {"type": "float"},
                    "room_type": {"type": "text"},
                    "price": {"type": "float"}
                }
            }
        })

    if not es.indices.exists(index="clients"):
        es.indices.create(index="clients", body={
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1
            },
            "mappings": {
                "properties": {
                    "name": { "type": "text" },
                }
            }
        })

create_es_index(es)

def get_es():
    global es
    return es

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


class SessionData(BaseModel):
    username: str

cookie_params = CookieParameters()
cookie = SessionCookie(
    cookie_name="session_cookie",
    identifier="session_verifier",
    auto_error=True,
    secret_key="YOUR_SECRET_KEY", 
    cookie_params=cookie_params,
)

backend = InMemoryBackend[UUID, SessionData]()

class BasicVerifier(SessionVerifier[UUID, SessionData]):
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: InMemoryBackend[UUID, SessionData],
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    def verify_session(self, model: SessionData) -> bool:
        """If the session exists, it is valid"""
        return True

verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=True,
    backend=backend,
    auth_http_exception=HTTPException(status_code=403, detail="invalid session"),
)