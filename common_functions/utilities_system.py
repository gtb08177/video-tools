#!/usr/bin/env python3

import subprocess

def get_gpu_info():
    try:
        # Run the 'ffmpeg' command with the '-hide_banner' and '-hwaccels' options
        result = subprocess.run(['ffmpeg', '-hide_banner', '-hwaccels'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Check if the output contains information about GPU acceleration methods
        if 'cuda' in result.stdout:
            return 'NVIDIA'
        elif 'videotoolbox' in result.stdout:
            return 'APPLE'
        else:
            return None

    except Exception as e:
        return f"Error getting GPU info: {str(e)}"

def get_cpu_info():
    # Get CPU information using system commands
    try:
        result = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout
    except Exception as e:
        return f"Error getting CPU info: {str(e)}"