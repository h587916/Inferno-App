from PySide6.QtCore import QObject, Signal
import os
import shutil
import stat

UPLOAD_FOLDER = 'files/uploads/'
METADATA_FOLDER = 'files/metadata/'
LEARNT_FOLDER = 'files/learnt/'

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
        self.uploaded_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.csv')]
        self.metadata_files = [f for f in os.listdir(METADATA_FOLDER) if f.endswith('.csv')]
        self.learnt_folders = [f for f in os.listdir(LEARNT_FOLDER) if os.path.isdir(os.path.join(LEARNT_FOLDER, f))]

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

