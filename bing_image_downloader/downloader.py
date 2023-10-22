import sys
import shutil
from pathlib import Path
from typing import Union

try:
    from bing import Bing
except ImportError:  # Python 3
    from .bing import Bing


def download(query: Union[str, list], limit=100, output_dir='dataset', adult_filter_off=True,
             force_replace=False, timeout=60, img_filter=None, img_size=None, verbose=True):
    """
    Downloads a series of images from Bing according to the query and other parameters
    :param query: String or list of strings to query Bing for images of.
    :param limit: Maximum number of images to download for the given query
    :param output_dir: Directory to place the downloaded images in
    :param adult_filter_off: whether to disable the Adult Content img_filter, or not (True disables it)
    :param force_replace: Replaces the `output_dir` is already present
    :param timeout: connection timeout in seconds
    :param img_filter: Filter images by desired type: line|photo|clipart|gif|transparent
    :param img_size: Minimum size of the images to download with `_` separating the width and height respectively (i.e.
    `512_512`)
    :param verbose: Whether to enable verbose logging

    """
    if img_filter is None:
        img_filter = ""
    if adult_filter_off:
        adult = 'off'
    else:
        adult = 'on'

    if type(query) is str:
        image_dir = Path(output_dir).joinpath(query).absolute()
    else:
        image_dir = Path(output_dir).joinpath(query[0]).absolute()

    if force_replace:
        if Path.is_dir(image_dir):
            shutil.rmtree(image_dir)

    if type(query) is list:
        bing = Bing("", limit, image_dir, adult, timeout, img_filter, verbose, img_size)
        for q in query:
            image_dir = Path(output_dir).joinpath(q).absolute()
            # check directory and create if necessary
            try:
                if not Path.is_dir(image_dir):
                    Path.mkdir(image_dir, parents=True, exist_ok=True)

            except Exception as e:
                print('[Error] Failed to create directory.', e)
                sys.exit(1)

            print("[%] Downloading Images to {}".format(str(image_dir.absolute())))
            bing.query = q
            bing.output_dir = image_dir
            bing.run()

    else:
        # check directory and create if necessary
        try:
            if not Path.is_dir(image_dir):
                Path.mkdir(image_dir, parents=True, exist_ok=True)

        except Exception as e:
            print('[Error]Failed to create directory.', e)
            sys.exit(1)

        print("[%] Downloading Images to {}".format(str(image_dir.absolute())))
        bing = Bing(query, limit, image_dir, adult, timeout, img_filter, verbose, img_size)
        bing.run()


if __name__ == '__main__':
    download('dog', output_dir="..\\Users\\cat", limit=10, timeout=1)
