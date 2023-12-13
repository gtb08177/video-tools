#!/usr/bin/env python3

import os
import csv
import sys
import subprocess

NEW_OUTPUT_DIR_NAME = "ffmpeg_cropped"
CSV_INPUT_EXPECTED_ARG_COUNT = 3

def is_csv_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    return file_extension.lower() == '.csv'


def get_new_filename(output_directory, base_filename):
    # Check if the file already exists
    new_filename = base_filename
    counter = 1
    while os.path.exists(os.path.join(output_directory, new_filename)):
        new_filename = f"{os.path.splitext(base_filename)[0]}_{counter}{os.path.splitext(base_filename)[1]}"
        counter += 1
    return new_filename


def process_csv(csv_file_path, is_dashcam_footage):
    if not is_csv_file(csv_file_path):
        raise ValueError("The provided file is not a CSV file.")

    with open(csv_file_path, 'r') as csv_file:
        # Create a directory named 'ffmpeg_cropped' in the same location
        # as the CSV file and use it as an output location for the new assets
        output_directory = os.path.join(os.path.dirname(csv_file_path), NEW_OUTPUT_DIR_NAME)
        os.makedirs(output_directory, exist_ok=True)

        # now process the data
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            if len(row) == CSV_INPUT_EXPECTED_ARG_COUNT:
                filename, start_time, end_time = row[0], row[1], row[2]
                # Construct the full path for the filename
                full_input_file_path = os.path.join(os.path.dirname(csv_file_path), filename)

                msg_debug_input = f"Input :: {full_input_file_path} - {start_time} to {end_time}"

                # TODO check these for GoPro
                ## 1080p filter
                ## -filter:v "crop=1710:962:105:82"
                ## 1080p bitrate
                ## -b:v 16500k

                ## 1440p filter
                ## -filter:v "crop=2280:1282:140:109"
                ## 1440p bitrate
                ## -b:v 28750k
                crop_filter = "crop=1710:962:105:82";

                # If the footage is known to come from the dashcam, we want to crop out the nextbase logo
                if is_dashcam_footage:
                    msg_debug_input += " (Dashcam footage)"
                    crop_filter = "crop=2280:1282:140:109"

                print(msg_debug_input)

                new_output_file_path = f'{output_directory}/' + get_new_filename(output_directory, os.path.basename(full_input_file_path))
                msg_debug_output = f'Output :: {new_output_file_path}'
                print(msg_debug_output)

                # Construct the ffmpeg shell command that uses the Apple Silicon GPU cores
                command = (
                    f'ffmpeg -i {full_input_file_path} -map_metadata 0 -map_metadata:s:v 0:s:v -map_metadata:s:a 0:s:a '
                    f'-filter:v crop={crop_filter} -c:v h264_videotoolbox -b:v 28750k -c:a copy '
                    f'{new_output_file_path}'
                )

                print(command)
                print()
                #subprocess.run(command, shell=True)
            else:
                # TODO Maybe add these to some form of log to revisit?
                print(f'Line :: {row} had more than {CSV_INPUT_EXPECTED_ARG_COUNT} arguments')

if __name__ == "__main__":
    # Check if three command-line arguments are provided (script name, file path, and is_dashcam_footage)
    if len(sys.argv) != 3:
        print("Usage: python3 csv_ffmpeg.py <file_path> <is_dashcam_footage>")
        sys.exit(1)

    file_path = sys.argv[1]
    is_dashcam_footage = sys.argv[2].lower() == 'true'

    try:
        process_csv(file_path, is_dashcam_footage)
    except ValueError as e:
        print(f"Error: {e}")
