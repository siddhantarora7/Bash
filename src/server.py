import asyncio
import random

from protocols import send_msg, read_msg
from questions import load, check

QUESTIONS = load()

class Room:
    def __init__(self, max_players = 8, difficulty = "any", countdown = 15, rounds = 5):
        self.queue = asyncio.Queue()
        self.host = None
        self.phase = "waiting"
        self.players = {}
        self.scores = {}
        self.out = set()
        self.pool = list(range(len(QUESTIONS)))
        self.current_answer = None
        self.num = 0
        self.rng = random.Random()
        self.max_players = max_players
        self.difficulty = difficulty
        self.countdown = countdown
        self.rounds = rounds

    # Reset room after game completion
    def reset(self):
        self.phase = "waiting"
        self.out = set()
        self.pool = list(range(len(QUESTIONS)))
        self.current_answer = None
        self.num = 0
        for name in self.scores:
            self.scores[name] = 0

# Init global room dict dynamically populated upon room creation
rooms = {}

def create_room(name, max_players = None, difficulty = None, countdown = None, rounds = None):
    rooms[name] = Room(max_players, difficulty, countdown, rounds)
    asyncio.create_task(room_loop(rooms[name]))
    return rooms[name]

# Convey a message to all players in a room
async def broadcast(room, msg):
    for player in room.players:
        await send_msg(room.players[player], msg)

async def start_timer(room, num, time=15):
    await asyncio.sleep(time)
    await room.queue.put(("timeout", num))

# Sed question via socket
async def send_question(room):
    room.out = set()
    idx = room.rng.choice(room.pool)
    room.pool.remove(idx)
    q = QUESTIONS[idx]
    room.current_answer = q.answer
    room.num += 1
    asyncio.create_task(start_timer(room, room.num, room.countdown))
    await broadcast(room, {"type": "question", "num": room.num, "text": q.question})

def leader_of(room):
    if not room.scores:
        return None
    return max(room.scores, key = room.scores.get)

# Client - Server communication over socket opened by main(), handles queue input only
async def handle(reader, writer):
    init = await read_msg(reader)

    if init["type"] == "list":
        catalog = []
        for rname, room in rooms.items():
            catalog.append({
                "name": rname,
                "players": len(room.players),
                "max_players": room.max_players,
                "difficulty": room.difficulty,
                "phase": room.phase,
                "leader": leader_of(room),
            })
        await send_msg(writer, {"type": "catalog", "rooms": catalog})
        # Temporary
        writer.close()
        await writer.wait_closed()
        return

    name, room_name = init["name"], init["room"]
    
    if init["type"] == "create":
        max_players, difficulty, countdown, rounds = init["max_players"], init["difficulty"], init["countdown"], init["rounds"]
        room = create_room(room_name, max_players, difficulty, countdown, rounds)
    else:
        if room_name not in rooms:
            await send_msg(writer, {"type": "error", "msg": "Room does not exist"})
            writer.close()
            return
        else:
            room = rooms[room_name]
            if len(room.players) >= room.max_players:
                await send_msg(writer, {"type": "error", "msg": "Room reached max capacity"})
                writer.close()
                return
    
    room.players[name] = writer
    room.scores[name] = 0

    if len(room.players) == 1:
        room.host = name

    await room.queue.put(("join", name))

    while True:
        msg = await read_msg(reader)
        if msg is None:
            await room.queue.put(("leave", name, room_name))
            break
        if msg["type"] == "start":
            if name == room.host:
                await room.queue.put(("start", name))
            else:
                await send_msg(writer, {"type": "error", "msg": "Permission Denied: Only host can start games"})
        elif msg["type"] == "submit":
            await room.queue.put(("submit", name, msg["answer"]))

# Core game loop
async def room_loop(room):
    while True:
        event = await room.queue.get()
        t = event[0]

        if t == "start":
            room.phase = "ready"
            await send_question(room)
        elif t == "submit":
            name = event[1]
            if name not in room.out:
                if room.phase == "ready":
                    answer = event[2]
                    if check(answer, room.current_answer):
                        room.scores[name] += 1
                        await send_msg(room.players[name], {"type": "result", "verdict": "correct", "answer": room.current_answer})
                        await broadcast(room, {"type": "global", "msg": f"Player {name} bashed it!"})   

                        if room.num >= min(len(QUESTIONS),room.rounds):
                            await broadcast(room, {"type": "game_over", "final_scores": room.scores})
                            room.reset()
                        else:
                            await send_question(room)  
                    else:
                        room.out.add(name)
                        await send_msg(room.players[name], {"type": "result", "verdict": "wrong", "answer": room.current_answer})
                else:
                    await send_msg(room.players[name], {"type": "error", "msg": "Game has not started yet"})
            else:
                await send_msg(room.players[name], {"type": "reanswer", "msg": "Player cannot answer twice"})
        elif t == "timeout":
            num = event[1]
            if num == room.num:
                await broadcast(room, {"type": "global", "msg": "Time's out!"})
                if room.num >= min(len(QUESTIONS), room.rounds):
                    await broadcast(room, {"type": "game_over", "final_scores": room.scores})
                    room.reset()
                else:
                    await send_question(room)
        elif t == "leave":
            name, room_name = event[1], event[2]
            room.players.pop(name, None)
            room.scores.pop(name, None)
            if not room.players:
                rooms.pop(room_name, None)
                return

# Actually start server
async def main():
    server = await asyncio.start_server(handle, "127.0.0.1", 8765)
    print("Server listening on 127.0.0.1:8765")
    async with server:
        await server.serve_forever()

asyncio.run(main())