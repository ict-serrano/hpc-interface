import pytest
import hpc.api.utils.downloader as downloader
import urllib.request
from unittest.mock import MagicMock
from urllib.error import HTTPError
from tempfile import TemporaryDirectory
from pathlib import Path


def test_http_file_exists(mocker):
    mocker.patch('urllib.request.urlopen', return_value=MagicMock(status=200))
    src = "http://abc.def.com/some_file.txt"
    response = downloader.get_response(src)
    assert response.status == 200


def test_http_file_does_not_exist(mocker):
    src = "http://abc.def.com/some_file.txt"
    mocker.patch(
        "urllib.request.urlopen",
        side_effect=HTTPError(src, 404, "Not Found", {}, None)
    )
    with pytest.raises(HTTPError):
        response = downloader.get_response(src)


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
        assert downloader.get_filename_from_uri(uri[0]) == uri[1]


def test_saving_http_response_into_local_file(mocker):
    response_text = b"1st block of text,2nd block of text"
    response_text_blocks = [b"1st block of text,", b"2nd block of text", ""]
    response_mock = MagicMock()
    response_mock.read.side_effect = response_text_blocks
    mocker.patch(
        "hpc.api.utils.downloader.get_response",
        return_value=response_mock)
    with TemporaryDirectory() as download_dir:
        local_dst = Path(download_dir) / "some_file.txt"
        downloader.save_response_locally(response_mock, local_dst)
        assert response_text == local_dst.read_bytes()
