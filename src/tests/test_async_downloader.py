import pytest
from pathlib import Path

from unittest.mock import MagicMock
from unittest.mock import patch
from aiohttp.client_exceptions \
    import ClientError, ClientResponseError, InvalidURL
import aiofiles
import aiofiles.tempfile

import hpc.api.utils.async_downloader as adownloader


@pytest.fixture
def various_uris_to_test():
    # TODO: what if an uri does not have filename nor path?
    return [
        ["http://abc.def.com/some_file.txt", "some_file.txt"],
        ["http://abc.def.com/some_file", "some_file"],
        ["http://abc.def.com/some_file.txt?a=b&c=d", "some_file.txt"],
        ["http://abc.def.com/some_file?a=b&c=d", "some_file"],
        ["http://abc.def.com/some%20file.txt?a=b&c=d", "some file.txt"],
        ["http://abc.def.com/some%20fil%C3%B1.txt?a=b&c=d", "some filñ.txt"],
    ]


def test_filename_retrieval_from_uri_path(various_uris_to_test):
    for uri in various_uris_to_test:
        assert adownloader.get_filename_from_uri(uri[0]) == uri[1]


@patch("aiohttp.ClientSession")
@pytest.mark.asyncio
async def test_http_file_does_not_exist(session_mock):
    get_mock = MagicMock()
    get_mock.get.side_effect = ClientResponseError(
        request_info=None, history=(), status=404,
        message="Not Found", headers=None
    )
    session_mock.return_value.__aenter__.return_value = get_mock
    uri = "http://abc.def.com/some_file.txt"
    with pytest.raises(ClientResponseError):
        await adownloader.save_uri(uri, "local_dst")


@patch("aiohttp.ClientSession")
@pytest.mark.asyncio
async def test_http_any_client_error(session_mock):
    get_mock = MagicMock()
    get_mock.get.side_effect = ClientError()
    session_mock.return_value.__aenter__.return_value = get_mock
    uri = "http://abc.def.com/some_file.txt"
    with pytest.raises(ClientError):
        await adownloader.save_uri(uri, "local_dst")


@pytest.mark.asyncio
async def test_empty_arguments():
    with pytest.raises(AttributeError):
        await adownloader.save_uri("uri", "")
    with pytest.raises(AttributeError):
        await adownloader.save_uri("", "local_dst")


@pytest.mark.asyncio
async def test_invalid_uri():
    with pytest.raises(InvalidURL):
        await adownloader.save_uri("invalid uri", "local_dst")


async def get_iter_bytes(*args, **kwargs):
    for chunk in [b"1st block of text,", b"2nd block of text", b""]:
        yield chunk


@patch("aiohttp.ClientSession")
@pytest.mark.asyncio
async def test_saving_http_response_into_local_file(session_mock):
    response_text = b"1st block of text,2nd block of text"
    response_mock = MagicMock(status=200)
    response_mock.content.iter_chunked = get_iter_bytes
    get_mock = MagicMock()
    get_mock.get.return_value.__aenter__.return_value = response_mock
    session_mock.return_value.__aenter__.return_value = get_mock
    async with aiofiles.tempfile.TemporaryDirectory() as download_dir:
        uri = "http://abc.def.com/some_file.txt"
        local_dst = Path(download_dir) / "some_file.txt"
        await adownloader.save_uri(uri, local_dst)
        async with aiofiles.open(local_dst, "rb") as file:
            assert response_text == await file.read()
