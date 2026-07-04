# Make all templates for questions (text + answer)

import json

class Question():
    def __init__(self, id: int, year: int, stage: str, question: str, answer: int):
        self.id: int = id
        self.year: int = year
        self.stage: str = stage
        self.question: str = question
        self.answer: int = answer
    
