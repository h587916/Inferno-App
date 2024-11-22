from PySide6.QtCore import QObject, Signal
import os
import shutil
from PySide6.QtWidgets import QMessageBox

HOME_DIR = os.path.expanduser('~')
APP_DIR = os.path.join(HOME_DIR, '.inferno_app')  # Using a hidden directory

if not os.path.exists(APP_DIR):
    os.makedirs(APP_DIR)

UPLOAD_FOLDER = os.path.join(APP_DIR, 'uploads')
METADATA_FOLDER = os.path.join(APP_DIR, 'metadata')
LEARNT_FOLDER = os.path.join(APP_DIR, 'learnt')
CONFIG_FOLDER = os.path.join(APP_DIR, 'config')

# Ensure the directories exist
for folder in [UPLOAD_FOLDER, METADATA_FOLDER, LEARNT_FOLDER, CONFIG_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

class FileManager(QObject):
    # Signals to notify when files or learnt folders are updated
    files_updated = Signal()
    learnt_folders_updated = Signal()

    def __init__(self):
        super().__init__()
        self.uploaded_files = []
        self.metadata_files = []
        self.learnt_folders = []
        self.refresh()

    def load_files(self):
        """Load the files from the uploads, metadata, and learnt folders."""
        if os.path.exists(UPLOAD_FOLDER):
            self.uploaded_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.csv')]

        if os.path.exists(METADATA_FOLDER):
            self.metadata_files = [f for f in os.listdir(METADATA_FOLDER) if f.endswith('.csv')]

        if os.path.exists(LEARNT_FOLDER):
            self.learnt_folders = [
                f for f in os.listdir(LEARNT_FOLDER) if os.path.isdir(os.path.join(LEARNT_FOLDER, f))
            ]

    def refresh(self):
        """Refresh the list of uploaded files, metadata files, and learnt folders."""
        self.load_files()
        self.files_updated.emit()
        self.learnt_folders_updated.emit()

    def add_file(self, file_path, folder):
        """Copy the file to the specified folder and refresh the list."""
        file_name = os.path.basename(file_path)
        destination = os.path.join(folder, file_name)

        try:
            shutil.copy(file_path, destination)
            self.refresh()
        except Exception as e:
            print(f"Error copying file: {e}")

    def delete_file(self, file_name, folder):
        """Delete the file from the specified folder and refresh the list."""
        file_path = os.path.join(folder, file_name)
        if os.path.exists(file_path):
            try:
                if os.path.isdir(file_path):
                    os.rmdir(file_path)
                else:
                    os.remove(file_path)
                self.refresh()
            except Exception as e:
                print(f"Error deleting file: {e}")

    def rename_file(self, file_name, new_name, folder):
        """Rename the file in the specified folder and refresh the list."""
        old_path = os.path.join(folder, file_name)
        new_path = os.path.join(folder, new_name)
        if os.path.exists(old_path):
            try:
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)
                    self.refresh()
            except Exception as e:
                print(f"Error renaming file: {e}")
