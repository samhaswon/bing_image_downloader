## Bing Image Downloader

A Python library to download bulk of images from Bing.com.

### Disclaimer

This program lets you download many images from Bing.

Please do not download or use any image that violates its copyright terms. 

### Installation 

```sh
pip install bing-image-downloader
```

or 

```bash
git clone https://github.com/gurugaurav/bing_image_downloader
cd bing_image_downloader
pip install .
```

### Usage

```python
from bing_image_downloader import downloader
query = "Cat"
downloader.download(query, 
                    limit=100,  
                    output_dir='dataset', 
                    adult_filter_off=True, 
                    force_replace=False, 
                    timeout=60, 
                    verbose=True)
```

`query_string` : String or list of strings to be searched.

`limit` : (optional, default is 100) Number of images to download (per query).

`output_dir` : (optional, default is 'dataset') Name of output dir.

`adult_filter_off` : (optional, default is True) Disable adult content filtering.

`force_replace` : (optional, default is False) Delete folder if present and start a fresh download.

`timeout` : (optional, default is 60) connection timeout in seconds.

`filter` : (optional, default is "") filter for only certain types of images, choose from [line, photo, clipart, gif, transparent]

`img_size` : (optional) Minimum size of the images to download with `_` separating the width and height respectively (i.e. `512_512`)

`verbose` : (optional, default is True) Enable downloaded message.

---

You can also test the program by running `test.py keyword`
