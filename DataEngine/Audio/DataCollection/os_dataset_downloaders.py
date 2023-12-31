import os
from typing import Optional

from .utils import download_kaggle_dataset, download_url, extract_archive, async_download_urls


def download_and_extract(out_path: str, url: str):
    """
    Downloads a file from a given URL and extracts it into a specified output path.

    Parameters:
    out_path (str): The path to the directory where the downloaded file will be saved and extracted.
    url (str): The URL of the file to be downloaded.
    """
    os.makedirs(out_path, exist_ok=True)
    print(f" > Downloading {url}...")
    download_url(url, out_path)
    basename = os.path.basename(url)
    archive = os.path.join(out_path, basename)
    print(f" > Extracting {archive} file...")
    extract_archive(archive)
    
    
def download_ljspeech(out_path: str):
    """
    Downloads the LJ Speech dataset into a specified output path.
    https://keithito.com/LJ-Speech-Dataset/

    Parameters:
    out_path (str): The path to the directory where the dataset will be saved and extracted.
    """
    url = "https://data.keithito.com/data/speech/LJSpeech-1.1.tar.bz2"
    download_and_extract(out_path, url)
    

def download_daps(out_path: str):
    """
    Downloads the DAPS dataset into a specified output path.
    https://zenodo.org/records/4660670

    Parameters:
    out_path (str): The path to the directory where the dataset will be saved and extracted.
    """
    url = "https://zenodo.org/records/4660670/files/daps.tar.gz?download=1"
    download_and_extract(out_path, url)
    

def download_thorsten_de(out_path: str):
    """
    Downloads the Thorsten German Speech dataset into a specified output path.
    https://www.openslr.org/resources/95

    Parameters:
    out_path (str): The path to the directory where the dataset will be saved and extracted.
    """
    url = "https://www.openslr.org/resources/95/thorsten-de_v02.tgz"
    download_and_extract(out_path, url)
    

def download_tweb(out_path: str):
    """
    Downloads the World English Bible Speech dataset from Kaggle into a specified output path.

    Parameters:
    out_path (str): The path to the directory where the dataset will be saved.

    Note:
    This function assumes the presence of `download_kaggle_dataset` function 
    which handles the downloading of datasets from Kaggle.
    """
    download_kaggle_dataset("bryanpark/the-world-english-bible-speech-dataset", "TWEB", out_path)
    
    
def download_tedlium(out_path: str):
    """
    Downloads the TED-LIUM dataset into a specified output path.
    https://www.openslr.org/51/

    Parameters:
    out_path (str): The path to the directory where the dataset will be saved and extracted.
    """
    url = "https://www.openslr.org/resources/51/TEDLIUM_release-3.tgz"
    download_and_extract(out_path, url)
    

def download_hifi_tts(out_path: str):
    """
    Hi-Fi Multi-Speaker English TTS Dataset (Hi-Fi TTS) is a multi-speaker English dataset.
    https://www.openslr.org/resources/109/

    Parameters:
    out_path (str): The path to the directory where the dataset will be saved and extracted.
    """
    url = "https://www.openslr.org/resources/109/hi_fi_tts_v0.tar.gz"
    download_and_extract(out_path, url)
    

def download_libri_light(out_path: str, size: str = "small"):
    url_dict = {
        "small": "https://dl.fbaipublicfiles.com/librilight/data/small.tar",
        "medium": "https://dl.fbaipublicfiles.com/librilight/data/medium.tar",
        "large": "https://dl.fbaipublicfiles.com/librilight/data/large.tar",
        "duplicated": "https://dl.fbaipublicfiles.com/librilight/data/duplicate.tar"
    }
    print(f" > Downloading {size}...")
    download_and_extract(out_path, url_dict[size])
    
    
def download_vctk(path: str, use_kaggle: Optional[bool] = False):
    """Download and extract VCTK dataset.

    Args:
        path (str): path to the directory where the dataset will be stored.

        use_kaggle (bool, optional): Downloads vctk dataset from kaggle. Is generally faster. Defaults to False.
    """
    if use_kaggle:
        download_kaggle_dataset("mfekadu/english-multispeaker-corpus-for-voice-cloning", "VCTK", path)
    else:
        url = "https://datashare.ed.ac.uk/bitstream/handle/10283/3443/VCTK-Corpus-0.92.zip"
        download_and_extract(path, url)
    
    
def download_libri_tts(
    path: str, 
    subset: Optional[str] = "all", 
    async_download: Optional[bool] = False,
    download_libri_tts_r: Optional[bool] = False
):
    """Download and extract libri tts dataset.

    Args:
        path (str): Path to the directory where the dataset will be stored.

        subset (str, optional): Name of the subset to download. If you only want to download a certain
        portion specify it here. Defaults to 'all'.
    """
    if download_libri_tts_r:
        subset_dict = {
            "libri-tts-clean-100": "https://www.openslr.org/resources/141/train_clean_100.tar.gz",
            "libri-tts-clean-360": "http://www.openslr.org/resources/141/train-clean-360.tar.gz",
            "libri-tts-other-500": "http://www.openslr.org/resources/141/train-other-500.tar.gz",
            "libri-tts-dev-clean": "http://www.openslr.org/resources/141/dev-clean.tar.gz",
            "libri-tts-dev-other": "http://www.openslr.org/resources/141/dev-other.tar.gz",
            "libri-tts-test-clean": "http://www.openslr.org/resources/141/test-clean.tar.gz",
            "libri-tts-test-other": "http://www.openslr.org/resources/141/test-other.tar.gz",
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

    os.makedirs(path, exist_ok=True)
    if subset == "all":
        if async_download:
            print(" > Downloading all subsets asynchronously...")
            async_download_urls(subset_dict, path)
        else:
            for sub, val in subset_dict.items():
                print(f" > Downloading {sub}...")
                download_and_extract(path, val)
        print(" > All subsets downloaded")
    else:
        download_and_extract(path, subset_dict[subset])
        
        
def download_mailabs(path: str, language: str = "all", async_download: Optional[bool] = False):
    """Download and extract Mailabs dataset.

    Args:
        path (str): Path to the directory where the dataset will be stored.

        language (str): Language subset to download. Defaults to english.
    """
    language_dict = {
        "en": "https://data.solak.de/data/Training/stt_tts/en_US.tgz",
        "de": "https://data.solak.de/data/Training/stt_tts/de_DE.tgz",
        "fr": "https://data.solak.de/data/Training/stt_tts/fr_FR.tgz",
        "it": "https://data.solak.de/data/Training/stt_tts/it_IT.tgz",
        "es": "https://data.solak.de/data/Training/stt_tts/es_ES.tgz",
    }
    if language == "all":
        if async_download:
            print(" > Downloading all languages asynchronously...")
            async_download_urls(language_dict, path)
        else:
            for lang, url in language_dict.items():
                print(f" > Downloading {lang}...")
                download_and_extract(path, url)
    else:
        url = language_dict[language]
        download_and_extract(path, url)
        
        
def download_mls(out_path: str, download_compressed: bool = False, language: str = "all", async_download: bool = False):
    url_dict = {
        "en": ("https://dl.fbaipublicfiles.com/mls/mls_english.tar.gz", "https://dl.fbaipublicfiles.com/mls/mls_english_opus.tar.gz"),
        "de": ("https://dl.fbaipublicfiles.com/mls/mls_german.tar.gz", "https://dl.fbaipublicfiles.com/mls/mls_german_opus.tar.gz"),
        "nl": ("https://dl.fbaipublicfiles.com/mls/mls_dutch.tar.gz", "https://dl.fbaipublicfiles.com/mls/mls_dutch_opus.tar.gz"),
        "fr": ("https://dl.fbaipublicfiles.com/mls/mls_french.tar.gz", "https://dl.fbaipublicfiles.com/mls/mls_french_opus.tar.gz"),
        "it": ("https://dl.fbaipublicfiles.com/mls/mls_italian.tar.gz", "https://dl.fbaipublicfiles.com/mls/mls_italian_opus.tar.gz"),
        "es": ("https://dl.fbaipublicfiles.com/mls/mls_spanish.tar.gz", "https://dl.fbaipublicfiles.com/mls/mls_spanish_opus.tar.gz"),
        "pt": ("https://dl.fbaipublicfiles.com/mls/mls_portuguese.tar.gz", "https://dl.fbaipublicfiles.com/mls/mls_portuguese_opus.tar.gz"),
        "pl": ("https://dl.fbaipublicfiles.com/mls/mls_polish.tar.gz", "https://dl.fbaipublicfiles.com/mls/mls_polish_opus.tar.gz"),
    }
    if language == "all":
        if async_download:
            print(" > Downloading all subsets asynchronously...")
            if download_compressed:
                url_dict = {key: values[-1] for key, values in url_dict.items()}
            else:
                url_dict = {key: values[0] for key, values in url_dict.items()}
            async_download_urls(url_dict, out_path)
        else:
            for lang, urls in url_dict.items():
                print(f" > Downloading {lang}...")
                if download_compressed:
                    download_and_extract(out_path, urls[1])
                else:
                    download_and_extract(out_path, urls[0])
        print(" > All languages downloaded")
    
    else:
        if download_compressed:
            url = url_dict[language][-1]
        else:
            url = url_dict[language][0]
        download_and_extract(out_path, url)
        