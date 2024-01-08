from glob import glob
import os
import pandas as pd
from tqdm import tqdm
from tqdm.contrib.concurrent import thread_map

from DataEngine.Audio.DataCollection.downloaders import download_and_extract
from DataEngine.Audio.DataCollection.utils import async_download_urls
from DataEngine.Audio.Utils.audio_utils import cut_audio
from DataEngine.Audio.Utils.generic_utils import convert_audio_file, get_timestamp_from_milliseconds, match_textfiles_list, search_for_text_files
from DataEngine.Audio.DataFilter.snr import wada_snr
from DataEngine.Audio.dataset_information import create_dataset_information


class LjSpeech:
    def __init__(self, path = None, download=False, audio_format: str = "wav"):
        self.path = path
        self.audio_format = audio_format
        
        if self.path is None:
            assert download, "If path is not specified, download must be True."
        
        if download:
            self.path = self._download_ljspeech()
            
        self._preprocess()

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
        headers = ["audio_file", "text", "text_normalized"]
        df.columns = headers
        df['audio_file'] = df['audio_file'].apply(lambda x: os.path.join(self.path, "wavs", f"{x}.wav"))
        
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
            output_file=self.path,
            original_source="https://keithito.com/LJ-Speech-Dataset/",
            description="A public domain speech dataset consisting of 13,100 short audio clips of a single speaker reading passages from 7 non-fiction books. A transcription is provided for each clip."
        )
        print(f"your dataset is ready at {self.path}")
        

class LibriTts:
    def __init__(
        self, 
        path: str = None, 
        download: bool = False, 
        use_libritts_r: bool = False,
        subset: str = "all",
        async_download: bool = False,
        use_normalized_text: bool = False,
        audio_format: str = "wav"
    ):
        self.path = path
        self.libritts_r = use_libritts_r
        self.subset = subset
        self.async_download = async_download
        self.use_normalized_text = use_normalized_text
        self.audio_format = audio_format
        
        if self.path is None:
            assert download, "If path is not specified, download must be True."
        
        if download:
            self.path = self._download_libri_tts()
            
        self._preprocess()
            
            
    def _download_libri_tts(self):
        """Download and extract libri tts dataset.

        Args:
            path (str): Path to the directory where the dataset will be stored.

            subset (str, optional): Name of the subset to download. If you only want to download a certain
            portion specify it here. Defaults to 'all'.
        """
        if self.libritts_r:
            subset_dict = {
                "libri-tts-clean-100": "https://www.openslr.org/resources/141/train_clean_100.tar.gz",
                "libri-tts-clean-360": "http://www.openslr.org/resources/141/train-clean-360.tar.gz",
                "libri-tts-other-500": "http://www.openslr.org/resources/141/train-other-500.tar.gz",
                "libri-tts-dev-clean": "http://www.openslr.org/resources/141/dev-clean.tar.gz",
                "libri-tts-dev-other": "http://www.openslr.org/resources/141/dev-other.tar.gz",
                "libri-tts-test-clean": "http://www.openslr.org/resources/141/test-clean.tar.gz",
                "libri-tts-test-other": "http://www.openslr.org/resources/141/test-other.tar.gz",
                "docs": "https://www.openslr.org/resources/141/doc.tar.gz",
                "failed_restoration_files": "https://www.openslr.org/resources/141/libritts_r_failed_speech_restoration_examples.tar.gz"
            }
        else:
            subset_dict = {
                "libri-tts-clean-100": "http://www.openslr.org/resources/60/train-clean-100.tar.gz",
                "libri-tts-clean-360": "http://www.openslr.org/resources/60/train-clean-360.tar.gz",
                "libri-tts-other-500": "http://www.openslr.org/resources/60/train-other-500.tar.gz",
                "libri-tts-dev-clean": "http://www.openslr.org/resources/60/dev-clean.tar.gz",
                "libri-tts-dev-other": "http://www.openslr.org/resources/60/dev-other.tar.gz",
                "libri-tts-test-clean": "http://www.openslr.org/resources/60/test-clean.tar.gz",
                "libri-tts-test-other": "http://www.openslr.org/resources/60/test-other.tar.gz",
            }

        if self.subset == "all":
            if self.async_download:
                print(" > Downloading all subsets asynchronously...")
                async_download_urls(subset_dict, self.path)
            else:
                for sub, val in subset_dict.items():
                    print(f" > Downloading {sub}...")
                    return download_and_extract(val, self.path)
            print(" > All subsets downloaded")
        else:
            return download_and_extract(subset_dict[self.subset], self.path)
        
    @staticmethod
    def _get_speaker_and_gender(samples, df):
        for sample in samples:
            speaker_id = int(sample['audio_file'].split("/")[-3])
            speaker_row = df[df['READER'] == speaker_id].iloc[0]
            sample['speaker'] = speaker_id
            sample['gender'] = speaker_row['GENDER']
        return samples
    
    
    def _preprocess(self):
        if self.use_normalized_text:
            text_files = [i for i in glob(f"{self.path}/*/*/*/*.txt", recursive=True) if "normalized" in i]
        else:
            text_files = [i for i in glob(f"{self.path}/*/*/*/*.txt", recursive=True) if "normalized" not in i]
        
        audio_files = glob(f"{self.path}/*/*/*/*.wav", recursive=True)
        speakers_df = pd.read_csv(os.path.join(self.path, "speakers.tsv"), delimiter='\t', header=0, index_col=False)
        
        matched_samples = match_textfiles_list(audio_files, text_files)
        
        speaker_samples = self._get_speaker_and_gender(matched_samples, speakers_df)
        if self.audio_format != "wav":
            print(f"Converting audio files to {self.audio_format} format...")
            for row in tqdm(speaker_samples):
                row["audio_file"] = convert_audio_file(row["audio_file"], sample_rate=None, audio_format=self.audio_format)
            print("Done!")
            
        print("Calculating SNR...")
        for row in tqdm(speaker_samples):
            row["snr"] = wada_snr(row["audio_file"])
            
        test_split = [i for i in speaker_samples if "test" in i['audio_file']]
        dev_split = [i for i in speaker_samples if "dev" in i['audio_file']]
        train_split = [i for i in speaker_samples if "train" in i['audio_file']]
        
        df = pd.DataFrame(speaker_samples)
        train_df = pd.DataFrame(train_split)
        test_df = pd.DataFrame(test_split)
        dev_df = pd.DataFrame(dev_split)
        
        df.to_csv(os.path.join(self.path, "metadata.csv"), index=False, sep="|")
        train_df.to_csv(os.path.join(self.path, "train_metadata.csv"), index=False, sep="|")
        test_df.to_csv(os.path.join(self.path, "test_metadata.csv"), index=False, sep="|")
        dev_df.to_csv(os.path.join(self.path, "dev_metadata.csv"), index=False, sep="|")
        
        if self.libritts_r:
            source = "http://www.openslr.org/141/"            
            description = "LibriTTS-R [1] is a sound quality improved version of the LibriTTS corpus (http://www.openslr.org/60/) which is a multi-speaker English corpus of approximately 585 hours of read English speech at 24kHz sampling rate, published in 2019. The constituent samples of LibriTTS-R are identical to those of LibriTTS, with only the sound quality improved. To improve sound quality, a speech restoration model, Miipher proposed by Yuma Koizumi [2], was used. "
        else:
            source = "https://openslr.org/60/"
            description = "LibriTTS is a multi-speaker English corpus of approximately 585 hours of read English speech at 24kHz sampling rate, prepared by Heiga Zen with the assistance of Google Speech and Google Brain team members. The LibriTTS corpus is designed for TTS research. It is derived from the original materials (mp3 audio files from LibriVox and text files from Project Gutenberg) of the LibriSpeech corpus"
        
        create_dataset_information(
            metadata_file=os.path.join(self.path, "metadata.csv"),
            dataset_name="LibriTTS",
            output_file=self.path,
            original_source=source,
            description=description
        )
        
        
class Mailabs:
    def __init__(self, path: str = None, download: bool = False, language: str = "all", async_download: bool = False, audio_format: str = "wav"):
        self.path = path
        self.lang = language
        self.async_download = async_download
        self.audio_format = audio_format
        
        if self.path is None:
            assert download, "If path is not specified, download must be True."
        
        if download:
            self.path = self._download_mailabs()
            
        self._preprocess()
        
    def _download_mailabs(self):
        """Download and extract Mailabs dataset.

        Args:
            path (str): Path to the directory where the dataset will be stored.

            language (str): Language subset to download. Defaults to all .
        """
        if self.path is None:
            self.path = os.path.expanduser('~/.local/share/dataengine/mailabs')
            
        language_dict = {
            "en": "https://data.solak.de/data/Training/stt_tts/en_US.tgz",
            "de": "https://data.solak.de/data/Training/stt_tts/de_DE.tgz",
            "fr": "https://data.solak.de/data/Training/stt_tts/fr_FR.tgz",
            "it": "https://data.solak.de/data/Training/stt_tts/it_IT.tgz",
            "es": "https://data.solak.de/data/Training/stt_tts/es_ES.tgz",
            "en-uk": "https://data.solak.de/data/Training/stt_tts/en_UK.tgz",
            "uk": "https://data.solak.de/data/Training/stt_tts/uk_UK.tgz",
            "ru": "https://data.solak.de/data/Training/stt_tts/ru_RU.tgz",
            "pl": "https://data.solak.de/data/Training/stt_tts/pl_PL.tgz",
        }
        if self.lang == "all":
            if self.async_download:
                print(" > Downloading all languages asynchronously...")
                async_download_urls(language_dict, self.path)
            else:
                for lang, url in language_dict.items():
                    print(f" > Downloading {lang}...")
                    return download_and_extract(url, self.path)
        else:
            url = language_dict[self.lang]
            return download_and_extract(url, self.path)
        
    @staticmethod
    def _reformat_metadata(metadata_path):
        metadata_root = os.path.dirname(metadata_path)
        df = pd.read_csv(metadata_path, sep="|", header=None)
        headers = ["audio_file", "text", "text_normalized"]
        df.columns = headers
        df['audio_file'] = df['audio_file'].apply(lambda x: os.path.join(metadata_root, "wavs", f"{x}.wav"))
        df['speaker'] = metadata_path.split("/")[-3]
        df['lang'] = metadata_path.split("/")[-6]
        df['gender'] = metadata_path.split("/")[-4]
        df['book'] = metadata_path.split("/")[-2]
        df_dict = df.to_dict(orient="records")
        return df_dict
    
    def _preprocess(self):
        files = glob(f"{self.path}/**/metadata.csv", recursive=True)
        
        all_metadata = []
        for f in tqdm(files):
            all_metadata.extend(self._reformat_metadata(f))
            
        if self.audio_format != "wav":
            print(f"Converting audio files to {self.audio_format} format...")
            for row in tqdm(all_metadata):
                row["audio_file"] = convert_audio_file(row["audio_file"], sample_rate=None, audio_format=self.audio_format)
            print("Done!")
            
        print("Calculating SNR...")
        for row in tqdm(all_metadata):
            try:
                row["snr"] = wada_snr(row["audio_file"])
            except Exception as e:
                print(f"{e} for {row['audio_file']}")
                row["snr"] = -1.0
            
        df = pd.DataFrame(all_metadata)
        
        df.to_csv(os.path.join(self.path, "metadata.csv"), index=False, sep="|")
        
        create_dataset_information(
            metadata_file=os.path.join(self.path, "metadata.csv"),
            dataset_name="Mailabs",
            output_file=self.path,
            original_source="https://www.caito.de/2019/01/03/the-m-ailabs-speech-dataset/",
            description="The M-AILABS Speech Dataset is the first large dataset that we are providing free-of-charge, freely usable as training data for speech recognition and speech synthesis."
        )
        
        
class Tedlium:
    def __init__(self, path: str = None, download: bool = False,  audio_format: str = "wav", workers: int = 8):
        self.path = path
        self.audio_format = audio_format
        self.workers = workers
        
        if self.path is None:
            assert download, "If path is not specified, download must be True."
        
        if download:
            self.path = self._download_tedlium()
            
        self._preprocess()
        
    def _download_tedlium(self):
        """
        Downloads the TED-LIUM dataset into a specified output path.
        https://www.openslr.org/51/

        Parameters:
        out_path (str): The path to the directory where the dataset will be saved and extracted.
        """
        url = "https://www.openslr.org/resources/51/TEDLIUM_release-3.tgz"
        return download_and_extract(url, self.path)
    
    def _preprocess(self):
        os.makedirs(os.path.join(self.path, "audio_segments"), exist_ok=True)
        audio_files = glob(f"{self.path}/data/sph/*.sph", recursive=True)
        audio_samples = [{"audio_file": f} for f in audio_files]
        text_pairs = search_for_text_files(audio_samples, self.path, text_file_extension="stm", read_text_file=False)
        for sample in text_pairs:
            text_file = sample['text_file']
            processed_lines = self._process_text_file(text_file)
            sample['text_output'] = processed_lines
        
        all_samples = thread_map(self._process_audio_and_text, text_pairs, max_workers=self.workers, chunksize=self.workers // 2)
        
        total_samples = []
        for samples in all_samples:
            for y in samples:
                total_samples.append(y)
        
        print("Calculating SNR...")
        for row in tqdm(total_samples):
            row["snr"] = wada_snr(row["audio_file"])
                        
        df = pd.DataFrame(total_samples)
        df.to_csv(os.path.join(self.path, "metadata.csv"), index=False, sep="|")
        
        create_dataset_information(
            metadata_file=os.path.join(self.path, "metadata.csv"),
            dataset_name="TED-LIUM",
            output_file=self.path,
            original_source="https://www.openslr.org/51/",
            description="TED-LIUM is an open source database for speech research, and especially targeted at speech recognition. It contains audio and aligned transcriptions for 1499 TED talks that are freely available on the TED website. The database is released under the Creative Commons license CC BY-NC-ND 3.0 (Attribution-NonCommercial-NoDerivs).",
        )

    @staticmethod
    def _process_line(line):
        metadata, text = line.split("<NA>")
        metadata_list = metadata.strip().split(" ")
        formatted_text = text.strip().replace("\n", "").replace("<unk>", "").strip()
        metadata_list.append(formatted_text)
        return metadata_list
    
    def _process_text_file(self, text_file):
        with open(text_file, mode='r', encoding='utf-8') as file:
            lines = file.readlines()
        processed_lines = []
        for line in lines:
            processed_line = self._process_line(line)
            processed_lines.append(processed_line)
        return processed_lines
    
    @staticmethod
    def seconds_to_milliseconds(seconds):
        milliseconds = seconds * 1000
        return int(milliseconds)
    
    def _process_stamp(self, stamp, audio):
        start_seconds = float(stamp[-3])
        end_seconds = float(stamp[-2])
        text = stamp[-1]
        
        start_milliseconds = self.seconds_to_milliseconds(start_seconds)
        end_milliseconds = self.seconds_to_milliseconds(end_seconds)
        
        start_timestamp = get_timestamp_from_milliseconds(start_milliseconds)
        end_timestamp = get_timestamp_from_milliseconds(end_milliseconds)
        
        audio_clip = cut_audio(audio, start_timestamp, end_timestamp, output_folder=os.path.join(self.path, "audio_segments"))
        
        return {
            "audio_file": audio_clip,
            "text": text,
            "start_timestamp": start_timestamp,
            "end_timestamp": end_timestamp,
            "orig_audio_file": audio
        }
        
    def _process_audio_and_text(self, sample):
        try:
            temp_audio = convert_audio_file(sample['audio_file'], audio_format=self.audio_format)
            stamps = sample['text_output']
            processed_stamps = [self._process_stamp(stamp, temp_audio) for stamp in stamps]
            os.remove(temp_audio)
            return processed_stamps
        except Exception as e:
            print(f"Error processing sample: {sample}")
            print(e)
            return None
