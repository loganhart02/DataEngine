import re
import os
from tqdm import tqdm


def match_textfiles_list(audio_files, text_files, samples_list=None): 
    files_map = {}
    for audio_file in tqdm(audio_files):
        base_name = os.path.basename(audio_file).split(".")[0]
        files_map[base_name] = {'audio_file': audio_file, 'text': None}
    for text_file in text_files:
        base_name = os.path.basename(text_file).split(".")[0]
        if base_name in files_map:
            with open(text_file, "r", encoding='utf-8') as text:
                transcript = text.read().replace("\n", "")
                files_map[base_name]['text'] = transcript
    matched_files = [f for f in files_map.values() if f['text'] is not None]
    return matched_files


#TODO: make this faster!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def search_for_text_files(
    audio_samples,
    root_data_path: str,
    text_file_extension: str = "txt",
    read_text_file: bool = False
):

    print("Searching for text files...")
    matched_samples = []
    for i in tqdm(range(len(audio_samples))):
        sample = audio_samples[i]
        audio_file = sample['audio_file']
        base_name = os.path.splitext(os.path.basename(audio_file))[0]
        base_name_regex = re.compile(r'^' + re.escape(base_name) + r'\.'+text_file_extension+'$')
        for subdir, _, files in os.walk(root_data_path):
            for file in files:
                if base_name_regex.match(file):
                    text_file = os.path.join(subdir, file)
                    if read_text_file is True:
                        with open(text_file, "r", encoding='utf-8') as text:
                            transcript = text.read().replace("\n", "")
                            sample['text'] = transcript
                            
                    sample['text_file'] = text_file
                    matched_samples.append(sample)
    unique_dicts = {frozenset(d.items()) for d in matched_samples}
    matched_samples = [dict(items) for items in unique_dicts]
    print(f"Found {len(matched_samples)} text files for {len(audio_samples)} audio files")
    return matched_samples


def get_timestamp_from_milliseconds(milliseconds: int):
    hours = int(milliseconds / (60 * 60 * 1000))
    milliseconds = milliseconds - hours * (60 * 60 * 1000)
    minutes = int(milliseconds / (60 * 1000))
    milliseconds = milliseconds - minutes * (60 * 1000)
    seconds = int(milliseconds / 1000)
    milliseconds = milliseconds - seconds * 1000
    return "%s:%s:%s.%s" % (
        str(hours).zfill(2),
        str(minutes).zfill(2),
        str(seconds).zfill(2),
        str(milliseconds).zfill(3),
    )