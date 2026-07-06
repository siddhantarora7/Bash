import asyncio

QUESTIONS = load()
username = input("Enter a username")

reader, writer = await asyncio.open_connection("127.0.0.1", 8765)
await send_msg(writer, {"type": "join", "name": username})

for i in range(min(5, len(QUESTIONS))):
    question_string = await read_msg(reader)
    console.print(Text(f"~ Question {i + 1} ~", style = "misty_rose3"))
    out = Text(question_string, style = "white")
    out.highlight_regex(r"\d+", "bold yellow")
    console.print(out)
    player_ans = input("> ")
    await send_msg(writer, {"type": "submit", "answer": player_ans})
    result = await read_msg(reader)
    if result["verdict"] == "correct":
        console.print("Correct!", style = "bold green")
    else:
        console.print(f"Incorrect! Answer is {q.answer}", style = "bold red")
    console.print()

score = await read_msg(reader)
score = score["final_score"]
console.print(f"☄. *. ⋆ Final Score: {score} . . . . . ╰──╮", style = "dark_sea_green1")
