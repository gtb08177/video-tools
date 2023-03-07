#!/bin/zsh

# Helper script to utilise FFMPeg
# Example of 1080p conversion
#➜ ffmpeg -i Day\ One\ -\ French\ Motorway\ Cut\ -\ Richard\ and\ Sam\ Rolling.mov -filter:v "crop=1710:962:105:82" -c:a copy test.mov  

# Example FIND command
# find /Volumes/Ryan/PHT\ -\ Alps\ \&\ Pyrenees\ \'22\ -\ Mid\ Review  -type d -iname "dashcam"

# TODO utilise command line parameters including if 1080p or 1440p
srce_loc="/Volumes/Ryan/Driving Footage/San Bernardino & Splugen Pass/Dashcam"
dest_loc="/Volumes/Ryan/Driving Footage/San Bernardino & Splugen Pass/Dashcam_FFMPEG_CROPPED_FIXED"

# Create the dest dir if it do not exist
mkdir -p $dest_loc
cd $srce_loc


## 1080p filter
## -filter:v "crop=1710:962:105:82"
## 1080p bitrate
## -b:v 16500k

## 1440p filter
## -filter:v "crop=2280:1282:140:109"
## 1440p bitrate
## -b:v 28750k


# 1080p w/ bitrate
#for f in *; do echo "Cropping $f file..."; ffmpeg -i $f -map_metadata 0 -map_metadata:s:v 0:s:v -map_metadata:s:a 0:s:a -filter:v "crop=1710:962:105:82" -c:v h264_videotoolbox -b:v 16500k -c:a copy $dest_loc/$f; echo "\n\n"; done

# 1440p w/ bitrate
for f in *; do echo "Cropping $f file..."; ffmpeg -i $f -map_metadata 0 -map_metadata:s:v 0:s:v -map_metadata:s:a 0:s:a -filter:v "crop=2280:1282:140:109" -c:v h264_videotoolbox -b:v 28750k -c:a copy $dest_loc/$f; echo "\n\n"; done
