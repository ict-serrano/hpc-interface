import pytest
from pathlib import Path

from unittest.mock import MagicMock, AsyncMock
from unittest.mock import patch
import asyncssh
import aiofiles.tempfile

import hpc.api.utils.async_ssh as ssh


@pytest.mark.asyncio
async def test_ssh_key_existence(ssh_infrastructures):
    for infrastructure in ssh_infrastructures:
        key_path = infrastructure["ssh_key"]["path"]
        assert await ssh.key_exists(key_path)


@pytest.mark.asyncio
async def test_enforce_non_empty_passphrase_for_ssh_key():
    with pytest.raises(AttributeError):
        await ssh.get_pkey("path", "")


@pytest.mark.asyncio
async def test_ssh_key_password_requirement(ssh_infrastructures):
    for infrastructure in ssh_infrastructures:
        key_type = infrastructure["ssh_key"]["type"]
        key_path = infrastructure["ssh_key"]["path"]
        key_password = infrastructure["ssh_key"]["password"]
        pkey = await ssh.get_pkey(key_path, key_password)
        assert pkey.get_algorithm() == key_type


@pytest.mark.asyncio
async def test_wrong_ssh_key_password(ssh_infrastructures):
    for infrastructure in ssh_infrastructures:
        key_path = infrastructure["ssh_key"]["path"]
        key_password = "wrong password"
        with pytest.raises(asyncssh.KeyEncryptionError):
            await ssh.get_pkey(key_path, key_password)


@pytest.mark.asyncio
async def test_non_existent_ssh_key_path(ssh_infrastructures):
    for infrastructure in ssh_infrastructures:
        key_path = "/non-existent/path"
        key_password = infrastructure["ssh_key"]["password"]
        with pytest.raises(FileNotFoundError):
            await ssh.get_pkey(key_path, key_password)


@patch("asyncssh.connect")
@pytest.mark.asyncio
async def test_ssh_command(connect_mock, ssh_infrastructures):
    for infrastructure in ssh_infrastructures:
        key_path = infrastructure["ssh_key"]["path"]
        key_password = infrastructure["ssh_key"]["password"]
        pkey = await ssh.get_pkey(key_path, key_password)
        host = infrastructure["host"]
        username = infrastructure["username"]
        hostname = infrastructure["hostname"]
        command = "hostname"
        run_mock = AsyncMock()
        run_mock.run.return_value = MagicMock(
            stdout=f"{hostname}\n", stderr="")
        connect_mock.return_value.__aenter__.return_value = run_mock
        stdout, stderr = await ssh.exec_command(host, username, pkey, command)
        assert stdout == hostname
        assert stderr == ""


@patch("asyncssh.connect")
@pytest.mark.asyncio
async def test_ssh_sftp_upload(connect_mock, ssh_infrastructures):
    for infrastructure in ssh_infrastructures:
        key_path = infrastructure["ssh_key"]["path"]
        key_password = infrastructure["ssh_key"]["password"]
        pkey = await ssh.get_pkey(key_path, key_password)
        host = infrastructure["host"]
        username = infrastructure["username"]
        async with aiofiles.tempfile.TemporaryDirectory() as tmp_dir:
            local_src = Path(tmp_dir) / "test_file.txt"
            local_src.touch()
            local_src.write_text("Some_text")
            remote_dst = Path("/tmp") / "test_file.txt"
            sftp_put_mock = AsyncMock()
            start_sftp_mock = MagicMock()
            start_sftp_mock.start_sftp_client.return_value.__aenter__.return_value = sftp_put_mock
            connect_mock.return_value.__aenter__.return_value = start_sftp_mock
            await ssh.sftp_upload(
                host, username, pkey,
                local_src, remote_dst
            )
