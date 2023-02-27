from typing import Tuple
from pathlib import Path

import aiofiles.os
import asyncssh


async def key_exists(key_path: str) -> bool:
    return await aiofiles.os.path.exists(key_path)


async def get_pkey(key_path: str, key_password: str) -> asyncssh.SSHKey:
    if not (key_path and key_password):
        raise AttributeError
    return asyncssh.read_private_key(key_path, key_password)


async def exec_command(
    host: str,
    username: str,
    pkey: asyncssh.SSHKey,
    command: str
) -> Tuple[str, str]:
    async with asyncssh.connect(
        host,
        username=username,
        client_keys=[pkey],
        known_hosts=None,  # TODO: security concern
    ) as conn:
        result = await conn.run(command, check=False)
        stdout = "".join(result.stdout).rstrip()
        stderr = "".join(result.stderr).rstrip()
        return stdout, stderr


async def sftp_upload(
    host: str,
    username: str,
    pkey: asyncssh.SSHKey,
    local_src: Path,
    remote_dst: Path
) -> None:
    async with asyncssh.connect(
        host,
        username=username,
        client_keys=[pkey],
        known_hosts=None,  # TODO: security concern
    ) as conn:
        async with conn.start_sftp_client() as sftp:
            await sftp.put(local_src, remote_dst)
