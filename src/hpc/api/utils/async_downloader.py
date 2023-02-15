import os
from urllib.parse import urlparse, unquote
from pathlib import Path

import aiohttp
import aiofiles


def get_filename_from_uri(uri: str) -> str:
    path = urlparse(uri).path
    return os.path.basename(unquote(path))


async def save_uri(uri: str, local_dst: Path) -> None:
    if not (uri and local_dst):
        raise AttributeError
    async with aiohttp.ClientSession() as session:
        async with session.get(uri) as response:
            async with aiofiles.open(local_dst, "wb") as file:
                chunk_size = 8192
                async for chunk in response.content.iter_chunked(chunk_size):
                    await file.write(chunk)
