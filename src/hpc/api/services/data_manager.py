import json
import hpc.api.utils.persistence as persistence
import hpc.api.utils.ssh as ssh
import hpc.api.utils.downloader as downloader
from tempfile import TemporaryDirectory
from pathlib import Path
from uuid import uuid4
from hpc.api.openapi.models.file_transfer_request import FileTransferRequest
from hpc.api.openapi.models.file_transfer_status import FileTransferStatus
from hpc.api.openapi.models.file_transfer_status_code import FileTransferStatusCode


def transfer(ft_request: FileTransferRequest) -> FileTransferStatus:
    infrastructure = json.loads(
        persistence.get(
            persistence.get_cluster_directory(ft_request.infrastructure)))
    key_type = infrastructure["ssh_key"]["type"]
    key_path = infrastructure["ssh_key"]["path"]
    key_password = infrastructure["ssh_key"]["password"]
    pkey = ssh.get_pkey(key_type, key_path, key_password)
    host = infrastructure["host"]
    username = infrastructure["username"]

    with TemporaryDirectory() as download_dir:
        # download remote file into local fs
        src = ft_request.src
        local_dst = Path(download_dir) / downloader.get_filename_from_uri(src)
        downloader.save_response_locally(
            downloader.get_response(src), local_dst)
        # upload local file to sftp
        local_src = str(local_dst.resolve())
        remote_dst = ft_request.dst
        ssh.sftp_upload(host, username, pkey, local_src, remote_dst)

    ft_id = str(uuid4())
    progress = 100
    status = FileTransferStatusCode.COMPLETED

    ft_status = FileTransferStatus(
        id=ft_id,
        progress=progress,
        status=status,
        infrastructure=ft_request.infrastructure,
        src=ft_request.src,
        dst=ft_request.dst,
    )

    persistence.save(
        persistence.get_file_transfer_directory(ft_id),
        json.dumps(ft_status.to_dict()))

    return ft_status


def get(file_transfer_id: str) -> FileTransferStatus:
    return FileTransferStatus.from_dict(
        json.loads(
            persistence.get(
                persistence.get_file_transfer_directory(file_transfer_id))))
