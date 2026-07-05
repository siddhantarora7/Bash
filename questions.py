# Make all templates for questions (text + answer)

import json

# A question will have an id, year of the competition, stage (school, chapter, state, nats), question text, and answer text.

class Question:
    def __init__(self, id: int, year: int, stage: str, question: str, answer: str):
        self.id: int = id
        self.year: int = year
        self.stage: str = stage
        self.question: str = question
        self.answer: str = answer
    
def load():
    with open('QUESTIONS.json', 'r') as f:
        data = json.load(f)

    questions = []
    for obj in data:
        q = Question(obj["id"], obj["year"], obj["stage"], obj["question"], obj["answer"])
        questions.append(q)

    return questions

def check(user_answer: str, correct_answer: str) -> bool:
    # Match answers
    return user_answer.strip().lower() == correct_answer.strip().lower()

REQUIRED = ("id", "year", "stage", "question", "answer")

def validate(path="QUESTIONS.json"):
    with open(path, "r") as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        print("Error: Tob level must be a list")
        return
    
    problems = []
    seen = set()

    for i, obj in enumerate(data):
        for field in REQUIRED:
            if field not in obj:
                problems.append(f"Entry #{i + 1} missing {field}")
        
        idx = obj.get("id")
        if idx in seen:
            problems.append(f"Entry #{i + 1} duplicate ID: {idx}")
        seen.add(idx)

        if not str(obj.get("question", "").strip()):
            problems.append(f"Entry #{i + 1} empty question")
        if not str(obj.get("answer", "").strip()):
            problems.append(f"Entry #{i + 1} empty answer")
        
        blob = str(obj.get("question", "").strip()) + str(obj.get("answer", "").strip())
        if "$" in blob or "//" in blob:
            problems.append(f"Entry #{i + 1} seems to have latex")

    if problems:
        print(f"{len(problems)} problems")
        print()
        for p in problems:
            print(" - " + p)
    else:
        print('No problems!')

