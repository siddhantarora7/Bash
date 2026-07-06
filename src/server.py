import asyncio
import random

from protocols import send_msg, read_msg
from questions import load, check

class Room:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.players = {}
        self.scores = {}
        self.pool = list(range(len(QUESTIONS)))
        self.current_answer = None
        self.num = 0

QUESTIONS = load()

# Sed question via socket
def send_question(room, name):
    idx = random.choice(room.pool)
    room.pool.remove(idx)
    q = QUESTIONS[idx]
    room.current_answer = q.answer
    room.num += 1
    send_msg(room.players[name], {"type": "question", "num": room.current_num, "text": q.question})

# Client - Server communication over socket opened by main(), handles queue input only
async def handle(reader, writer):
    join = await read_msg(reader)
    name = join["name"]
    room.players[name] = writer
    room.scores[name] = 0
    await room.queue.put(("join", name))

    while True:
        msg = await read_msg(reader)
        if msg is None:
            await room.queue.put(("leave", name))
            break
        if msg["type"] == "submit":
            await room.queue.put(("submit", name, msg["answer"]))

# Core game loop
async def room_loop(room):
    while True:
        event = room.queue.get()
        t = event[0]

        if t == "join":
            name = event[1]
            await start_question(room, name)
        elif t == "submit":
            name, answer = event[1], event[2]
        elif t == "leave":
            name = event[1]
            room.players.pop(name, None)
            room.scores.pop(name, None)


# Actually start server
async def main():
    server = await asyncio.start_server(handle, "127.0.0.1", 8765)
    print("Server listening on 127.0.0.1:8765")
    async with server:
        await server.serve_forever()

asyncio.run(main())