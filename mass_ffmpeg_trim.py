#!/usr/bin/env python3

import os
import csv
import sys
import subprocess
from common_functions.utilities_video import *
from common_functions.utilities_file import *


NEW_OUTPUT_DIR_NAME = "ffmpeg_trimmed"
CSV_INPUT_EXPECTED_ARG_COUNT = 3


def process_row(row: [str], input_file_loc: str, output_directory: str, hw_encoder: str):
    """
        For a given row of data, input file directory location, output file directory location and available hardware acceleration
        Append the file name from the row, to the input file directory location and attempt to crop to known sizes and remove
        the nextbase logo and output the new asset at a similar location.
    """
    if len(row) != CSV_INPUT_EXPECTED_ARG_COUNT:
        print(f'Line :: {row} had more than {CSV_INPUT_EXPECTED_ARG_COUNT} arguments')
    else: 
        filename, start_time, end_time = row[0], row[1], row[2]
        
        # Construct the full file path for the input
        full_input_file_path = os.path.join(os.path.dirname(input_file_loc), filename)
        
        ## TODO Validate the start and end times are within limits?
        ## What about the crazy GoPro timing as the FPS is far higher than dashcam

        # Construct the full file path for the output
        new_output_file_path = f'{output_directory}/' + get_new_filename(output_directory, os.path.basename(full_input_file_path))

        # We now have all we need to feed into ffmpeg, so give a printout to help show this
        print(f"Input :: {full_input_file_path}")
        print(f'Output :: {new_output_file_path}')

        # Construct the ffmpeg shell command that uses the Apple Silicon GPU cores
        command = (
            f'ffmpeg -i {full_input_file_path} -map_metadata 0 -map_metadata:s:v 0:s:v -map_metadata:s:a 0:s:a '
            f'-filter:v -c:v {hw_encoder} -c:a copy '
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
        print("Usage: python3 mass_ffmpeg_trim.py <fully_qualified_file_path>")
        sys.exit(1)

    try:
        process_csv(sys.argv[1])
    except ValueError as e:
        print({e})
