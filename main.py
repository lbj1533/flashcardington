import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QListWidget, QTextEdit, QPushButton, QFileDialog, QMessageBox, 
    QSplitter, QTreeWidget, QTreeWidgetItem, QTabWidget, QInputDialog
)
from PyQt6.QtCore import Qt

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
        self.sidebar = QTreeWidget()
        self.sidebar.setHeaderHidden(True)
        self.sidebar.itemClicked.connect(self.on_item_clicked)
        
        # Tab widget for multiple file editors
        self.tab_widget = QTabWidget()
        
        # Splitter to allow resizing between sidebar and tab widget
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.tab_widget)
        splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(splitter)
        
        # Load the directory structure into the sidebar
        self.load_directory_structure("flashcards")
        
        # Save button and New File/Folder/Delete buttons
        save_button = QPushButton("Save File")
        save_button.clicked.connect(self.save_file)
        self.statusBar().addPermanentWidget(save_button)

        new_file_button = QPushButton("New File")
        new_file_button.clicked.connect(self.new_file)
        self.statusBar().addPermanentWidget(new_file_button)

        new_folder_button = QPushButton("New Folder")
        new_folder_button.clicked.connect(self.new_folder)
        self.statusBar().addPermanentWidget(new_folder_button)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_item)
        self.statusBar().addPermanentWidget(delete_button)

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
            QMessageBox.information(self, "Success", "File saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")

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
        """Close any open tabs related to the given file or directory path."""
        for index in range(self.tab_widget.count() - 1, -1, -1):
            tab_text = self.tab_widget.tabText(index)
            tab_path = os.path.join(os.path.dirname(self.current_file_path), tab_text)

            # Check if the tab corresponds to the deleted file or is inside a deleted directory
            if tab_path == path or path in os.path.dirname(tab_path):
                self.tab_widget.removeTab(index)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileEditorApp()
    window.show()
    sys.exit(app.exec())
