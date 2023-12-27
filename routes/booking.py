from fastapi import Request, Form, HTTPException, Depends
from fastapi.responses import RedirectResponse
from bson import ObjectId
from bson.errors import InvalidId
from uuid import UUID
import time

from models import Booking

from hazelcast_manager import get_hazelcast_client, lock_room, unlock_room
from dependencies import logger, router, templates, get_db, get_es

@router.get("/booking/")
async def booking_form(request: Request):
# async def booking_form(request: Request, session_id: UUID = Depends(cookie), session_data: SessionData = Depends(verifier)):
    # username = session_data.username if session_data else None
    username = 'Admin'
    return templates.TemplateResponse("booking.html", {
        "request": request,
        "username": username
    })


@router.post("/booking/")
async def create_booking(request: Request, name: str = Form(...), room_id: str = Form(...), date_start: str = Form(...), date_end: str = Form(...)):
    db = get_db()
    es = get_es()
    hazelcast_client = get_hazelcast_client()

    # Поиск клиента по имени с помощью Elasticsearch
    client_search = es.search(index="clients", body={"query": {"match": {"name": name}}})
    client_hits = client_search['hits']['hits']
    print(client_search)
    print(name)
    if not client_hits:
        return RedirectResponse(url="/register", status_code=303)
    client_id = ObjectId(client_hits[0]['_id'])

    try:
        room_object_id = ObjectId(room_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid room ID")

    # Проверка существования комнаты
    room_exists = db.rooms.find_one({"_id": room_object_id})
    if not room_exists:
        raise HTTPException(status_code=404, detail="Room not found")

    logger.info(f"Attempting to lock room {room_id}")
    lock_successful = lock_room(hazelcast_client, str(room_object_id))
    if not lock_successful:
        logger.error(f"Failed to lock room {room_id}")
        raise HTTPException(status_code=400, detail="Room is already booked")

    # Имитация задержки
    time.sleep(60)

    # Создание и сохранение бронирования
    booking = Booking(room_id=str(room_object_id), client_id=str(client_id), booking_dates={"start": date_start, "end": date_end}, status="reserved")
    booking_id = booking.save()
    
    unlock_room(hazelcast_client, str(room_object_id))
    logger.info(f"Room {room_id} unlocked after booking")

    return templates.TemplateResponse("booking_confirmation.html", {"request": request, "booking_id": booking_id})