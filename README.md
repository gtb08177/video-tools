# video-tools
A repo for capturing all things video tool related.
Currently focused on combing the power of `ffmpeg` with my current Dell XPS (w/ NVidia) and Apple Silicon (M1 Pro) GPU hardware acceleration to make light work of trimming videos from dashcams and GoPro devices.

## GoPro Footage Trimming
Executing `mass_gopro_ffmpeg_trim.py`, you can provide a fully qualified csv file location and each row within that csv will be processed (with the exception of the first row).
The csv file location should be placed alongside the video files you intend to trim e.g.
```
/videos/video_trim_details.csv
/videos/GX010115.MP4
/videos/GX010116.MP4
```
The expected format of the csv can be seen in [examples/mass_gopro_ffmpeg_trim_input.csv](./example/mass_gopro_ffmpeg_trim_input.csv)

The example shows that file `/videos/GX010115.MP4` will be cropped in a new file, starting at 53 seconds in the original through to 1 minute and 55 seconds.

NB, the original footage will not be altered or deleted.
<br/>
NB, the output directory for the new assets will live in the same directory as the original content i.e. `/videos/ffmpeg_trimmed/GX010115.MP4`

There is logic to handle multiple output files from the same input file; these filenames will have a counter in there file name.


## Nextbase Footage Logo Removal
Having owned a Nextbase 512GW dashboard camera; all footage from this device has an annoying Nextbase logo in the top corner.
The script named `nextbase_logo_removal.py` takes a fully qualified csv file location (similar to the GoPro script) and will process each row of data within it one at a time.

The expected format of the csv can be seen in [examples/nextbase_logo_removal_input.csv](./example/nextbase_logo_removal_input.csv)

The script itself only supports 1080p or 1440p Nextbase videos files as that was all that was required at time of writing.

NB, the original footage will not be altered or deleted.
<br/>
NB, the output directory for the new assets will live in the same directory as the original content

## Testing
There is currently no means of testing other than validating with the human eye that the video outputs are good inbetween code changes.
This was a conscious decision as not to include any video media within the repos that would cause the repo size to be an obscene size.