from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles

from pymongo import MongoClient
import uvicorn

from routes import booking, search, users, login
from dependencies import get_db, MONGO_URL, templates, SessionData, cookie, verifier
from uuid import UUID

app = FastAPI()

app.include_router(booking.router)
app.include_router(search.router)
app.include_router(users.router)
app.include_router(login.router)

app.mount("/static", StaticFiles(directory="static"), name="static")

client = MongoClient(MONGO_URL)

# def get_current_user(session_data: SessionData = Depends(verifier)):
#     if not session_data:
#         raise HTTPException(status_code=307, detail="Not logged in", headers={"Location": "/login"})
#     return session_data

@app.get("/")
async def main(request: Request):
# async def main(request: Request, session_data: SessionData = Depends(get_current_user)):
    # username = session_data.username
    username = 'Admin'

    collections_empty = False
    try:
        client.admin.command('ping')
        db_status = "Соединение с базой данных установлено"
        collections_empty = not list(get_db().list_collection_names())
        if collections_empty:
            db_status += "\nВнимание: Таблицы для работы отсутствуют или пусты"
    except Exception as e:
        db_status = f"Ошибка соединения с базой данных: {e}"

    return templates.TemplateResponse("index.html", {
        "request": request,
        "db_status": db_status,
        "collections_empty": collections_empty,
        "username": username
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
