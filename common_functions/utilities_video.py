#!/usr/bin/env python3

import subprocess
import json
from common_functions.utilities_system import get_cpu_info, get_gpu_info

## FFPROBE Helpers

def get_video_bitrate(file_path):
    try:
        # Run ffprobe command to get video information
        command = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=bit_rate',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            file_path
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        # Parse the output to get the bitrate as a string
        bitrate_str = result.stdout.strip()
        return bitrate_str
    except subprocess.CalledProcessError as e:
        print(f"Error running ffprobe: {e}")
        return None
    
    
def get_video_codec(file_path):
    cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_name', '-of', 'json', file_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Parse the JSON output
    try:
        data = json.loads(result.stdout)
        codec_name = data['streams'][0]['codec_name']
        return codec_name
    except (json.JSONDecodeError, KeyError, IndexError):
        return None


def get_ffmpeg_video_codec_arg_for_video(input_file):
    input_codec = get_video_codec(input_file)
    NVIDIA = 'NVIDIA'
    APPLE = 'APPLE'

    if input_codec == 'h264':
        # H.264 codec detected
        if NVIDIA in get_gpu_info():
            return 'h264_nvenc'
        elif APPLE in get_gpu_info():
            return 'h264_videotoolbox'
        else:
            raise ValueError("Unsupported GPU or architecture for H.264 encoding")
    elif input_codec == 'hevc':
        # HEVC codec detected
        if NVIDIA in get_gpu_info():
            return 'hevc_nvenc'
        elif APPLE in get_gpu_info():
            return 'hevc_videotoolbox'
        else:
            raise ValueError("Unsupported GPU or architecture for HEVC encoding")
    else:
        raise ValueError("Unsupported or unknown video codec")


def get_resolution(file_path):
    """ 
        Uses ffprobe to return a tuple (boolean,boolean,int) representing if the file provided is_1080p, is_1440p, bit_rate
    """
    command = f'ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 {file_path}'
    result = subprocess.check_output(command, shell=True, text=True)
    width, height = map(int, result.strip().split(','))

    is_1080p = width == 1920 and height == 1080
    is_1440p =  width == 2560 and height == 1440

    return is_1080p, is_1440p


def is_valid_time_range(file_path, start_time, end_time):
    """
        Returns True IFF the start and end time exists within the bounds of the video file provided.
    """
    try:
        # Run ffprobe to get information about the video file
        cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Parse the duration from the ffprobe output
        duration = float(result.stdout)

        # Check if start_time and end_time are within the valid range
        return 0 <= start_time <= duration and 0 <= end_time <= duration and start_time < end_time

    except (ValueError, subprocess.CalledProcessError):
        return False

## FFMPEG Helpers

def get_available_hwaccels() -> list[str]:
    """
        Return a list of hardware acceleration options available to ffmpeg
    """
    try:
        result = subprocess.run(['ffmpeg', '-hide_banner', '-hwaccels'], capture_output=True, text=True)
        return result.stdout.strip().split('\n')[1:]
    except FileNotFoundError:
        return []


def get_ffmpeg_encoder_str(hwaccels_options, encoder) -> str:
    """
        For a list of hardware acceleration options available
        return an appropriate string value for ffmpeg to utilise

        Returns None if hwaccels_options is empty or encoder is not available on this machine
    """
    # if 'cuda' in hwaccels_options and encoder == 'h264_nvenc':
    #     return 'h264_nvenc'
    # elif encoder in hwaccels_options:
    #     return encoder
    # else:
    #     return None

    if 'cuda' in hwaccels_options and encoder == 'h264_nvenc':
        return 'cuda'
    elif 'vaapi' in hwaccels_options and encoder == 'h264_vaapi':
        return 'h264_vaapi'
    elif encoder in hwaccels_options:
        return encoder
    else:
        return None
    

def get_hw_encoder() -> str:
    """
        Return one of the two known hardware accel options otherwise throw exception
        NB. Apple silicin or NVidia 3050Ti
    """
    # Establish what hardware accel we have available to us
    available_hwaccels = get_available_hwaccels()
    chosen_encoder = get_ffmpeg_encoder_str(available_hwaccels, 'h264_videotoolbox') # Apple Silicon expected value
    if not chosen_encoder:
        chosen_encoder = get_ffmpeg_encoder_str(available_hwaccels, 'h264_nvenc') # Dell XPS NVidia 3050Ti expected value

    if not chosen_encoder:
        # None of two hardware acceleration options we prefer are available to lets back out
        raise ValueError("No suitable hardware-accelerated encoder found.")

    return chosen_encoder
