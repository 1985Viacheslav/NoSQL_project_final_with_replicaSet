import hazelcast
from dependencies import logger

def get_hazelcast_client():
    client = hazelcast.HazelcastClient(
        cluster_members=[
            "hazelcast:5701"
        ]
    )
    return client

def lock_room(client, room_id):
    lock = client.get_lock(str(room_id))
    locked = lock.lock()
    logger.info(f"Room {room_id} locked: {locked}")
    return locked

def unlock_room(client, room_id):
    lock = client.get_lock(str(room_id))
    lock.unlock()
    logger.info(f"Room {room_id} unlocked")
