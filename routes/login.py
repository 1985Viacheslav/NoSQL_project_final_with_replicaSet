from fastapi import FastAPI, Request, HTTPException, Form, Depends, Response
from fastapi.responses import RedirectResponse
from uuid import uuid4

from dependencies import get_es, router, templates, cookie, SessionData, verifier, backend
from uuid import UUID

@router.get("/login/")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login/")
async def login_post(request: Request, response: Response, username: str = Form(...)):
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")
    
    # Создаем новую сессию
    session_id = uuid4()
    session_data = SessionData(username=username)
    await backend.create(session_id, session_data)
    cookie.attach_to_response(response, session_id)

    return RedirectResponse(url="/", status_code=303)

@router.get("/whoami", dependencies=[Depends(cookie)])
async def whoami(session_data: SessionData = Depends(verifier)):
    if session_data:
        return {"username": session_data.username}
    return {"username": "Аноним"}

@router.post("/delete_session")
async def delete_session(response: Response, session_id: UUID = Depends(cookie)):
    await backend.delete(session_id)
    cookie.delete_from_response(response)
    return RedirectResponse(url="/", status_code=303)

