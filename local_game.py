from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich import box

from questions import load
from questions import check
import random

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

score = 0

questions = load()
ind = [i for i in range(len(questions))]

for i in range(min(5, len(questions))):
    idx = random.choice(ind)
    ind.remove(idx)
    q = questions[idx]
    question_string = q.question
    console.print(Text(f"~ Question {i + 1} ~", style = "misty_rose3"))
    out = Text(question_string, style = "white")
    out.highlight_regex(r"\d+", "bold yellow")
    console.print(out)
    player_ans = input("> ")
    if check(player_ans, q.answer):
        score += 1
        console.print("Correct!", style = "bold green")
    else:
        console.print(f"Incorrect! Answer is {q.answer}", style = "bold red")
    console.print()

console.print(f"☄. *. ⋆ Final Score: {score} . . . . . ╰──╮", style = "dark_sea_green1")
