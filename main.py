import sys
import json
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QLabel, QWidget,
    QFileDialog, QLineEdit, QFormLayout, QComboBox, QTextEdit, 
    QMessageBox, QHBoxLayout
)
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtCore import Qt

# Main Window
class FlashcardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flashcard App")
        self.setGeometry(100, 100, 800, 600)

        # Welcome Screen
        self.welcome_screen()

    def welcome_screen(self):
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        layout = QVBoxLayout()

        # Welcome message
        self.welcome_label = QLabel("Welcome to the Flashcard App!")
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.welcome_label)

        # Load Flashcards Button
        self.load_button = QPushButton("Load Flashcards")
        self.load_button.clicked.connect(self.load_flashcards)
        layout.addWidget(self.load_button)

        # Create Flashcard Set Button
        self.create_set_button = QPushButton("Create Flashcard Set")
        self.create_set_button.clicked.connect(self.create_flashcard_set)
        layout.addWidget(self.create_set_button)

        # Set the layout
        self.main_widget.setLayout(layout)

        # Keyboard shortcut to load flashcards
        load_flashcards_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        load_flashcards_shortcut.activated.connect(self.load_flashcards)

    def load_flashcards(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("JSON Files (*.json)")
        file_dialog.setDirectory(os.path.join(os.getcwd(), "flashcards"))  # Start in the flashcards folder
        if file_dialog.exec():
            flashcard_file = file_dialog.selectedFiles()[0]
            self.start_study_session(flashcard_file)

    def start_study_session(self, file):
        with open(file, "r") as f:
            self.flashcards_data = json.load(f)
        self.current_card_index = 0
        self.show_flashcard()

    def show_flashcard(self):
        # Clear screen
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        layout = QVBoxLayout()

        # Get the current flashcard
        card = self.flashcards_data["cards"][self.current_card_index]
        question = card["question"]
        answer = card["answer"]
        note = card.get("note", "")

        # Display question(s) without the label prefix
        self.question_label = QLabel(", ".join(question))
        layout.addWidget(self.question_label)

        # Display note if present without shifting layout, otherwise add blank label to keep layout consistent
        self.note_label = QLabel(f"Note: {note}" if note else " ")  # Blank space for consistency
        layout.addWidget(self.note_label)

        # Answer input field
        self.answer_input = QLineEdit(self)
        layout.addWidget(self.answer_input)

        # Feedback label for incorrect answers
        self.feedback_label = QLabel("")
        layout.addWidget(self.feedback_label)

        # Button to submit answer
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.check_answer)
        layout.addWidget(self.submit_button)

        # Quit button during study session
        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.welcome_screen)
        layout.addWidget(self.quit_button)

        self.main_widget.setLayout(layout)
        self.answer_input.setFocus()  # Automatically focus on the answer input

        # Shortcut for submitting answer with Return key
        submit_shortcut = QShortcut(QKeySequence("Return"), self)
        submit_shortcut.activated.connect(self.check_answer)

    def check_answer(self):
        card = self.flashcards_data["cards"][self.current_card_index]
        correct_answers = card["answer"]
        user_answer = self.answer_input.text().strip()

        # Handle behavior ("and"/"or") and check answers
        behavior = card.get("behavior", "and")
        if behavior == "or":
            if user_answer in correct_answers:
                self.feedback_label.setText("Correct!")
                self.move_to_next_card()
            else:
                self.feedback_label.setText(f"Incorrect. Correct Answer: {', '.join(correct_answers)}")
        else:  # "and" behavior
            if all(answer in user_answer for answer in correct_answers):
                self.feedback_label.setText("Correct!")
                self.move_to_next_card()
            else:
                self.feedback_label.setText(f"Incorrect. Correct Answer: {', '.join(correct_answers)}")

    def move_to_next_card(self):
        self.current_card_index += 1
        if self.current_card_index >= len(self.flashcards_data["cards"]):
            self.end_session()
        else:
            self.show_flashcard()

    def end_session(self):
        self.feedback_label.setText("You have completed the session!")
        self.submit_button.setDisabled(True)

    def create_flashcard_set(self):
        self.flashcard_set = []
        self.current_card = {}
        self.show_flashcard_set_creation()

    def show_flashcard_set_creation(self):
        # Clear screen
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        layout = QVBoxLayout()

        # Form for entering flashcard details
        form_layout = QFormLayout()

        # Set name input
        self.set_name_input = QLineEdit()
        form_layout.addRow("Set Name:", self.set_name_input)

        # Question input
        self.question_input = QLineEdit()
        form_layout.addRow("Question(s):", self.question_input)

        # Answer input
        self.answer_input = QLineEdit()
        form_layout.addRow("Answer(s):", self.answer_input)

        # Behavior selection
        self.behavior_box = QComboBox()
        self.behavior_box.addItems(["and", "or"])
        form_layout.addRow("Behavior:", self.behavior_box)

        # Note input (optional), smaller size
        self.note_input = QTextEdit()
        self.note_input.setFixedHeight(50)
        form_layout.addRow("Note (optional):", self.note_input)

        layout.addLayout(form_layout)

        # Add card button
        self.add_card_button = QPushButton("Add Card")
        self.add_card_button.clicked.connect(self.add_card)
        layout.addWidget(self.add_card_button)

        # Save set button
        self.save_set_button = QPushButton("Save Flashcard Set")
        self.save_set_button.clicked.connect(self.save_flashcard_set)
        layout.addWidget(self.save_set_button)

        # Quit button for leaving without saving
        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.welcome_screen)
        layout.addWidget(self.quit_button)

        self.main_widget.setLayout(layout)

        # Set focus to question input
        self.question_input.setFocus()

        # Shortcut to save the set (Ctrl+S)
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_flashcard_set)

        # Shortcut to add card with the Return key
        enter_shortcut = QShortcut(QKeySequence("Return"), self)
        enter_shortcut.activated.connect(self.add_card)

        # Ensure tab skips over the note field
        self.note_input.setTabChangesFocus(True)

    def add_card(self):
        question = self.question_input.text().strip()
        answer = self.answer_input.text().strip()
        behavior = self.behavior_box.currentText()
        note = self.note_input.toPlainText().strip()

        if question and answer:
            card = {
                "question": [q.strip() for q in question.split(',')],
                "answer": [a.strip() for a in answer.split(',')],
                "behavior": behavior
            }
            if note:
                card["note"] = note
            self.flashcard_set.append(card)

            # Clear inputs for the next card
            self.question_input.clear()
            self.answer_input.clear()
            self.note_input.clear()
            self.question_input.setFocus()
        else:
            QMessageBox.warning(self, "Error", "Please fill in both question and answer fields.")

    def save_flashcard_set(self):
        set_name = self.set_name_input.text().strip()
        if not set_name:
            QMessageBox.warning(self, "Error", "Please provide a name for the set.") 
            return
        if self.flashcard_set:
            file_dialog = QFileDialog(self)
            file_dialog.setFileMode(QFileDialog.FileMode.Directory)
        if file_dialog.exec():
            directory = file_dialog.selectedFiles()[0]
            file_path = os.path.join(directory, set_name + ".json")
            with open(file_path, "w") as f:
                flashcard_set_data = {
                    "score": 0,
                    "last_scores": [],
                    "cards": self.flashcard_set
                }
                json.dump(flashcard_set_data, f, indent=4)

            QMessageBox.information(self, "Success", "Flashcard set saved successfully!")
            self.welcome_screen()
        else:
            QMessageBox.warning(self, "Error", "Cannot save an empty set.")
    
if __name__ == "__main__": 
    app = QApplication(sys.argv) 
    window = FlashcardApp() 
    window.show() 
    sys.exit(app.exec())
