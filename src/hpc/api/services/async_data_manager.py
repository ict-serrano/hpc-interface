import json
import asyncio
from pathlib import Path
from uuid import uuid4


import aiofiles.tempfile

import hpc.api.utils.async_persistence as persistence
import hpc.api.utils.async_ssh as ssh
import hpc.api.utils.async_downloader as downloader
from hpc.api.openapi.models.file_transfer_request import FileTransferRequest
from hpc.api.openapi.models.file_transfer_status import FileTransferStatus
from hpc.api.openapi.models.file_transfer_status_code import FileTransferStatusCode


async def transfer(ft_request: FileTransferRequest) -> FileTransferStatus:
    ft_status = FileTransferStatus(
        id=str(uuid4()),
        status=FileTransferStatusCode.TRANSFERRING,
        infrastructure=ft_request.infrastructure,
        src=ft_request.src,
        dst=ft_request.dst,
        reason=""
    )
    await persistence.save(
        persistence.get_file_transfer_directory(ft_status.id),
        json.dumps(ft_status.to_dict()))
    asyncio.create_task(handle_copy(ft_request, ft_status), name=ft_status.id)
    return ft_status


async def handle_copy(
    ft_request: FileTransferRequest,
    ft_status: FileTransferStatus
) -> None:
    try:
        await copy(ft_request.infrastructure, ft_request.src, ft_request.dst)
        ft_status.status = FileTransferStatusCode.COMPLETED
    except Exception as e:  # TODO: better error handling and error description
        ft_status.status = FileTransferStatusCode.FAILURE
        ft_status.reason = repr(e)
    finally:
        await persistence.save(
            persistence.get_file_transfer_directory(ft_status.id),
            json.dumps(ft_status.to_dict()))


async def copy(infrastructure: str, src: str, dst: str) -> None:
    infrastructure = json.loads(
        await persistence.get(
            persistence.get_cluster_directory(infrastructure)))
    key_path = infrastructure["ssh_key"]["path"]
    key_password = infrastructure["ssh_key"]["password"]
    pkey = await ssh.get_pkey(key_path, key_password)
    host = infrastructure["host"]
    username = infrastructure["username"]
    async with aiofiles.tempfile.TemporaryDirectory() as download_dir:
        # download remote file into local fs
        local_dst = Path(download_dir) / downloader.get_filename_from_uri(src)
        await downloader.save_uri(src, local_dst)
        # upload local file to sftp
        local_src = local_dst
        remote_dst = Path(dst)
        await ssh.sftp_upload(host, username, pkey, local_src, remote_dst)


async def get(file_transfer_id: str) -> FileTransferStatus:
    return FileTransferStatus.from_dict(
        json.loads(
            await persistence.get(
                persistence.get_file_transfer_directory(file_transfer_id))))
