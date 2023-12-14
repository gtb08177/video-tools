#!/usr/bin/env python3

import os
import csv
import sys
import subprocess
import platform

NEW_OUTPUT_DIR_NAME = "ffmpeg_cropped"
CSV_INPUT_EXPECTED_ARG_COUNT = 1

def is_csv_file(file_path):
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


def get_resolution_and_bitrate(file_path):
    """ 
        Uses ffprobe to return a tuple (boolean,boolean,int) representing if the file provided is_1080p, is_1440p, bit_rate
    """
    # Use ffprobe to get video resolution and bitrate
    command = f'ffprobe -v error -select_streams v:0 -show_entries stream=width,height,bit_rate -of csv=p=0 {file_path}'
    result = subprocess.check_output(command, shell=True, text=True)
    width, height, bit_rate = map(int, result.strip().split(','))

    is_1080p = width == 1920 and height == 1080
    is_1440p =  width == 2560 and height == 1440

    return is_1080p, is_1440p, bit_rate


def get_available_hwaccels():
    try:
        result = subprocess.run(['ffmpeg', '-hide_banner', '-hwaccels'], capture_output=True, text=True)
        return result.stdout.strip().split('\n')[1:]
    except FileNotFoundError:
        return []


def use_hwaccel_for_encoder(hwaccels, encoder):
    if 'cuda' in hwaccels and encoder == 'h264_nvenc':
        return 'h264_nvenc'
    elif encoder in hwaccels:
        return encoder
    else:
        return None
    

def process_csv(csv_file_path):
    if not is_csv_file(csv_file_path):
        raise ValueError("The provided file is not a CSV file.")

    # Establish what hardware accel we have available to us
    available_hwaccels = get_available_hwaccels()
    chosen_encoder = use_hwaccel_for_encoder(available_hwaccels, 'h264_videotoolbox')
    if not chosen_encoder:
        chosen_encoder = use_hwaccel_for_encoder(available_hwaccels, 'h264_nvenc')

    if chosen_encoder:
        print(f"Using hardware-accelerated encoder: {chosen_encoder}")
    else:
        raise ValueError("No suitable hardware-accelerated encoder found.")

    with open(csv_file_path, 'r') as csv_file:
        # Create a directory named 'ffmpeg_cropped' in the same location
        # as the CSV file and use it as an output location for the new assets
        output_directory = os.path.join(os.path.dirname(csv_file_path), NEW_OUTPUT_DIR_NAME)
        os.makedirs(output_directory, exist_ok=True)

        # now process the contents of the csv file
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            if len(row) == CSV_INPUT_EXPECTED_ARG_COUNT:
                filename = row[0]
                #start_time, end_time =  row[1], row[2]
                
                # Construct the full file path for the input
                full_input_file_path = os.path.join(os.path.dirname(csv_file_path), filename)
                
                # Establish some traits about the video
                is_1080p, is_1440p, bit_rate = get_resolution_and_bitrate(full_input_file_path)

                crop_filter = ""                
                if is_1080p:
                    crop_filter = "1710:962:105:82"
                    bit_rate = "16500k"
                elif is_1440p:
                    crop_filter = "2280:1282:140:109"
                    bit_rate = "28750k"
                else:
                    raise ValueError(f'File {full_input_file_path} is neither 1080p or 1440p and therefore unsure how to handle.')

                new_output_file_path = f'{output_directory}/' + get_new_filename(output_directory, os.path.basename(full_input_file_path))

                # We now have all we need to feed into ffmpeg, so give a printout to help show this
                print(f"Input :: {full_input_file_path}")
                print(f'Output :: {new_output_file_path}')

                # Construct the ffmpeg shell command that uses the Apple Silicon GPU cores
                command = (
                    f'ffmpeg -i {full_input_file_path} -map_metadata 0 -map_metadata:s:v 0:s:v -map_metadata:s:a 0:s:a '
                    f'-filter:v crop={crop_filter} -c:v {chosen_encoder} -b:v {bit_rate} -c:a copy '
                    f'{new_output_file_path}'
                )

                print("\n" + command)
                print()
                subprocess.run(command, shell=True)
            else:
                # TODO Maybe add these to some form of log to revisit?
                print(f'Line :: {row} had more than {CSV_INPUT_EXPECTED_ARG_COUNT} arguments')

if __name__ == "__main__":
    # Check if three command-line arguments are provided (script name and file path)
    if len(sys.argv) != 2:
        print("Usage: python3 csv_ffmpeg.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        process_csv(file_path)
    except ValueError as e:
        print(f"Error: {e}")
