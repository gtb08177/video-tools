#!/usr/bin/env python3
import subprocess


## FFPROBE Helpers
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
    if 'cuda' in hwaccels_options and encoder == 'h264_nvenc':
        return 'h264_nvenc'
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
