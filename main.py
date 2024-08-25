import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QListWidget, QTextEdit, QPushButton, QFileDialog, QMessageBox, 
    QSplitter, QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import Qt

class FileEditorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Editor with Sidebar")
        self.setGeometry(100, 100, 800, 600)
        
        # Main layout
        main_layout = QHBoxLayout()
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
        # Sidebar: QTreeWidget to list files and directories
        self.sidebar = QTreeWidget()
        self.sidebar.setHeaderHidden(True)
        self.sidebar.itemClicked.connect(self.on_item_clicked)
        
        # Scroll area for the sidebar
        self.sidebar_scroll = QWidget()
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_layout.addWidget(self.sidebar)
        self.sidebar_scroll.setLayout(self.sidebar_layout)
        
        # Main text editor
        self.text_editor = QTextEdit()
        
        # Splitter to allow resizing between sidebar and editor
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.text_editor)
        splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(splitter)
        
        # Load the directory structure into the sidebar
        self.load_directory_structure("flashcards")
        
        # Save button
        save_button = QPushButton("Save File")
        save_button.clicked.connect(self.save_file)
        self.statusBar().addPermanentWidget(save_button)

        # Current file path
        self.current_file_path = ""

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
        """Open the file and display its contents in the text editor."""
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            self.text_editor.setPlainText(content)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")

    def save_file(self):
        """Save the content of the text editor to the current file."""
        if not self.current_file_path:
            QMessageBox.warning(self, "Warning", "No file selected.")
            return

        try:
            with open(self.current_file_path, 'w') as file:
                file.write(self.text_editor.toPlainText())
            QMessageBox.information(self, "Success", "File saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileEditorApp()
    window.show()
    sys.exit(app.exec())
