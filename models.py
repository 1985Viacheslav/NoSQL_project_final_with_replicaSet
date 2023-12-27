from pymongo import MongoClient
from bson import ObjectId, json_util
from dependencies import MONGO_URL, MONGO_DB, es

class Client:
    def __init__(self, name):
        self.name = name

        self.client = MongoClient(MONGO_URL)
        self.db = self.client[MONGO_DB]

    def save(self):
        client_data = {"name": self.name}
        client_id = self.db.clients.insert_one(client_data).inserted_id
        es.index(index="clients", id=str(client_id), document=client_data)
        return client_id

class Room:
    def __init__(self, room_id, name, neighbourhood, latitude, longitude, room_type, price):
        self.room_id = room_id
        self.name = name
        self.neighbourhood = neighbourhood
        self.latitude = latitude
        self.longitude = longitude
        self.room_type = room_type
        self.price = price

        self.client = MongoClient(MONGO_URL)
        self.db = self.client[MONGO_DB]

    def save(self):
        room_data = {
            "name": self.name,
            "neighbourhood": self.neighbourhood,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "room_type": self.room_type,
            "price": self.price
        }
        result = self.db.rooms.insert_one(room_data)
        room_id = str(result.inserted_id)

        es_data = {k: v for k, v in room_data.items() if k != '_id'}
        es.index(index="rooms", id=room_id, document=es_data)
        return room_id

class Booking:
    def __init__(self, room_id, client_id, booking_dates, status):
        self.room_id = ObjectId(room_id)
        self.client_id = ObjectId(client_id)
        self.booking_dates = booking_dates
        self.status = status

        self.client = MongoClient(MONGO_URL)
        self.db = self.client[MONGO_DB]

    def save(self):
        booking_data = {
            "room_id": self.room_id,
            "client_id": self.client_id,
            "booking_dates": self.booking_dates,
            "status": self.status
        }
        booking_id = self.db.bookings.insert_one(booking_data).inserted_id

        es_data = json_util.dumps(booking_data)

        es.index(index="bookings", id=str(booking_id), document=es_data)
        return booking_id
