import sys
from bing_image_downloader import downloader

query = sys.argv[1]

if len(sys.argv) == 3:
    img_filter = sys.argv[2]
else:
    img_filter = ""

downloader.download(
    query,
    limit=10,
    output_dir="dataset",
    adult_filter_off=True,
    force_replace=False,
    timeout=60,
    img_filter=img_filter,
    verbose=True,
)
