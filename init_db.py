from pymongo import MongoClient
from models import Room
import pandas as pd
import random
from datetime import datetime, timedelta
from dependencies import MONGO_URL, MONGO_DB, DATABASE_RESET

# Функция для генерации случайных дат
def random_dates(start, end, n=1):
    start_u = start.timestamp()
    end_u = end.timestamp()
    return [datetime.fromtimestamp(random.uniform(start_u, end_u)) for _ in range(n)]

def initialize_db(reset=True):
    # Подключение к MongoDB
    client = MongoClient(MONGO_URL)
    db = client[MONGO_DB]

    # Очистка коллекций при необходимости
    if reset:
        db.clients.delete_many({})
        db.rooms.delete_many({})
        db.bookings.delete_many({})

    # Генерация пользователей 
    # Загрузка данных из CSV файла
    df = pd.read_csv('./static/customer_names.csv')

    # Обработка каждой строки
    for index, row in df.iterrows():
        # Формирование уникального имени пользователя
        user_name = f"{row['First Name']} {row['Last Name']}".strip()
        # Вставка в базу данных
        db.clients.insert_one({"name": user_name})

    # Загрузка комнат
    # Загрузка данных из CSV файла
    df = pd.read_csv('./static/room_data.csv')

    # Очистка и форматирование данных
    df = df[['id', 'name', 'neighbourhood', 'latitude', 'longitude', 'room_type', 'price']]
    
    # Добавление данных в базу
    for index, row in df.iterrows():
        room = Room(row['id'], row['name'], row['neighbourhood'], row['latitude'], row['longitude'], row['room_type'], row['price'])
        room.save()
    
    # Генерация броней
    client_ids = [client['_id'] for client in db.clients.find({})]
    room_ids = [room['_id'] for room in db.rooms.find({})]
    
    for room_id in room_ids:
        for _ in range(random.randint(5, 10)):  # Случайное количество бронирований для каждой комнаты
            client_id = random.choice(client_ids)
            start_date, end_date = random_dates(datetime.now(), datetime.now() + timedelta(days=365), 2)
            start_date, end_date = sorted([start_date.date(), end_date.date()])

            booking_data = {
                "room_id": room_id,
                "client_id": client_id,
                "booking_dates": {"start": start_date.strftime("%Y-%m-%d"), "end": end_date.strftime("%Y-%m-%d")},
                "status": "reserved"
            }
            db.bookings.insert_one(booking_data)

initialize_db(reset=DATABASE_RESET)
