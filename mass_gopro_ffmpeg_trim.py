#!/usr/bin/env python3

## TODO : If no end time is provided; detect this and assume you want dynamically obtain the end time as to ensure not even a ms is lost of footage
import os
import csv
import sys
import subprocess
from common_functions.utilities_video import *
from common_functions.utilities_file import *


NEW_OUTPUT_DIR_NAME = "ffmpeg_trimmed"
CSV_INPUT_EXPECTED_ARG_COUNT = 3


def process_row(row: [str], common_directory: str, output_directory: str):
    """
        For a given row of data, input video file path, output file directory location and available hardware acceleration
        Append the file name from the row, to the input file directory location and attempt to crop to known sizes and remove
        the nextbase logo and output the new asset at a similar location.
    """
    if len(row) != CSV_INPUT_EXPECTED_ARG_COUNT:
        print(f'Line :: {row} had more than {CSV_INPUT_EXPECTED_ARG_COUNT} arguments')
    else: 
        filename, start_time, end_time = row[0], row[1], row[2]
        
        # We don't know the full file path to the input; we assume it
        # lives in the same dir as the csv file provided.
        # Construct the full input video file path combining the known
        # common directory provided and the filename from the csv file
        video_input_path = os.path.join(common_directory, filename)
        
        # Construct the full output video file path combining the known
        # common directory provided and a newly generated filenamefor the output
        new_output_file_path = gen_new_filepath(output_directory, os.path.basename(filename),'mp4')

        # We now know what the input is and what the output will 
        # be print them to the console for convenience.
        print(f"Input :: {video_input_path}")
        print(f'Output :: {new_output_file_path}')

        ## TODO validation
        # if is_valid_time_range(full_input_file_path,start_time,end_time):
        #     print("time range deemed valid")

        # Need to dynamically obtain some values to plug into FFMPEG
        ffmpeg_v_codec_arg = get_ffmpeg_video_codec_arg_for_video(video_input_path)
        orig_video_bitrate = get_video_bitrate(video_input_path)

        command = (
            f'ffmpeg -i \'{video_input_path}\' -ss {start_time} -to {end_time} -c copy -map_metadata 0 '
            f'\'{new_output_file_path}\''
        )

        print("\nCommand :: " + command)
        print()
        # ffmpeg -i '/Users/ryan/Desktop/PHT - Spain & Portugal 23/GoPro - Day 1&2/GX010037.MP4' -ss 00:01:11 -to 00:01:54 -c copy -map_metadata 0 '/Users/ryan/Desktop/PHT - Spain & Portugal 23/GoPro - Day 1&2/ffmpeg_trimmed/GX010037.mp4'
        subprocess.run(command, shell=True)


def process_csv(csv_file_path):
    if not is_csv_file(csv_file_path):
        raise ValueError("The provided file is not a CSV file.")

    with open(csv_file_path, 'r') as csv_file:
        # In the same location as the csv file provided, 
        # create a directory named 'ffmpeg_cropped' and use 
        # it as an output location for the new video assets
        common_directory = os.path.dirname(csv_file_path)
        output_directory = os.path.join(common_directory, NEW_OUTPUT_DIR_NAME)
        os.makedirs(output_directory, exist_ok=True)

        # Now loop through the contents of the csv file
        csv_reader = csv.reader(csv_file)
        next(csv_reader,None) # skip first row 
        for row in csv_reader:
            process_row(row, common_directory, output_directory)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 mass_ffmpeg_trim.py <fully_qualified_file_path>")
        sys.exit(1)

    try:
        process_csv(sys.argv[1])
    except ValueError as e:
        print({e})
