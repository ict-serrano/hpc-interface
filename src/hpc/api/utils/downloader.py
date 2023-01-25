import os
import urllib.request
from urllib.parse import urlparse, unquote


def get_response(src):
    return urllib.request.urlopen(src)


def get_filename_from_uri(uri):
    path = urlparse(uri).path
    return os.path.basename(unquote(path))


def save_response_locally(response, local_dst):
    # handle large files
    with local_dst.open("wb") as f:
        block_size = 8192
        while True:
            buffer = response.read(block_size)
            if not buffer:
                break
            f.write(buffer)
