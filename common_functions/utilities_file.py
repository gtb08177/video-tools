#!/usr/bin/env python3
import os

def is_csv_file(file_path: str) -> bool:
    """
        Returns true if the file has an extension of 'csv'
    """
    return os.path.exists(file_path) and file_path.endswith('.csv')


def gen_new_filepath(output_directory: str, file: str, new_extension: str = None) -> str:
    """ 
        Generates and returns a new file name based on inputs. 
        If the file already exists at the destination, the file name will have a number
        suffix determined by the number of files with the same name already. 
    """

    # Default return name in the event this file does not exist at the destination.
    output_filename = file
    base_name, extension = os.path.splitext(file)

    # if an alternate extension is wanted, override the output filename
    if new_extension:
        output_filename = base_name + '.' + new_extension
    
    counter = 0

    # Iterate until a non-existing filename is found
    while os.path.exists(os.path.join(output_directory, output_filename)):
        counter += 1
        output_filename = f"{base_name}_{counter}{extension}"

    return os.path.join(output_directory, output_filename)
