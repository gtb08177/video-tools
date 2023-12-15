#!/usr/bin/env python3
import os

def is_csv_file(file_path: str) -> bool:
    """
        Returns true if the file has an extension of 'csv'
    """
    _, file_extension = os.path.splitext(file_path)
    return file_extension.lower() == '.csv'


def get_new_filename(output_directory: str, base_filename: str) -> str:
    """ 
        Generates and returns a new file name based on inputs. 
        If the file already exists at the destination, the filename will have a suffix 
        counter determined by the number of files with the same name already 
    """
    new_filename = base_filename
    counter = 1
    while os.path.exists(os.path.join(output_directory, new_filename)):
        new_filename = f"{os.path.splitext(base_filename)[0]}_{counter}{os.path.splitext(base_filename)[1]}"
        counter += 1
    return new_filename