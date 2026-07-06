import asyncio
from rich.console import Console
from rich.text import Text
from protocol import send_msg, read_msg

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

async def main():
    username = input("Enter a username > ")
    reader, writer = await asyncio.open_connection("127.0.0.1", 8765)

    await send_msg(writer, {"type": "join", "name": username})

    i = 0
    while True:
        msg = await read_msg(reader)
        if msg is None:
            break
        
        if msg["type"] == "question":
            console.print(Text(f"~ Question {i + 1} ~", style = "misty_rose3"))
            out = Text(msg["text"], style = "white")
            out.highlight_regex(r"\d+", "bold yellow")
            console.print(out)
            player_ans = input("> ")
            i += 1
            await send_msg(writer, {"type": "submit", "answer": player_ans})
        elif msg["type"] == "result":
            if msg["verdict"] == "correct":
                console.print("Correct!", style = "bold green")
            else:
                console.print(f"Incorrect! Answer is {msg['answer']}", style = "bold red")
            console.print()
        elif msg["type"] == "game_over":
            console.print(f"☄. *. ⋆ Final Score: {msg['final_score']} . . . . . ╰──╮", style = "dark_sea_green1")
            break

    writer.close()
    await writer.wait_closed()

asyncio.run(main())
