import asyncio
import pytest
from uuid import UUID

from unittest.mock import patch
from unittest.mock import DEFAULT

from hpc.api.services.async_data_manager import DataManagerFactory
import hpc.api.utils.async_persistence as persistence
from hpc.api.openapi.models.file_transfer_request import FileTransferRequest
from hpc.api.openapi.models.s3_file_transfer_request import S3FileTransferRequest
from hpc.api.openapi.models.file_transfer_status_code import FileTransferStatusCode


async def sleep(*args, **kwargs):
    t = 0.1
    await asyncio.sleep(t)
    return DEFAULT


@pytest.fixture
async def submit_ft(assh_infrastructures):
    data_manager = DataManagerFactory.get_data_manager(DataManagerFactory.HTTP)
    ssh_infrastructures = await assh_infrastructures
    ft_request = FileTransferRequest(
        src="http://abc.def.com/some_file.txt",
        dst="/tmp/some_file.txt",
        infrastructure=ssh_infrastructures[1]["name"]
    )
    return data_manager, ft_request, await data_manager.transfer(ft_request)


@pytest.fixture
async def submit_s3_ft(assh_infrastructures):
    data_manager = DataManagerFactory.get_data_manager(DataManagerFactory.S3)
    ssh_infrastructures = await assh_infrastructures
    ft_request = S3FileTransferRequest(
        endpoint="https://some-s3-endpoint.com/s3",
        bucket="test-bucket",
        object="some-object.txt",
        region="some-region",
        access_key="access-key",
        secret_key="secret-key",
        dst="/tmp/some_file.txt",
        infrastructure=ssh_infrastructures[1]["name"]
    )
    return data_manager, ft_request, await data_manager.transfer(ft_request)


@pytest.mark.asyncio
async def test_factory_bad_proto():
    with pytest.raises(NotImplementedError):
        DataManagerFactory.get_data_manager("non_existent_proto")


@patch("hpc.api.utils.async_ssh.sftp_upload", side_effect=sleep)
@patch("hpc.api.utils.async_downloader.save_uri", side_effect=sleep)
@pytest.mark.asyncio
async def test_successful_http_file_transfer_waiting_long_execution(
    downloader,
    sftp,
    submit_ft
):
    data_manager, ft_request, ft_status = await submit_ft
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
            await asyncio.sleep(0.1)
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
    downloader,
    sftp,
    submit_ft
):
    data_manager, _, ft_status = await submit_ft
    assert ft_status.status == FileTransferStatusCode.TRANSFERRING
    while True:
        ft_status = await data_manager.get(ft_status.id)
        if ft_status.status == FileTransferStatusCode.TRANSFERRING:
            await asyncio.sleep(0.1)
            continue
        else:
            assert ft_status.status == FileTransferStatusCode.FAILURE
            assert ft_status.reason
            break


@patch("hpc.api.utils.async_ssh.sftp_upload", side_effect=Exception("oops!"))
@patch("hpc.api.utils.async_downloader.save_uri")
@pytest.mark.asyncio
async def test_unsuccessful_http_file_transfer_sftp_upload_failed(
    downloader,
    sftp,
    submit_ft
):
    data_manager, _, ft_status = await submit_ft
    assert ft_status.status == FileTransferStatusCode.TRANSFERRING
    while True:
        ft_status = await data_manager.get(ft_status.id)
        if ft_status.status == FileTransferStatusCode.TRANSFERRING:
            await asyncio.sleep(0.1)
            continue
        else:
            assert ft_status.status == FileTransferStatusCode.FAILURE
            assert ft_status.reason
            break


@pytest.mark.asyncio
async def test_non_existent_file_transfer():
    data_manager = DataManagerFactory.get_data_manager(DataManagerFactory.HTTP)
    with pytest.raises(KeyError):
        await data_manager.get("non_existent_file")


@patch("hpc.api.utils.async_ssh.sftp_upload", side_effect=sleep)
@patch("hpc.api.utils.async_s3.download_file", side_effect=sleep)
@pytest.mark.asyncio
async def test_successful_s3_transfer_waiting_long_execution(
    downloader,
    sftp,
    submit_s3_ft
):
    data_manager, ft_request, ft_status = await submit_s3_ft
    assert UUID(ft_status.id, version=4)
    assert ft_status.infrastructure == ft_request.infrastructure
    assert ft_status.endpoint == ft_request.endpoint
    assert ft_status.bucket == ft_request.bucket
    assert ft_status.object == ft_request.object
    assert ft_status.region == ft_request.region
    assert ft_status.dst == ft_request.dst
    assert ft_status.status == FileTransferStatusCode.TRANSFERRING
    assert ft_status.reason == ""
    assert await persistence.get(
        persistence.get_s3_transfer_directory(ft_status.id))

    # TODO: testing "get" here. Should be tested in the next test
    # TODO: Running the next test will close previous loop,
    # and therefore will terminate the async handle_copy function
    # Think how to elegantly overcome this.
    while True:
        ft_status = await data_manager.get(ft_status.id)
        if ft_status.status == FileTransferStatusCode.TRANSFERRING:
            await asyncio.sleep(0.1)
            continue
        else:
            assert UUID(ft_status.id, version=4)
            assert ft_status.status == FileTransferStatusCode.COMPLETED
            assert ft_status.infrastructure == ft_request.infrastructure
            assert ft_status.endpoint
            assert ft_status.bucket
            assert ft_status.object
            assert ft_status.region
            assert ft_status.dst
            assert ft_status.reason == ""
            break


@patch("hpc.api.utils.async_ssh.sftp_upload")
@patch("hpc.api.utils.async_s3.download_file", side_effect=Exception("oops!"))
@pytest.mark.asyncio
async def test_unsuccessful_s3_file_transfer_download_file_failed(
    downloader,
    sftp,
    submit_s3_ft
):
    data_manager, _, ft_status = await submit_s3_ft
    assert ft_status.status == FileTransferStatusCode.TRANSFERRING
    while True:
        ft_status = await data_manager.get(ft_status.id)
        if ft_status.status == FileTransferStatusCode.TRANSFERRING:
            await asyncio.sleep(0.1)
            continue
        else:
            assert ft_status.status == FileTransferStatusCode.FAILURE
            assert ft_status.reason
            break


@patch("hpc.api.utils.async_ssh.sftp_upload", side_effect=Exception("oops!"))
@patch("hpc.api.utils.async_s3.download_file")
@pytest.mark.asyncio
async def test_unsuccessful_s3_file_transfer_sftp_upload_failed(
    downloader,
    sftp,
    submit_s3_ft
):
    data_manager, _, ft_status = await submit_s3_ft
    assert ft_status.status == FileTransferStatusCode.TRANSFERRING
    while True:
        ft_status = await data_manager.get(ft_status.id)
        if ft_status.status == FileTransferStatusCode.TRANSFERRING:
            await asyncio.sleep(0.1)
            continue
        else:
            assert ft_status.status == FileTransferStatusCode.FAILURE
            assert ft_status.reason
            break


@pytest.mark.asyncio
async def test_non_existent_s3_file_transfer():
    data_manager = DataManagerFactory.get_data_manager(DataManagerFactory.S3)
    with pytest.raises(KeyError):
        await data_manager.get("non_existent_file")
