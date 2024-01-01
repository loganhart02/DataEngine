import os
import pandas as pd
from tqdm import tqdm

from DataEngine.Audio.DataCollection.downloaders import download_and_extract
from DataEngine.Audio.DataCreation.utils import convert_audio_file
from DataEngine.Audio.DataFilter.snr import wada_snr
from DataEngine.Audio.dataset_information import create_dataset_information


class LjSpeech:
    def __init__(self, path, download=False, audio_format: str = "wav"):
        self.path = path
        self.audio_format = audio_format
        
        if download:
            self.path = self._download_ljspeech()

    def _download_ljspeech(self):
        """
        Downloads the LJ Speech dataset into a specified output path.
        https://keithito.com/LJ-Speech-Dataset/

        Parameters:
        out_path (str): The path to the directory where the dataset will be saved and extracted.
        """
        url = "https://data.keithito.com/data/speech/LJSpeech-1.1.tar.bz2"
        return download_and_extract(url, self.path)
    
    def _preprocess(self):
        df = pd.read_csv(os.path.join(self.path, "metadata.csv"), sep="|", header=None)
        headers = ["audio_file", "text"]
        df.columns = headers
        df['audio_file'] = df['audio_file'].apply(lambda x: os.path.join(self.path, x))
        
        df_dict = df.to_dict(orient="records")
        if self.audio_format != "wav":
            print(f"Converting audio files to {self.audio_format} format...")
            for row in tqdm(df_dict):
                row["audio_file"] = convert_audio_file(row["audio_file"], sample_rate=None, audio_format=self.audio_format)
            print("Done!")
        
        print("Calculating SNR...")
        for row in tqdm(df_dict):
            row["snr"] = wada_snr(row["audio_file"])
                        
        df = pd.DataFrame(df_dict)
        df.to_csv(os.path.join(self.path, "metadata.csv"), index=False, sep="|")
        
        create_dataset_information(
            metadata_file=os.path.join(self.path, "metadata.csv"),
            dataset_name="LJ Speech",
            output_file=os.path.join(self.path, "dataset_information.md"),
            original_source="https://keithito.com/LJ-Speech-Dataset/",
            description="A public domain speech dataset consisting of 13,100 short audio clips of a single speaker reading passages from 7 non-fiction books. A transcription is provided for each clip."
        )
        
    
        
    
        
