# Adapted from https://github.com/pytorch/audio/

import hashlib
import logging
import os
import tarfile
import multiprocessing
from tqdm import tqdm
from multiprocessing import Manager
import urllib
import urllib.request
import zipfile
from os.path import expanduser
from typing import Any, Iterable, List, Optional

from torch.utils.model_zoo import tqdm


def get_the_directory(base_path, full_path):
    """
    Extracts the base path and the first subdirectory from the given path.

    Parameters:
    full_path (str): The full path from which to extract the base path and first subdirectory.

    Returns:
    str: The base path and the first subdirectory, if available.
    """
    base_path = "/home/logan/.local/share/dataengine"
    if full_path.startswith(base_path):
        remaining_path = full_path[len(base_path):].strip("/")
        first_subdirectory = remaining_path.split(os.sep, 1)[0]
        return os.path.join(base_path, first_subdirectory)
    else:
        raise ValueError("The provided path does not start with the expected base path.")
    

def stream_url(
    url: str, start_byte: Optional[int] = None, block_size: int = 32 * 1024, progress_bar: bool = True
) -> Iterable:
    """Stream url by chunk

    Args:
        url (str): Url.
        start_byte (int or None, optional): Start streaming at that point (Default: ``None``).
        block_size (int, optional): Size of chunks to stream (Default: ``32 * 1024``).
        progress_bar (bool, optional): Display a progress bar (Default: ``True``).
    """

    # If we already have the whole file, there is no need to download it again
    req = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(req) as response:
        url_size = int(response.info().get("Content-Length", -1))
    if url_size == start_byte:
        return

    req = urllib.request.Request(url)
    if start_byte:
        req.headers["Range"] = "bytes={}-".format(start_byte)

    with urllib.request.urlopen(req) as upointer, tqdm(
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        total=url_size,
        disable=not progress_bar,
    ) as pbar:
        num_bytes = 0
        while True:
            chunk = upointer.read(block_size)
            if not chunk:
                break
            yield chunk
            num_bytes += len(chunk)
            pbar.update(len(chunk))


def download_url(
    url: str,
    download_folder: str,
    filename: Optional[str] = None,
    hash_value: Optional[str] = None,
    hash_type: str = "sha256",
    progress_bar: bool = True,
    resume: bool = False,
) -> None:
    """Download file to disk.

    Args:
        url (str): Url.
        download_folder (str): Folder to download file.
        filename (str or None, optional): Name of downloaded file. If None, it is inferred from the url
            (Default: ``None``).
        hash_value (str or None, optional): Hash for url (Default: ``None``).
        hash_type (str, optional): Hash type, among "sha256" and "md5" (Default: ``"sha256"``).
        progress_bar (bool, optional): Display a progress bar (Default: ``True``).
        resume (bool, optional): Enable resuming download (Default: ``False``).
    """

    req = urllib.request.Request(url, method="HEAD")
    req_info = urllib.request.urlopen(req).info()  # pylint: disable=consider-using-with

    # Detect filename
    filename = filename or req_info.get_filename() or os.path.basename(url)
    filepath = os.path.join(download_folder, filename)
    if resume and os.path.exists(filepath):
        mode = "ab"
        local_size: Optional[int] = os.path.getsize(filepath)

    elif not resume and os.path.exists(filepath):
        raise RuntimeError("{} already exists. Delete the file manually and retry.".format(filepath))
    else:
        mode = "wb"
        local_size = None

    if hash_value and local_size == int(req_info.get("Content-Length", -1)):
        with open(filepath, "rb") as file_obj:
            if validate_file(file_obj, hash_value, hash_type):
                return
        raise RuntimeError("The hash of {} does not match. Delete the file manually and retry.".format(filepath))

    with open(filepath, mode) as fpointer:
        for chunk in stream_url(url, start_byte=local_size, progress_bar=progress_bar):
            fpointer.write(chunk)

    with open(filepath, "rb") as file_obj:
        if hash_value and not validate_file(file_obj, hash_value, hash_type):
            raise RuntimeError("The hash of {} does not match. Delete the file manually and retry.".format(filepath))


def validate_file(file_obj: Any, hash_value: str, hash_type: str = "sha256") -> bool:
    """Validate a given file object with its hash.

    Args:
        file_obj: File object to read from.
        hash_value (str): Hash for url.
        hash_type (str, optional): Hash type, among "sha256" and "md5" (Default: ``"sha256"``).

    Returns:
        bool: return True if its a valid file, else False.
    """

    if hash_type == "sha256":
        hash_func = hashlib.sha256()
    elif hash_type == "md5":
        hash_func = hashlib.md5()
    else:
        raise ValueError

    while True:
        # Read by chunk to avoid filling memory
        chunk = file_obj.read(1024**2)
        if not chunk:
            break
        hash_func.update(chunk)

    return hash_func.hexdigest() == hash_value


def extract_archive(from_path: str, to_path: Optional[str] = None, overwrite: bool = False) -> List[str]:
    """Extract archive.
    Args:
        from_path (str): the path of the archive.
        to_path (str or None, optional): the root path of the extraced files (directory of from_path)
            (Default: ``None``)
        overwrite (bool, optional): overwrite existing files (Default: ``False``)

    Returns:
        list: List of paths to extracted files even if not overwritten.
    """

    if to_path is None:
        to_path = os.path.dirname(from_path)

    try:
        with tarfile.open(from_path, "r") as tar:
            logging.info("Opened tar file %s.", from_path)
            files = []
            for file_ in tar:  # type: Any
                file_path = os.path.join(to_path, file_.name)
                print(file_.name)
                if file_.isfile():
                    files.append(file_path)
                    if os.path.exists(file_path):
                        logging.info("%s already extracted.", file_path)
                        if not overwrite:
                            continue
                tar.extract(file_, to_path)
        return get_the_directory(to_path, files[0])
    except tarfile.ReadError:
        pass

    try:
        with zipfile.ZipFile(from_path, "r") as zfile:
            logging.info("Opened zip file %s.", from_path)
            files = zfile.namelist()
            for file_ in files:
                file_path = os.path.join(to_path, file_)
                if os.path.exists(file_path):
                    logging.info("%s already extracted.", file_path)
                    if not overwrite:
                        continue
                zfile.extract(file_, to_path)
        return get_the_directory(to_path, files[0])
    except zipfile.BadZipFile:
        pass

    raise NotImplementedError(" > [!] only supports tar.gz, tgz, and zip achives.")


def download_kaggle_dataset(dataset_path: str, dataset_name: str, output_path: str):
    """Download dataset from kaggle.
    Args:
        dataset_path (str):
        This the kaggle link to the dataset. for example vctk is 'mfekadu/english-multispeaker-corpus-for-voice-cloning'
        dataset_name (str): Name of the folder the dataset will be saved in.
        output_path (str): Path of the location you want the dataset folder to be saved to.
    """
    data_path = os.path.join(output_path, dataset_name)
    try:
        import kaggle  # pylint: disable=import-outside-toplevel

        kaggle.api.authenticate()
        print(f"""\nDownloading {dataset_name}...""")
        kaggle.api.dataset_download_files(dataset_path, path=data_path, unzip=True)
        return data_path
    except OSError:
        print(
            f"""[!] in order to download kaggle datasets, you need to have a kaggle api token stored in your {os.path.join(expanduser('~'), '.kaggle/kaggle.json')}"""
        )
        
        
def async_download_urls(url_dict, path):
    def download_and_extract(url, val, path, progress_list):
        print(f" > Downloading {url}...")
        download_url(val, path, progress_bar=False)
        basename = os.path.basename(val)
        archive = os.path.join(path, basename)
        print(f" > Extracting {archive} file...")
        _ = extract_archive(archive)
        progress_list.append(1)
        
    with Manager() as manager:
        progress_list = manager.list()
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        
        for url, val in url_dict.items():
            pool.apply_async(download_and_extract, args=(url, val, path, progress_list))

        pool.close()

        # Display progress with tqdm
        with tqdm(total=len(url_dict)) as pbar:
            while len(progress_list) < len(url_dict):
                current_length = len(progress_list)
                pbar.update(current_length - pbar.n)

        pool.join()
        print(" > All subsets downloaded")
