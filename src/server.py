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
    
    score = 0
    inds = list(range(len(QUESTIONS)))
    for i in range(min(5, len(QUESTIONS))):
        idx = random.choice(inds)
        inds.remove(idx)
        q = QUESTIONS[idx]

        await send_msg(writer, {"type": "question", "num": i + 1, "text": q.question})
        reply = await read_msg(reader)

        if reply is None:
            break

        if check(reply["answer"], q.answer):
            score += 1
            await send_msg(writer, {"type": "result", "verdict": "correct", "answer": q.answer})
        else:
            await send_msg(writer, {"type": "result", "verdict": "wrong", "answer": q.answer})
    
    await send_msg(writer, {"type": "game_over", "final_score": score})
    writer.close()
    await writer.wait_closed()

# Actually start server
async def main():
    server = await asyncio.start_server(handle, "127.0.0.1", 8765)
    print("Server listening on 127.0.0.1:8765")
    async with server:
        await server.serve_forever()

asyncio.run(main())