from rich.console import Console
from rich.text import Text
console = Console()

from questions import load
from questions import check
import random

rainbow = ["red", "orange", "yellow", "green", "cyan", "blue", "indigo", "magenta"]

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

console.print(t)

score = 0

questions = load()
ind = [i for i in range(len(questions))]

for i in range(min(5, len(questions))):
    idx = random.choice(ind)
    ind.remove(idx)
    q = questions[idx]
    print(q.question)
    player_ans = input("> ")
    if check(player_ans, q.answer):
        score += 1
        print("Correct!")
    else:
        print(f"Incorrect! It was {q.answer}")

print("Final score", score)
