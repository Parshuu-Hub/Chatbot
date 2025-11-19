import os
import shutil
from fastapi import UploadFile
import tempfile
from typing import List

def save_uploaded_files_temp(files: List[UploadFile]) -> List[str]:
    """
    Saves uploaded files as temporary files and returns a list of their temp file paths.
    The files are deleted automatically when closed unless otherwise specified.
    """
    temp_file_paths = []
    for file in files:
        # Create a NamedTemporaryFile for each uploaded file
        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        temp_file.write(file.file.read())
        temp_file.flush()
        temp_file_paths.append(temp_file.name)
        temp_file.close()
    return temp_file_paths
