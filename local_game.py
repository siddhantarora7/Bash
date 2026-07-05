from questions import load
from questions import check
import random

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
