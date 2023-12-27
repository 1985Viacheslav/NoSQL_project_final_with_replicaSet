from dependencies import router, SessionData, backend, cookie, verifier
from fastapi import Response, Depends

from uuid import UUID, uuid4

@router.post("/create_session/{username}")
async def create_session(username: str, response: Response):
    session_id = uuid4()
    data = SessionData(username=username)
    await backend.create(session_id, data)
    cookie.attach_to_response(response, session_id)
    return f"Сессия создана для {username}"

@router.get("/whoami", dependencies=[Depends(cookie)])
async def whoami(session_data: SessionData = Depends(verifier)):
    return session_data

@router.post("/delete_session")
async def delete_session(response: Response, session_id: UUID = Depends(cookie)):
    await backend.delete(session_id)
    cookie.delete_from_response(response)
    return "Сессия удалена"