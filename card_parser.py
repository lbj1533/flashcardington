import json
from pathlib import Path

class JSONFlashcardParser:
    def __init__(self, filename):
        self.filepath = Path('flashcards') / filename
        self.data = None
    
    def parse(self):
        with open(self.filepath, 'r') as f:
            self.data = json.load(f)
    
    def get_score(self):
        return self.data.get('score')

    def get_last_scores(self):
        return self.data.get('last_scores')

    def get_cards(self):
        return self.data.get('cards')

# Example usage:
parser = JSONFlashcardParser('myflashcards.json')
parser.parse()

print("Score:", parser.get_score())
print("Last 5 Scores:", parser.get_last_scores())
print("Cards:")
for card in parser.get_cards():
    print(card)
