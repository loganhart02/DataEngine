import os
import re
from subprocess import call, DEVNULL, STDOUT, check_output
import soundfile as sf


def get_sample_rate(audio_path):
    info = sf.info(audio_path)
    return info.samplerate


def convert_audio_file(
    audio_path, 
    bitrate="16k", 
    sample_rate=16000, 
    audio_format="wav"
):
    assert os.path.exists(audio_path), f"Audio file {audio_path} does not exist!"
    assert os.path.isfile(audio_path), f"Audio path {audio_path} is not a file!"
    if sample_rate is None:
        sample_rate = get_sample_rate(audio_path)
    
    output_path = os.path.splitext(audio_path)[0] + f"_{str(sample_rate)}_{str(bitrate)}.{audio_format}"
    if os.path.isfile(output_path):
        print("WARNING: overwriting:", output_path)
        os.remove(output_path)
        
    check_output(
        [
            "ffmpeg",
            "-i",
            audio_path,
            "-b:a",
            bitrate,
            "-ac",
            "1",
            "-map",
            "a",
            "-ar",
            str(sample_rate),
            output_path,
            "-loglevel",
            "error",
            "-hide_banner"
        ]
    )
    return output_path


def cut_audio(input_path: str, start: str, end: str, output_folder: str, output_name: str = None):
    def _timestamp_to_filename(timestamp):
        return re.sub("[^0-9]", "", timestamp)

    assert os.path.isfile(input_path), f"{input_path} does not exist"

    if output_name is None:
        input_path_basename = os.path.splitext(os.path.basename(input_path))
        extension = input_path_basename[1]
        input_path_basename = input_path_basename[0]
        output_name = f"{input_path_basename}_{_timestamp_to_filename(start)}_{_timestamp_to_filename(end)}{extension}"

    output_path = os.path.join(output_folder, output_name)

    if os.path.isfile(output_path):
        print("WARNING: overwriting:", output_path)
        os.remove(output_path)

    call(
        ["ffmpeg", "-ss", start, "-to", end, "-i", input_path, output_path],
        stdout=DEVNULL,
        stderr=STDOUT,
    )
    return output_path