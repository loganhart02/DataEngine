import os
import re
import json
from tqdm import tqdm
import pandas as pd
from pydub import AudioSegment


def get_audio_length(audio_path: str):
    """
    Retrieves the duration of an audio file in seconds.

    Parameters:
        - audio_path (str): The path to the audio file.

    Returns:
        - float: The duration of the audio file in seconds.

    Example:
        >>> get_audio_length('audio.wav')
        10.5
    """
    try:
        audio_file = AudioSegment.from_file(audio_path)
        duration_in_ms = len(audio_file)
        duration_in_sec = duration_in_ms / 1000
        return duration_in_sec, audio_file.frame_rate
    except:
        print(f"Error: {audio_path} is not a valid audio file or corrupt. marking as -1 length")
        return -1, -1
    

def get_audio_lengths(metadata_file: str):
    print("getting audio lengths...")
    df = pd.read_csv(metadata_file, sep="|")
    df_dict = df.to_dict(orient="records")
    for row in tqdm(df_dict):
        length, sample_rate = get_audio_length(row["audio_file"])
        row["audio_len"] = length
        row["sample_rate"] = sample_rate
    df = pd.DataFrame(df_dict)
    print("Done!")
    return df 



def create_dataset_information(
    metadata_file: str, 
    dataset_name: str, 
    output_file: str,
    original_source: str = "Fill this in if you want",
    description: str = "Fill this in if you want",
):
    df = get_audio_lengths(metadata_file)
    num_corrupt_files = len(df[df["audio_len"] == -1])

    markdown_content = f"""
# {dataset_name}
metadata file: `{metadata_file}`
    
## Original Source
`{original_source}`
    
## Description
{description}
    
## Dataset Information
    
### Total Number of Samples
`{len(df)}`
    
### Number of Corrupt Files
`{num_corrupt_files}`
    
### Audio Durations
Total Duration: `{df["audio_len"].sum() / 3600}` Hours

Max Duration: `{df["audio_len"].max()}` Seconds

Min Duration: `{df['audio_len'].min()}` Seconds

Average Duration: `{df["audio_len"].mean()}` Seconds
    
### Number of Speakers
`{len(df["speaker"].unique()) if "speaker" in df.columns else 1}`
    
### Number of Emotions
`{len(df["emotion"].unique()) if "emotion" in df.columns else 0}`
    
### Sample Rates
`{df["sample_rate"].unique().tolist()}`
    
### Audio Format
`{os.path.splitext(df["audio_file"].iloc[0])[1]}`
    
### Metadata Lables
`{df.columns.tolist()}`
    
# TODOs
- [ ] Add more information
    
# Notes
- [ ] Add more notes
    """
    with open(os.path.join(output_file, "dataset_card.md"), "w") as f:
        f.write(markdown_content)

    
    