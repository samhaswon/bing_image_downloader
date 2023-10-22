import time
from PIL import Image
import hashlib
import shutil
import posixpath
import re
import urllib
import urllib.request
import os
from typing import Union, Tuple

'''
Python package to download image form Bing.
Author: Guru Prasad (g.gaurav541@gmail.com)
'''


def get_hash(file_path: str, mode="md5") -> str:
    """
    Calculates the hash of the given file
    :param file_path: Path to the file
    :param mode: Method to calculate the hash of the file
    :returns: Hex digest of the file hash
    """
    file_hash = hashlib.new(mode)
    with open(file_path, 'rb') as file:
        data = file.read()
    file_hash.update(data)
    return file_hash.hexdigest()


class Bing:
    def __init__(self, query, limit=100, output_dir='dataset', adult=True, timeout=60, img_filter=None, verbose=True,
                 image_size=None) -> None:
        """
        Initialize a Bing (downloader) object
        :param query: String or list of strings to query Bing for images of.
        :param limit: Maximum number of images to download for the given query
        :param output_dir: Directory to place the downloaded images in
        :param adult: whether to disable the Adult Content img_filter, or not (True disables it)
        :param timeout: connection timeout in seconds
        :param img_filter: Filter images by desired type: line|photo|clipart|gif|transparent
        :param image_size: Minimum size of the images to download with `_` separating the width and height respectively
        (i.e. `512_512`)
        :param verbose: Whether to enable verbose logging
        """
        if img_filter is None:
            img_filter = ""
        self.image_size: str = image_size
        self.__download_count: int = 0
        self.file_hashes: set = set()
        self.__query: str = query
        self.__output_dir = output_dir
        self.adult: bool = adult
        self.filter: Union[str, None] = img_filter
        self.verbose: bool = verbose
        self.seen: set = set()
        self.back_off: Tuple[bool, int] = False, 0

        assert type(limit) == int, "limit must be integer"
        self.limit = limit
        assert type(timeout) == int, "timeout must be integer"
        self.timeout = timeout

        self.page_counter: int = 0
        self.headers: dict = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                                            'AppleWebKit/537.11 (KHTML, like Gecko) '
                                            'Chrome/23.0.1271.64 Safari/537.11',
                              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                              'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                              'Accept-Encoding': 'none',
                              'Accept-Language': 'en-US,en;q=0.8',
                              'Connection': 'keep-alive'}

    def get_filter(self, shorthand) -> str:
        """
        Generates the filter string for Bing
        :param shorthand: type of image to filter for
        :returns: Filter string for the Bing URL
        """

        filter_string = ""

        if shorthand == "line" or shorthand == "linedrawing":
            filter_string += "+filterui:photo-linedrawing"
        elif shorthand == "photo":
            filter_string += "+filterui:photo-photo"
        elif shorthand == "clipart":
            filter_string += "+filterui:photo-clipart"
        elif shorthand == "gif" or shorthand == "animatedgif":
            filter_string += "+filterui:photo-animatedgif"
        elif shorthand == "transparent":
            filter_string += "+filterui:photo-transparent"

        if self.image_size is not None:
            filter_string += "+filterui:imagesize-custom_" + self.image_size

        return filter_string

    def save_image(self, link, file_path) -> None:
        """
        Does the actual downloading of the file at the given link to the specified file path
        :param link: Link to the file to download
        :param file_path: Path to save the given file to
        """
        # Short circuit on some of the watermarked images
        if "dreamstime" in link or \
                "alamy" in link or \
                "istockphoto" in link or \
                "depositphotos" in link or \
                "gettyimages" in link:
            raise Exception("Watermarked photo")

        # Generally works for most URLs
        try:
            urllib.request.urlretrieve(link, file_path)
        # Generally works for broken URLs
        except urllib.request.HTTPError:
            # Just in case the previous method actually downloaded something
            if os.path.isfile(file_path):
                os.remove(file_path)
            print("[%] Encountered HTTP Error 403. Attempting secondary download method")
            request = urllib.request.Request(link, None, self.headers)
            image: bytes = urllib.request.urlopen(request, timeout=self.timeout).read()
            with open(str(file_path), 'wb') as f:
                f.write(image)
        # Validate the downloaded image with Pillow
        finally:
            try:
                img = Image.open(file_path)
                img.load()
                if not img.format:
                    img.close()
                    os.remove(file_path)
                    print('[Error]Invalid image, not saving {}\n'.format(link))
                    raise ValueError('Invalid image, not saving {}\n'.format(link))
                else:
                    img.close()

                # Check for duplicates from multiple sources via file hashes
                file_hash = get_hash(file_path)
                if file_hash in self.file_hashes:
                    os.remove(file_path)
                    raise Exception("Duplicate file found")
                else:
                    self.file_hashes.add(file_hash)
            except Exception:
                print('[Error] Invalid image, not saving {}\n'.format(link))
                raise ValueError('Invalid image, not saving {}\n'.format(link))

    def download_image(self, link: str) -> None:
        """
        Downloads the image at the given link to the predefined folder
        :param link: The link to the image to download
        """
        self.__download_count += 1
        # Get the image link
        try:
            path = urllib.parse.urlsplit(link).path
            filename = posixpath.basename(path).split('?')[0]
            file_type = filename.split(".")[-1]
            if file_type.lower() not in ["jpe", "jpeg", "jfif", "exif", "tiff", "gif", "bmp", "png", "webp", "jpg"]:
                file_type = "jpg"

            if self.verbose:
                # Download the image
                print("[%] Downloading Image #{} from {}".format(self.__download_count, link))

            # Pseudo-sanitize the query for file naming
            query_name = re.sub(r"\s", "_", self.query)

            self.save_image(link, self.__output_dir.joinpath("{}_Image_{}.{}".format(query_name,
                                                                                     str(self.__download_count),
                                                                                     file_type)))
            if self.verbose:
                print("[%] File Downloaded !\n")

        except Exception as e:
            self.__download_count -= 1
            print("[!] Issue getting: {}\n[!] Error:: {}".format(link, e))

    def run(self) -> None:
        """
        Starts the download process
        :returns: None
        """
        while self.__download_count < self.limit:
            if self.verbose:
                print('\n\n[!!]Indexing page: {}\n'.format(self.page_counter + 1))

            # Parse the page source and download pics
            request_url = 'https://www.bing.com/images/async?q=' + \
                          urllib.parse.quote_plus(self.__query) + \
                          '&first=' + str(self.page_counter) + \
                          '&count=' + str(self.limit) + \
                          '&adlt=' + str(self.adult) + \
                          '&qft=' + self.get_filter(self.filter)
            request = urllib.request.Request(request_url, None, headers=self.headers)
            response = urllib.request.urlopen(request)
            html = response.read().decode('utf8')

            # Backoff if being rate limited.
            if self.back_off[0] and self.back_off[1] + 2 < self.__download_count:
                self.back_off = False, 0
            if html == "" and self.back_off[0]:
                print("[%] No more images are available")
                break
            elif html == "" and not self.back_off[0]:
                print("[%] Encountered rate limit. Backing off...")
                time.sleep(5)
                self.back_off = True, self.__download_count
                continue

            # Find all image links
            links = re.findall('murl&quot;:&quot;(.*?)&quot;', html)
            if self.verbose:
                print("[%] Indexed {} Images on Page {}.".format(len(links), self.page_counter + 1))

                # Terminal width bar made of equals signs
                print("\n" + "=" * shutil.get_terminal_size((80, 20)).columns + "\n")

            # Download each link from the page if it has not been seen
            for link in links:
                if self.__download_count < self.limit and link not in self.seen:
                    self.seen.add(link)
                    self.download_image(link)

            self.page_counter += 1
        print("\n\n[%] Done. Downloaded {} images.".format(self.__download_count))

        # Reset the counts for repeated use
        self.page_counter = 0
        self.__download_count = 0

    @property
    def query(self):
        """
        The query to search Bing for
        """
        return self.__query

    @query.setter
    def query(self, value):
        """
        Set a new query to search for
        """
        self.__query = value

    @property
    def output_dir(self):
        """
        The directory images are saved to
        """
        return self.__output_dir

    @output_dir.setter
    def output_dir(self, value):
        """
        Set the directory images are saved to
        """
        self.__output_dir = value
