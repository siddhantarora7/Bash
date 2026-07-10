import asyncio
import argparse
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from rich import box
from protocols import send_msg, read_msg

console = Console()

rainbow = ["red", "orange1", "yellow", "green", "cyan", "blue", "blue_violet", "magenta"]

t = Text()
art = r'''    ____  ___   _____ __  __
   / __ )/   | / ___// / / /
  / __  / /| | \__ \/ /_/ / 
 / /_/ / ___ |___/ / __  /  
/_____/_/  |_/____/_/ /_/   '''

for line in art.splitlines():
    for x, ch in enumerate(line):
        t.append(ch, style = rainbow[x % len(rainbow)])
    t.append("\n")

panel = Panel(Align.center(t), box = box.ROUNDED, title = "✦ ✧ MATH BASH ✧ ✦",  subtitle = "~ press enter to play ~", border_style = "dim white", expand = False)

console.print(Align.center(panel))

def render_catalog(rooms):
    table = Table(title = "Room Catalog", show_header = True, header_style = "white")
        
    table.add_column("Name", style = "dim", width = 12)
    table.add_column("Players", style = "white")
    table.add_column("Difficulty", style = "white")
    table.add_column("Status", style = "white")
    table.add_column("Leader", style = "white")

    for key in rooms:
        table.add_row(key["name"], f"{key['players']}/{key['max_players']}", key["difficulty"], key["phase"], key["leader"] or "-")

    console.print(table)

# Render lobby ever 5 secs
async def rerender(host, port, lobby, time = 5):
    reader, writer = await asyncio.open_connection(host, port)
    while lobby and not lobby.done():
        await asyncio.sleep(time)
        await send_msg(writer, {"type": "list"})
        msg = await read_msg(reader)
        console.rule("[bold cyan]LOBBY[/bold cyan]")
        render_catalog(msg["rooms"])
    writer.close()
    await writer.wait_closed()

# Render lobby initially and get next cmd upon start
async def run_lobby(host, port, username):
    inp = asyncio.create_task(asyncio.to_thread(input, "Lobby > "))
    try:
        while True:
            reader, writer = await asyncio.open_connection(host, port)
            await send_msg(writer, {"type": "list"})
            msg = await read_msg(reader)
            writer.close()
            await writer.wait_closed()

            console.rule("[bold cyan]LOBBY[/bold cyan]")
            render_catalog(msg["rooms"])

            try:
                line = await asyncio.wait_for(asyncio.shield(inp), timeout = 5)
            except asyncio.TimeoutError:
                continue

            cmd = line.strip().split()
            if not cmd or cmd[0] == "refresh":
                continue
            if cmd[0] == "quit":
                return None
            elif cmd[0] == "join" and len(cmd) >= 2:
                return {"action": "join", "room": cmd[1]}
            elif cmd[0] == "create" and len(cmd) >= 2:
                if len(cmd) >= 6:
                    return {"action": "create", "room": cmd[1], "max_players": int(cmd[2]), "difficulty": cmd[3], "countdown": int(cmd[4]), "rounds": int(cmd[5])}
                return {"action": "create", "room": cmd[1],
                        "max_players": 8, "difficulty": "any", "countdown": 15, "rounds": 5}
            else:
                console.print("Commands: refresh | join <room> | create <room> | quit", style = "yellow")

# Initiate game from lobby cmd
async def run_game(host, port, username, choice):
    reader, writer = await asyncio.open_connection(host, port)
    if choice["action"] == "create":
        await send_msg(writer, {"type": "create", "name": username, "room": choice["room"], "max_players": choice["max_players"],
         "difficulty": choice["difficulty"], "countdown": choice["countdown"], "rounds": choice["rounds"]})
    else:
        await send_msg(writer, {"type": "join", "name": username, "room": choice["room"]})

    recv = asyncio.create_task(receive_loop(reader))
    inp = asyncio.create_task(input_loop(writer, username))

    await recv
    inp.cancel()
    try:
        await inp
    except asyncio.CancelledError:
            pass
    
    writer.close()
    await writer.wait_closed()

# Client side input only
async def input_loop(writer, username):
    while True:
        line = await asyncio.to_thread(input, "")
        line = line.strip()
        if line == "start":
            await send_msg(writer, {"type": "start", "name": username})
        else:
            await send_msg(writer, {"type": "submit", "answer": line})

# Get from server and respond, no input
async def receive_loop(reader):
    while True:
        msg = await read_msg(reader)
        if msg is None:
            break
        
        t = msg["type"]
        
        if t == "question":
            console.print(Text(f"~ Question {msg['num']} ~", style = "misty_rose3"))
            out = Text(msg["text"], style = "white")
            out.highlight_regex(r"\d+", "bold yellow")
            console.print(out)
        elif t == "result":
            if msg["verdict"] == "correct":
                console.print("Correct!", style = "bold green")
            else:
                console.print(f"Incorrect! Answer is {msg['answer']}", style = "bold red")
            console.print()
        elif t == "game_over":
            console.print(f"☄. *. ⋆ Final Scores: . . . . . ╰──╮", style = "dark_sea_green1")
            final_scores = msg["final_scores"]
            ranked = sorted(final_scores.items(), key = lambda x: x[1], reverse = True)
            medals = {0: "gold1", 1: "grey70", 2: "orange3"}
            for i, (name, pts) in enumerate(ranked):
                col = medals.get(i, "red")
                line = Text()
                line.append(f"{i + 1}. ", style = col)
                if pts == 1:
                    line.append(f"{name} - {pts} point", style = "white")
                else:
                    line.append(f"{name} - {pts} points", style = "white")
                console.print(line)
            break
        elif t == "global":
            console.print(msg["msg"], style = "bold cyan")
        elif t in ("error", "reanswer"):
            console.print(msg["msg"], style = "yellow")

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default = "127.0.0.1")
    parser.add_argument("--port", type = int, default = 8765)
    args = parser.parse_args()
    
    username = input("Username > ")
    
    while True:
        lobby = asyncio.create_task(run_lobby(args.host, args.port, username))
        choice = await lobby
        if choice is None:
            break

        await run_game(args.host, args.port, username, choice)

asyncio.run(main())
