# Make all templates for questions (text + answer)

import json

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
