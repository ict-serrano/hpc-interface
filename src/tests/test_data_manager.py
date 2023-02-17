import pytest
import hpc.api.services.data_manager as data_manager
import hpc.api.utils.persistence as persistence

from uuid import UUID
from hpc.api.openapi.models.secure_storage_mount import SecureStorageMount
from hpc.api.openapi.models.file_transfer_request import FileTransferRequest
from hpc.api.openapi.models.file_transfer_status_code import FileTransferStatusCode


def test_http_file_transfer_to_sftp(ssh_infrastructures, mocker):
    ft_request = FileTransferRequest(
        src="http://abc.def.com/some_file.txt",
        dst="/tmp/some_file.txt",
        infrastructure=ssh_infrastructures[1]["name"],
        secure_storage_mount=SecureStorageMount.NONE,
        secure_storage_mount_path="",
    )
    mocker.patch("hpc.api.utils.downloader.get_filename_from_uri")
    mocker.patch("hpc.api.utils.downloader.save_response_locally")
    mocker.patch("hpc.api.utils.downloader.get_response")
    mocker.patch("hpc.api.utils.ssh.sftp_upload")
    ft_status = data_manager.transfer(ft_request)
    assert UUID(ft_status.id, version=4)
    assert ft_status.infrastructure == ssh_infrastructures[1]["name"]
    assert ft_status.src == ft_request.src
    assert ft_status.dst == ft_request.dst
    assert ft_status.status == FileTransferStatusCode.COMPLETED
    assert persistence.get(
        persistence.get_file_transfer_directory(ft_status.id))
    pytest.file_transfer_id = ft_status.id


def test_file_transfer_retrieval(ssh_infrastructures, mocker):
    ft_status = data_manager.get(pytest.file_transfer_id)
    assert UUID(ft_status.id, version=4)
    assert ft_status.status == FileTransferStatusCode.COMPLETED
    assert ft_status.infrastructure == ssh_infrastructures[1]["name"]
    assert ft_status.src
    assert ft_status.dst


def test_non_existent_file_transfer():
    with pytest.raises(KeyError):
        data_manager.get("non_existent_file")
