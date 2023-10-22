from bing_image_downloader import downloader


if __name__ == '__main__':
    query = ["Cat", "Cats"]
    downloader.download(query,
                        limit=10,
                        output_dir='dataset',
                        adult_filter_off=True,
                        force_replace=False,
                        img_filter="photo",
                        img_size="512_512",
                        timeout=60,
                        verbose=True)
