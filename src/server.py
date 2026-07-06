import asyncio
import random

from protocols import send_msg, read_msg
from questions import load, check

class Room:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.players = {}
        self.scores = {}

QUESTIONS = load()

# Client - Server communication over socket opened by main()
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

# Actually start server
async def main():
    server = await asyncio.start_server(handle, "127.0.0.1", 8765)
    print("Server listening on 127.0.0.1:8765")
    async with server:
        await server.serve_forever()

asyncio.run(main())