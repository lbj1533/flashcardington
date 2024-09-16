import sys
import json
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QLabel, QWidget,
    QFileDialog, QLineEdit, QFormLayout, QComboBox, QTextEdit, 
    QMessageBox, QHBoxLayout, QScrollArea, QGridLayout
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

        # Edit Flashcard Set Button
        self.edit_set_button = QPushButton("Edit Flashcard Set")
        self.edit_set_button.clicked.connect(self.edit_flashcard_set)
        layout.addWidget(self.edit_set_button)

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
        
        # Initialize study session variables
        self.current_card_index = 0
        self.incorrect_cards = []

        # Create a persistent shortcut for the entire study session
        self.submit_shortcut = QShortcut(QKeySequence("Return"), self)
        self.submit_shortcut.activated.connect(self.check_answer)

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

        # Display note if present without shifting layout
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

    def check_answer(self):
        current_card = self.flashcards_data["cards"][self.current_card_index]
        user_answer = self.answer_input.text().strip().lower()
        correct_answers = [ans.lower() for ans in current_card["answer"]]

        if user_answer in correct_answers:
            self.feedback_label.setText("Correct!")
            if self.current_card_index in self.incorrect_cards:
                self.incorrect_cards.remove(self.current_card_index)  # Remove if previously wrong
            self.move_to_next_card()
        else:
            self.feedback_label.setText(f"Incorrect. Correct Answer: {', '.join(current_card['answer'])}")
            if self.current_card_index not in self.incorrect_cards:
                self.incorrect_cards.append(self.current_card_index)  # Add to incorrect cards


    def move_to_next_card(self):
        self.current_card_index += 1

        # If we reach the end of the deck
        if self.current_card_index >= len(self.flashcards_data["cards"]):
            if self.incorrect_cards:
                # Restart with the incorrect cards
                self.current_card_index = self.incorrect_cards.pop(0)
                self.show_flashcard()
            else:
                # End session if no incorrect cards left
                self.end_session()
        else:
            # Show the next card
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
    # Flashcard editing interface
    def edit_flashcard_set(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("JSON Files (*.json)")
        file_dialog.setDirectory(os.path.join(os.getcwd(), "flashcards"))  # Start in the flashcards folder
        if file_dialog.exec():
            flashcard_file = file_dialog.selectedFiles()[0]
            self.load_flashcard_set_for_editing(flashcard_file)

    def load_flashcard_set_for_editing(self, file):
        with open(file, "r") as f:
            self.flashcards_data = json.load(f)

        self.flashcard_file = file
        self.show_edit_flashcards()

    def show_edit_flashcards(self):
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.scroll_area = scroll
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        for index, card in enumerate(self.flashcards_data["cards"]):
            # Card layout and container widget
            card_container = QWidget()
            card_layout = QGridLayout(card_container)

            # Question field
            question_edit = QLineEdit(", ".join(card["question"]))
            card_layout.addWidget(QLabel(f"Question {index+1}:"), 0, 0)
            card_layout.addWidget(question_edit, 0, 1)

            # Answer field
            answer_edit = QLineEdit(", ".join(card["answer"]))
            card_layout.addWidget(QLabel(f"Answer {index+1}:"), 1, 0)
            card_layout.addWidget(answer_edit, 1, 1)

            # Behavior field
            behavior_edit = QComboBox()
            behavior_edit.addItems(["and", "or"])
            behavior_edit.setCurrentText(card.get("behavior", "and"))
            card_layout.addWidget(QLabel(f"Behavior {index+1}:"), 2, 0)
            card_layout.addWidget(behavior_edit, 2, 1)

            # Note field
            note_edit = QTextEdit(card.get("note", ""))
            card_layout.addWidget(QLabel(f"Note {index+1} (optional):"), 3, 0)
            card_layout.addWidget(note_edit, 3, 1)

            # Small red 'X' button for deleting the card, at the top-right
            delete_button = QPushButton("X")
            delete_button.setStyleSheet("QPushButton { color: red; }")
            delete_button.setFixedSize(30, 30)
            delete_button.clicked.connect(lambda checked, idx=index: self.delete_card(idx))
            card_layout.addWidget(delete_button, 0, 2, alignment=Qt.AlignmentFlag.AlignRight)

            # Add the card container to the scroll layout
            scroll_layout.addWidget(card_container)

        # Add New Card button
        add_card_button = QPushButton("Add New Card")
        add_card_button.clicked.connect(self.add_new_card)
        scroll_layout.addWidget(add_card_button)

        # Set up the scroll area
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Bottom bar layout
        bottom_bar_layout = QHBoxLayout()

        # Quit button (on the left)
        quit_button = QPushButton("Quit")
        quit_button.clicked.connect(self.welcome_screen)
        bottom_bar_layout.addWidget(quit_button)

        # Save and Quit button (on the right)
        save_and_quit_button = QPushButton("Save and Quit")
        save_and_quit_button.clicked.connect(self.save_and_quit)
        bottom_bar_layout.addWidget(save_and_quit_button)

        # Spacer for aligning buttons
        bottom_bar_layout.addStretch()

        # Delete Entire Set button with red text, at the bottom
        delete_set_button = QPushButton("Delete Entire Set")
        delete_set_button.setStyleSheet("color: red;")
        delete_set_button.clicked.connect(self.delete_entire_set)
        bottom_bar_layout.addWidget(delete_set_button)

        # Bottom bar styling to minimize size
        bottom_bar_widget = QWidget()
        bottom_bar_widget.setLayout(bottom_bar_layout)
        bottom_bar_widget.setMaximumHeight(50)

        # Add the bottom bar to the main layout
        layout.addWidget(bottom_bar_widget)

        # Finalize layout
        self.main_widget.setLayout(layout)

    def delete_card(self, index):
        del self.flashcards_data["cards"][index]
        #self.save_edited_flashcard_set()
        self.show_edit_flashcards()

    def add_new_card(self):
        # Your existing logic for adding a new card
        # Ensure to scroll to the new card after adding it
        self.flashcards_data["cards"].append({
            "question": [""],
            "answer": [""],
            "behavior": "and",
            "note": ""
        })
        self.show_edit_flashcards()

        # Restore scroll position after adding a new card
        scroll_position = self.scroll_area.verticalScrollBar().value()  # Save scroll position
        self.scroll_area.verticalScrollBar().setValue(scroll_position)  # Set it back after the new card is added



    def delete_entire_set(self):
        confirmation = QMessageBox.question(self, "Confirm Deletion", 
                                            "Are you sure you want to delete the entire set? This action cannot be undone.",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirmation == QMessageBox.StandardButton.Yes:
            try:
                os.remove(self.flashcard_file)  # Delete the JSON file
            except OSError as e:
                QMessageBox.critical(self, "Error", f"Could not delete file: {str(e)}")
            self.welcome_screen()  # Return to the welcome screen

    def save_and_quit(self):
        invalid_cards = []

        # Check all cards for validity (question and answer should not be blank)
        for index, card in enumerate(self.flashcards_data["cards"]):
            if not any(q.strip() for q in card["question"]) or not any(a.strip() for a in card["answer"]):
                invalid_cards.append(index)

        # If there are invalid cards, show popup and ask user to fix or delete
        if invalid_cards:
            popup = QMessageBox(self)
            popup.setIcon(QMessageBox.Warning)
            popup.setWindowTitle("Invalid Cards")
            popup.setText("Some cards have missing questions or answers. Please fix or delete them.")
            popup.exec_()
        else:

            # Save the changes
            self.save_edited_flashcard_set_no_popup()
            self.welcome_screen()  # Return to welcome screen

    def save_edited_flashcard_set(self):
        with open(self.flashcard_file, "w") as f:
            json.dump(self.flashcards_data, f, indent=4)
        QMessageBox.information(self, "Success", "Flashcard set updated successfully!")

    def save_edited_flashcard_set_no_popup(self):
        with open(self.flashcard_file, "w") as f:
            json.dump(self.flashcards_data, f, indent=4)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FlashcardApp()
    window.show()
    sys.exit(app.exec())