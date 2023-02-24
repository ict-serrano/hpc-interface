import json
import asyncio
from pathlib import Path
from uuid import uuid4


import aiofiles.tempfile

import hpc.api.utils.async_persistence as persistence
import hpc.api.utils.async_ssh as ssh
import hpc.api.utils.async_downloader as downloader
import hpc.api.utils.async_s3 as s3
from hpc.api.openapi.models.file_transfer_request import FileTransferRequest
from hpc.api.openapi.models.file_transfer_status import FileTransferStatus
from hpc.api.openapi.models.s3_file_transfer_request import S3FileTransferRequest
from hpc.api.openapi.models.s3_file_transfer_status import S3FileTransferStatus
from hpc.api.openapi.models.file_transfer_status_code import FileTransferStatusCode


class DataManagerFactory:
    HTTP = "http"
    S3 = "s3"

    @classmethod
    def get_data_manager(cls, proto):
        if proto == cls.HTTP:
            return HTTPDataManager()
        elif proto == cls.S3:
            return S3DataManager()
        else:
            raise NotImplementedError(f"This proto {proto} is not implemented")


class HTTPDataManager:
    async def transfer(
        self,
        ft_request: FileTransferRequest
    ) -> FileTransferStatus:
        ft_status = FileTransferStatus(
            id=str(uuid4()),
            status=FileTransferStatusCode.TRANSFERRING,
            infrastructure=ft_request.infrastructure,
            src=ft_request.src,
            dst=ft_request.dst,
            reason="")
        await persistence.save(
            persistence.get_file_transfer_directory(ft_status.id),
            json.dumps(ft_status.to_dict()))
        asyncio.create_task(
            self.handle_copy(ft_request, ft_status),
            name=ft_status.id)
        return ft_status

    async def handle_copy(
        self,
        ft_request: FileTransferRequest,
        ft_status: FileTransferStatus
    ) -> None:
        try:
            await self.copy(ft_request)
            ft_status.status = FileTransferStatusCode.COMPLETED
        except Exception as e:  # TODO: better error handling and error description
            ft_status.status = FileTransferStatusCode.FAILURE
            ft_status.reason = repr(e)
        finally:
            await persistence.save(
                persistence.get_file_transfer_directory(ft_status.id),
                json.dumps(ft_status.to_dict()))

    async def copy(
        self,
        ft_request: FileTransferRequest
    ) -> None:
        infrastructure = json.loads(
            await persistence.get(
                persistence.get_cluster_directory(ft_request.infrastructure)))
        key_path = infrastructure["ssh_key"]["path"]
        key_password = infrastructure["ssh_key"]["password"]
        pkey = await ssh.get_pkey(key_path, key_password)
        host = infrastructure["host"]
        username = infrastructure["username"]
        async with aiofiles.tempfile.TemporaryDirectory() as download_dir:
            # download remote file into local fs
            local_dst = Path(download_dir) / \
                downloader.get_filename_from_uri(ft_request.src)
            await downloader.save_uri(ft_request.src, local_dst)
            # upload local file to sftp
            local_src = local_dst
            remote_dst = Path(ft_request.dst)
            await ssh.sftp_upload(host, username, pkey, local_src, remote_dst)

    async def get(
        self,
        file_transfer_id: str
    ) -> FileTransferStatus:
        return FileTransferStatus.from_dict(
            json.loads(
                await persistence.get(
                    persistence.get_file_transfer_directory(file_transfer_id))))


class S3DataManager:
    async def transfer(
        self,
        ft_request: S3FileTransferRequest
    ) -> S3FileTransferStatus:
        ft_status = S3FileTransferStatus(
            id=str(uuid4()),
            status=FileTransferStatusCode.TRANSFERRING,
            infrastructure=ft_request.infrastructure,
            endpoint=ft_request.endpoint,
            bucket=ft_request.bucket,
            object=ft_request.object,
            region=ft_request.region,
            dst=ft_request.dst,
            reason="")
        await persistence.save(
            persistence.get_s3_transfer_directory(ft_status.id),
            json.dumps(ft_status.to_dict()))
        asyncio.create_task(
            self.handle_copy(ft_request, ft_status),
            name=ft_status.id)
        return ft_status

    async def handle_copy(
        self,
        ft_request: S3FileTransferRequest,
        ft_status: S3FileTransferStatus
    ) -> None:
        try:
            await self.copy(ft_request)
            ft_status.status = FileTransferStatusCode.COMPLETED
        except Exception as e:  # TODO: better error handling and error description
            ft_status.status = FileTransferStatusCode.FAILURE
            ft_status.reason = repr(e)
        finally:
            await persistence.save(
                persistence.get_s3_transfer_directory(ft_status.id),
                json.dumps(ft_status.to_dict()))

    async def copy(
        self,
        ft_request: S3FileTransferRequest
    ) -> None:
        infrastructure = json.loads(
            await persistence.get(
                persistence.get_cluster_directory(ft_request.infrastructure)))
        key_path = infrastructure["ssh_key"]["path"]
        key_password = infrastructure["ssh_key"]["password"]
        pkey = await ssh.get_pkey(key_path, key_password)
        host = infrastructure["host"]
        username = infrastructure["username"]
        async with aiofiles.tempfile.TemporaryDirectory() as download_dir:
            client = s3.get_client(
                ft_request.endpoint,
                ft_request.region,
                ft_request.access_key,
                ft_request.secret_key)
            # download remote file into local fs
            local_dst = Path(download_dir) / ft_request.object
            await s3.download_file(
                client,
                ft_request.bucket,
                ft_request.object,
                local_dst)
            # upload local file to sftp
            local_src = local_dst
            remote_dst = Path(ft_request.dst)
            await ssh.sftp_upload(host, username, pkey, local_src, remote_dst)

    async def get(
        self,
        file_transfer_id: str
    ) -> S3FileTransferStatus:
        return S3FileTransferStatus.from_dict(
            json.loads(
                await persistence.get(
                    persistence.get_s3_transfer_directory(file_transfer_id))))
