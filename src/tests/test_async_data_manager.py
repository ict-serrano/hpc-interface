import asyncio
import pytest
from uuid import UUID

from unittest.mock import patch
from unittest.mock import DEFAULT

import hpc.api.services.async_data_manager as data_manager
import hpc.api.utils.async_persistence as persistence
from hpc.api.openapi.models.secure_storage_mount import SecureStorageMount
from hpc.api.openapi.models.file_transfer_request import FileTransferRequest
from hpc.api.openapi.models.file_transfer_status_code import FileTransferStatusCode


async def sleep(*args, **kwargs):
    t = 1
    await asyncio.sleep(t)
    return DEFAULT


@pytest.fixture
async def submit_ft(assh_infrastructures):
    ssh_infrastructures = await assh_infrastructures
    ft_request = FileTransferRequest(
        src="http://abc.def.com/some_file.txt",
        dst="/tmp/some_file.txt",
        infrastructure=ssh_infrastructures[1]["name"],
        secure_storage_mount=SecureStorageMount.NONE,
        secure_storage_mount_path="",
    )
    return ft_request, await data_manager.transfer(ft_request)


@patch("hpc.api.utils.async_ssh.sftp_upload", side_effect=sleep)
@patch("hpc.api.utils.async_downloader.save_uri", side_effect=sleep)
@pytest.mark.asyncio
async def test_successful_http_file_transfer_waiting_long_execution(
    sftp,
    downloader,
    submit_ft
):
    ft_request, ft_status = await submit_ft
    assert UUID(ft_status.id, version=4)
    assert ft_status.infrastructure == ft_request.infrastructure
    assert ft_status.src == ft_request.src
    assert ft_status.dst == ft_request.dst
    assert ft_status.status == FileTransferStatusCode.TRANSFERRING
    assert ft_status.reason == ""
    assert await persistence.get(
        persistence.get_file_transfer_directory(ft_status.id))

    # TODO: testing "get" here. Should be tested in the next test
    # TODO: Running the next test will close previous loop,
    # and therefore will terminate the async handle_copy function
    # Think how to elegantly overcome this.
    while True:
        ft_status = await data_manager.get(ft_status.id)
        if ft_status.status == FileTransferStatusCode.TRANSFERRING:
            await asyncio.sleep(1)
            continue
        else:
            assert UUID(ft_status.id, version=4)
            assert ft_status.status == FileTransferStatusCode.COMPLETED
            assert ft_status.infrastructure == ft_request.infrastructure
            assert ft_status.src
            assert ft_status.dst
            assert ft_status.reason == ""
            break


@patch("hpc.api.utils.async_ssh.sftp_upload")
@patch("hpc.api.utils.async_downloader.save_uri", side_effect=Exception("oops!"))
@pytest.mark.asyncio
async def test_unsuccessful_http_file_transfer_save_uri_failed(
    sftp,
    downloader,
    submit_ft
):
    _, ft_status = await submit_ft
    assert ft_status.status == FileTransferStatusCode.TRANSFERRING
    while True:
        ft_status = await data_manager.get(ft_status.id)
        if ft_status.status == FileTransferStatusCode.TRANSFERRING:
            await asyncio.sleep(1)
            continue
        else:
            assert ft_status.status == FileTransferStatusCode.FAILURE
            assert ft_status.reason
            break


@patch("hpc.api.utils.async_ssh.sftp_upload", side_effect=Exception("oops!"))
@patch("hpc.api.utils.async_downloader.save_uri")
@pytest.mark.asyncio
async def test_unsuccessful_http_file_transfer_sftp_upload_failed(
    sftp,
    downloader,
    submit_ft
):
    _, ft_status = await submit_ft
    assert ft_status.status == FileTransferStatusCode.TRANSFERRING
    while True:
        ft_status = await data_manager.get(ft_status.id)
        if ft_status.status == FileTransferStatusCode.TRANSFERRING:
            await asyncio.sleep(1)
            continue
        else:
            assert ft_status.status == FileTransferStatusCode.FAILURE
            assert ft_status.reason
            break


@pytest.mark.asyncio
async def test_non_existent_file_transfer():
    with pytest.raises(KeyError):
        await data_manager.get("non_existent_file")