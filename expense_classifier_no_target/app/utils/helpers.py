import os
import tempfile

def create_temp_directory():
    return tempfile.mkdtemp()

def validate_file_extension(filename):
    allowed_extensions = ['xlsx', 'xls']
    if not filename.split('.')[-1].lower() in allowed_extensions:
        raise ValueError(f"Invalid file extension. Allowed extensions: {allowed_extensions}")
