#!/usr/bin/env python3

import os
import csv
import sys
import subprocess
from common_functions.utilities_video import *
from common_functions.utilities_file import *


NEW_OUTPUT_DIR_NAME = "ffmpeg_nextbase_logo_cropped"
CSV_INPUT_EXPECTED_ARG_COUNT = 1


def get_crop_filter_and_bit_rate(full_input_file_path: str):
    """
        Given the full_input_file_path is a known nextbase dashcam video file
        return the appropriate crop filter and bit rate values dependent
        on the resolution of the original file.
    """
    # Establish some traits about the video
    is_1080p, is_1440p = get_resolution(full_input_file_path)
    
    crop_filter = ""
    bit_rate = 0

    if is_1080p:
        crop_filter = "1710:962:105:82"
        bit_rate = "16500k"
    elif is_1440p:
        crop_filter = "2280:1282:140:109"
        bit_rate = "28750k"
    else:
        raise ValueError(f'File {full_input_file_path} is neither 1080p or 1440p and therefore unsure how to handle.')

    return crop_filter, bit_rate


def process_row(row: [str], input_file_loc: str, output_directory: str, hw_encoder: str):
    """
        For a given row of data, input file directory location, output file directory location and available hardware acceleration
        Append the file name from the row, to the input file directory location and attempt to crop to known sizes and remove
        the nextbase logo and output the new asset at a similar location.
    """
    if len(row) != CSV_INPUT_EXPECTED_ARG_COUNT:
        print(f'Line :: {row} had more than {CSV_INPUT_EXPECTED_ARG_COUNT} arguments')
    else: 
        filename = row[0] 
        
        # Construct the full file path for the input
        full_input_file_path = os.path.join(os.path.dirname(input_file_loc), filename)
        
        # Generates the ffmpeg filter and bit rate values
        crop_filter, bit_rate = get_crop_filter_and_bit_rate(full_input_file_path)

        # Construct the full file path for the output
        new_output_file_path = f'{output_directory}/' + get_new_filename(output_directory, os.path.basename(full_input_file_path))

        # We now have all we need to feed into ffmpeg, so give a printout to help show this
        print(f"Input :: {full_input_file_path}")
        print(f'Output :: {new_output_file_path}')

        # Construct the ffmpeg shell command that uses the Apple Silicon GPU cores
        command = (
            f'ffmpeg -i {full_input_file_path} -map_metadata 0 -map_metadata:s:v 0:s:v -map_metadata:s:a 0:s:a '
            f'-filter:v crop={crop_filter} -c:v {hw_encoder} -b:v {bit_rate} -c:a copy '
            f'{new_output_file_path}'
        )

        print("\n" + command)
        print()
        subprocess.run(command, shell=True)


def process_csv(input_file_path):
    if not is_csv_file(input_file_path):
        raise ValueError("The provided file is not a CSV file.")

    # Establish what hardware accel we have available to us
    chosen_encoder = get_hw_encoder()

    with open(input_file_path, 'r') as csv_file:
        # In the same location as the csv file provided, 
        # create a directory named 'ffmpeg_cropped' and use 
        # it as an output location for the new video assets
        output_directory = os.path.join(os.path.dirname(input_file_path), NEW_OUTPUT_DIR_NAME)
        os.makedirs(output_directory, exist_ok=True)

        # Now loop through the contents of the csv file
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            process_row(row, input_file_path, output_directory, chosen_encoder)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 nextbase_logo_removal.py <fully_qualified_file_path>")
        sys.exit(1)

    try:
        process_csv(sys.argv[1])
    except ValueError as e:
        print({e})
