import os
from typing import Optional

from .utils import download_kaggle_dataset, download_url, extract_archive, async_download_urls


def download_and_extract(url: str, out_path: str = None):
    """
    Downloads a file from a given URL and extracts it into a specified output path.

    Parameters:
    out_path (str): The path to the directory where the downloaded file will be saved and extracted.
    url (str): The URL of the file to be downloaded.
    """
    if out_path is None:
        out_path = os.path.expanduser('~/.local/share/dataengine')
    os.makedirs(out_path, exist_ok=True)
    print(f" > Downloading {url}...")
    download_url(url, out_path)
    basename = os.path.basename(url)
    archive = os.path.join(out_path, basename)
    print(f" > Extracting {archive} file...")
    return extract_archive(archive)
    

def download_daps(out_path: str = None):
    """
    Downloads the DAPS dataset into a specified output path.
    https://zenodo.org/records/4660670

    Parameters:
    out_path (str): The path to the directory where the dataset will be saved and extracted.
    """
    url = "https://zenodo.org/records/4660670/files/daps.tar.gz?download=1"
    return download_and_extract(url, out_path)
    

def download_thorsten_de(out_path: str = None):
    """
    Downloads the Thorsten German Speech dataset into a specified output path.
    https://www.openslr.org/resources/95

    Parameters:
    out_path (str): The path to the directory where the dataset will be saved and extracted.
    """
    url = "https://www.openslr.org/resources/95/thorsten-de_v02.tgz"
    return download_and_extract(url, out_path)
    

def download_tweb(out_path: str ):
    """
    Downloads the World English Bible Speech dataset from Kaggle into a specified output path.

    Parameters:
    out_path (str): The path to the directory where the dataset will be saved.

    Note:
    This function assumes the presence of `download_kaggle_dataset` function 
    which handles the downloading of datasets from Kaggle.
    """
    return download_kaggle_dataset("bryanpark/the-world-english-bible-speech-dataset", "TWEB", out_path)
    
    
def download_tedlium(out_path: str = None):
    """
    Downloads the TED-LIUM dataset into a specified output path.
    https://www.openslr.org/51/

    Parameters:
    out_path (str): The path to the directory where the dataset will be saved and extracted.
    """
    url = "https://www.openslr.org/resources/51/TEDLIUM_release-3.tgz"
    return download_and_extract(url, out_path)
    

def download_hifi_tts(out_path: str = None):
    """
    Hi-Fi Multi-Speaker English TTS Dataset (Hi-Fi TTS) is a multi-speaker English dataset.
    https://www.openslr.org/resources/109/

    Parameters:
    out_path (str): The path to the directory where the dataset will be saved and extracted.
    """
    url = "https://www.openslr.org/resources/109/hi_fi_tts_v0.tar.gz"
    return download_and_extract(url, out_path)
    

def download_libri_light(out_path: str = None, size: str = "small"):
    url_dict = {
        "small": "https://dl.fbaipublicfiles.com/librilight/data/small.tar",
        "medium": "https://dl.fbaipublicfiles.com/librilight/data/medium.tar",
        "large": "https://dl.fbaipublicfiles.com/librilight/data/large.tar",
        "duplicated": "https://dl.fbaipublicfiles.com/librilight/data/duplicate.tar"
    }
    print(f" > Downloading {size}...")
    return download_and_extract(url_dict[size], out_path)
    
    
def download_vctk(out_path: str, use_kaggle: Optional[bool] = False):
    """Download and extract VCTK dataset.

    Args:
        path (str): path to the directory where the dataset will be stored.

        use_kaggle (bool, optional): Downloads vctk dataset from kaggle. Is generally faster. Defaults to False.
    """
    if use_kaggle:
        download_kaggle_dataset("mfekadu/english-multispeaker-corpus-for-voice-cloning", "VCTK", out_path)
    else:
        url = "https://datashare.ed.ac.uk/bitstream/handle/10283/3443/VCTK-Corpus-0.92.zip"
        return download_and_extract(url, out_path)
        
        
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
                   return download_and_extract(out_path, urls[1])
                else:
                    return download_and_extract(out_path, urls[0])
        print(" > All languages downloaded")
    
    else:
        if download_compressed:
            url = url_dict[language][-1]
        else:
            url = url_dict[language][0]
        return download_and_extract(out_path, url)
        