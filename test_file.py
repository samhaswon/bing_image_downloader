########################################################################
# Showcase using a file with a query on each line for downloading a
# large dataset at once
#
# File name: test_file.py
# Author: Samuel Howard, Computer Science Major
# Version: 10-21-2023
########################################################################

from bing_image_downloader import downloader


if __name__ == '__main__':
    with open("queries.txt", "r") as query_file:
        queries = query_file.read().splitlines()
    downloader.download(queries,
                        limit=10,
                        output_dir='dataset',
                        adult_filter_off=True,
                        force_replace=False,
                        img_filter="photo",
                        img_size="512_512",
                        timeout=60,
                        verbose=True)
