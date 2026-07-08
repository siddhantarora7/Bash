import asyncio
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
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
    username = input("Username > ")
    reader, writer = await asyncio.open_connection("127.0.0.1", 8765)
    await send_msg(writer, {"type": "join", "name": username})

    async with asyncio.TaskGroup() as tg:
        tg.create_task(receive_loop(reader))
        tg.create_task(input_loop(writer, username))
    writer.close()
    await writer.wait_closed()

asyncio.run(main())
