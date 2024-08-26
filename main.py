import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QListWidget, QTextEdit, QPushButton, QFileDialog, QMessageBox, 
    QSplitter, QTreeWidget, QTreeWidgetItem, QTabWidget, QInputDialog
)
from PyQt6.QtCore import Qt, QTimer

class FileEditorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Editor with Tabs and Sidebar")
        self.setGeometry(100, 100, 800, 600)
        
        # Main layout
        main_layout = QHBoxLayout()
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
        # Sidebar: QTreeWidget to list files and directories
        sidebar_layout = QVBoxLayout()
        self.sidebar = QTreeWidget()
        self.sidebar.setHeaderHidden(True)
        self.sidebar.itemClicked.connect(self.on_item_clicked)
        sidebar_layout.addWidget(self.sidebar)
        
        # Buttons for New File, New Folder, and Delete in the sidebar
        self.new_file_button = QPushButton("New File")
        self.new_file_button.clicked.connect(self.new_file)
        sidebar_layout.addWidget(self.new_file_button)

        self.new_folder_button = QPushButton("New Folder")
        self.new_folder_button.clicked.connect(self.new_folder)
        sidebar_layout.addWidget(self.new_folder_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_item)
        sidebar_layout.addWidget(self.delete_button)

        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar_layout)
        
        # Tab widget for multiple file editors
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

        # Splitter to allow resizing between sidebar and tab widget
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(sidebar_widget)
        splitter.addWidget(self.tab_widget)
        splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(splitter)
        
        # Load the directory structure into the sidebar
        self.load_directory_structure("flashcards")
        
        # Save button and new buttons on the status bar
        save_button = QPushButton("Save File")
        save_button.clicked.connect(self.save_file)
        self.statusBar().addPermanentWidget(save_button)

        help_button = QPushButton("Help")
        help_button.clicked.connect(self.show_help)
        self.statusBar().addPermanentWidget(help_button)

        study_button = QPushButton("Study")
        study_button.clicked.connect(self.study)
        self.statusBar().addPermanentWidget(study_button)

        # Current file path
        self.current_file_path = ""
        
        # Timer for auto-save
        self.auto_save_timer = QTimer()
        self.auto_save_timer.setInterval(2000)  # Auto-save delay (in milliseconds)
        self.auto_save_timer.timeout.connect(self.auto_save)

    def load_directory_structure(self, root_dir):
        """Load the directory structure into the sidebar."""
        self.sidebar.clear()
        root_item = QTreeWidgetItem([root_dir])
        self.sidebar.addTopLevelItem(root_item)
        self.add_sub_items(root_item, root_dir)
        root_item.setExpanded(True)

    def add_sub_items(self, tree_widget_item, path):
        """Recursively add subdirectories and files to the tree."""
        for item in sorted(os.listdir(path)):
            item_path = os.path.join(path, item)
            sub_item = QTreeWidgetItem([item])
            tree_widget_item.addChild(sub_item)
            if os.path.isdir(item_path):
                self.add_sub_items(sub_item, item_path)

    def on_item_clicked(self, item, column):
        """Handle the event when an item in the sidebar is clicked."""
        path_parts = []
        current_item = item
        while current_item:
            path_parts.insert(0, current_item.text(0))
            current_item = current_item.parent()
        
        self.current_file_path = os.path.join(*path_parts)
        
        if os.path.isfile(self.current_file_path):
            self.open_file(self.current_file_path)

    def open_file(self, file_path):
        """Open the file in a new tab and display its contents in the text editor."""
        # Check if the file is already open in any tab
        for index in range(self.tab_widget.count()):
            if self.tab_widget.tabText(index) == os.path.basename(file_path):
                # If the file is already open, switch to the tab
                self.tab_widget.setCurrentIndex(index)
                return

        # If the file is not open, open it in a new tab
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            
            # Create a new text editor widget for this file
            text_editor = QTextEdit()
            text_editor.setPlainText(content)
            text_editor.textChanged.connect(self.start_auto_save_timer)
            tab_index = self.tab_widget.addTab(text_editor, os.path.basename(file_path))
            self.tab_widget.setCurrentIndex(tab_index)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")

    def save_file(self):
        """Save the content of the text editor in the current tab to the current file."""
        if not self.current_file_path:
            QMessageBox.warning(self, "Warning", "No file selected.")
            return

        current_editor = self.tab_widget.currentWidget()
        if not current_editor:
            QMessageBox.warning(self, "Warning", "No file open in the current tab.")
            return

        try:
            with open(self.current_file_path, 'w') as file:
                file.write(current_editor.toPlainText())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")

    def start_auto_save_timer(self):
        """Start the auto-save timer when the text editor content changes."""
        self.auto_save_timer.start()

    def auto_save(self):
        """Automatically save the file if changes have been made."""
        self.auto_save_timer.stop()  # Stop the timer once the save operation is triggered
        self.save_file()

    def new_file(self):
        """Create a new file in the selected directory."""
        if not self.current_file_path or not os.path.isdir(self.current_file_path):
            QMessageBox.warning(self, "Warning", "Please select a directory to create a new file.")
            return

        file_name, ok = QInputDialog.getText(self, 'New File', 'Enter file name:')
        if ok and file_name:
            file_path = os.path.join(self.current_file_path, file_name)
            try:
                open(file_path, 'w').close()
                self.load_directory_structure("flashcards")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not create file: {str(e)}")

    def new_folder(self):
        """Create a new folder in the selected directory."""
        if not self.current_file_path or not os.path.isdir(self.current_file_path):
            QMessageBox.warning(self, "Warning", "Please select a directory to create a new folder.")
            return

        folder_name, ok = QInputDialog.getText(self, 'New Folder', 'Enter folder name:')
        if ok and folder_name:
            folder_path = os.path.join(self.current_file_path, folder_name)
            try:
                os.makedirs(folder_path)
                self.load_directory_structure("flashcards")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not create folder: {str(e)}")

    def delete_item(self):
        """Delete the selected file or folder, handling non-empty directories."""
        if not self.current_file_path:
            QMessageBox.warning(self, "Warning", "No file or folder selected.")
            return

        if os.path.isdir(self.current_file_path):
            # Count the number of items in the directory
            item_count = sum([len(files) for _, _, files in os.walk(self.current_file_path)])
            reply = QMessageBox.question(self, 'Delete Directory', 
                                         f"The directory '{self.current_file_path}' contains {item_count} items. "
                                         "Are you sure you want to delete it and all its contents?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                         QMessageBox.StandardButton.No)
        else:
            reply = QMessageBox.question(self, 'Delete File', f"Are you sure you want to delete '{self.current_file_path}'?", 
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                         QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Close any open tabs related to this file or directory
                self.close_related_tabs(self.current_file_path)

                # Delete file or directory
                if os.path.isdir(self.current_file_path):
                    self.delete_directory(self.current_file_path)
                else:
                    os.remove(self.current_file_path)
                self.load_directory_structure("flashcards")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete item: {str(e)}")

    def delete_directory(self, path):
        """Recursively delete a directory and all its contents."""
        for root, dirs, files in os.walk(path, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(path)

    def close_related_tabs(self, path):
        """Close any open tabs related to the file or directory being deleted."""
        for index in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(index)
            tab_path = os.path.join(os.path.dirname(self.current_file_path), self.tab_widget.tabText(index))
            if tab_path.startswith(path):
                self.tab_widget.removeTab(index)

    def close_tab(self, index):
        """Close the tab at the given index."""
        self.tab_widget.removeTab(index)

    def show_help(self):
        """Show help information about the application."""
        QMessageBox.information(self, "Help", 
                                "This is a flashcard file editor. You can create, delete, and edit files and folders.\n"
                                "Flashcard files should have a specific format:\n"
                                "1. Use '# comment' for comments\n"
                                "2. Use 'question : answer' format for flashcards\n"
                                "3. '&' represents 'and', '|' represents 'or', '*' represents smart grading.")

    def study(self):
        """Process the flashcard file for study."""
        if not self.current_file_path:
            QMessageBox.warning(self, "Warning", "No file selected.")
            return
        
        current_editor = self.tab_widget.currentWidget()
        if not current_editor:
            QMessageBox.warning(self, "Warning", "No file open in the current tab.")
            return
        
        content = current_editor.toPlainText()
        questions = self.parse_flashcards(content)
        self.process_flashcards(questions)

    def parse_flashcards(self, content):
        """Parse the flashcards from the content."""
        lines = content.splitlines()
        flashcards = {}
        for line in lines:
            if ':' in line:
                question, answer = line.split(':', 1)
                flashcards[question.strip()] = answer.strip()
        return flashcards

    def process_flashcards(self, flashcards):
        """Process each flashcard for the study session."""
        for question, answer in flashcards.items():
            user_answer, ok = QInputDialog.getText(self, "Flashcard", question)
            if ok:
                correct = self.evaluate_answer(answer, user_answer)
                QMessageBox.information(self, "Result", "Correct!" if correct else "Incorrect.")
    
    def evaluate_answer(self, correct_answer, user_answer):
        """Evaluate the user's answer based on the correct answer format."""
        correct_parts = [part.strip() for part in correct_answer.split('|')]
        for part in correct_parts:
            subparts = [subpart.strip() for subpart in part.split('&')]
            if all(subpart in user_answer for subpart in subparts):
                return True
        return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileEditorApp()
    window.show()
    sys.exit(app.exec())
