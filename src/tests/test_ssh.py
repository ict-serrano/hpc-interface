import os
import pytest
import yaml

import hpc.api.utils.ssh as ssh
from unittest.mock import MagicMock
from tempfile import TemporaryDirectory
from pathlib import Path


def test_ssh_key_existence(ssh_infrastructures):
    for infrastructure in ssh_infrastructures:
        key_path = infrastructure["ssh_key"]["path"]
        assert ssh.key_exists(key_path)


def test_ssh_key_password_requirement(ssh_infrastructures):
    for infrastructure in ssh_infrastructures:
        key_type = infrastructure["ssh_key"]["type"]
        key_path = infrastructure["ssh_key"]["path"]
        key_password = infrastructure["ssh_key"]["password"]
        pkey = ssh.get_pkey(key_type, key_path, key_password)
        assert pkey.get_name() == key_type


def test_ssh_key_types(ssh_infrastructures):
    for infrastructure in ssh_infrastructures:
        key_type = "ssh-not-supported-type"
        key_path = infrastructure["ssh_key"]["path"]
        key_password = infrastructure["ssh_key"]["password"]
        with pytest.raises(NotImplementedError):
            pkey = ssh.get_pkey(key_type, key_path, key_password)


def test_ssh_command(mocker, ssh_infrastructures):
    for infrastructure in ssh_infrastructures:
        key_type = infrastructure["ssh_key"]["type"]
        key_path = infrastructure["ssh_key"]["path"]
        key_password = infrastructure["ssh_key"]["password"]
        pkey = ssh.get_pkey(key_type, key_path, key_password)
        host = infrastructure["host"]
        username = infrastructure["username"]
        hostname = infrastructure["hostname"]
        command = "hostname"
        stdout_mock = MagicMock()
        stdout_mock.readlines.return_value = hostname + "\n"
        mocker.patch("paramiko.client.SSHClient.connect")
        mocker.patch("paramiko.client.SSHClient.close")
        mocker.patch(
            "paramiko.client.SSHClient.exec_command",
            return_value=(MagicMock(), stdout_mock, MagicMock()))
        stdout, stderr = ssh.exec_command(host, username, pkey, command)
        assert stdout == hostname


def test_ssh_sftp_upload(mocker, ssh_infrastructures):
    for infrastructure in ssh_infrastructures:
        key_type = infrastructure["ssh_key"]["type"]
        key_path = infrastructure["ssh_key"]["path"]
        key_password = infrastructure["ssh_key"]["password"]
        pkey = ssh.get_pkey(key_type, key_path, key_password)
        host = infrastructure["host"]
        username = infrastructure["username"]
        hostname = infrastructure["hostname"]
        command = "hostname"
        sftp_mock = MagicMock()
        mocker.patch("paramiko.client.SSHClient.connect")
        mocker.patch("paramiko.client.SSHClient.close")
        mocker.patch(
            "paramiko.client.SSHClient.open_sftp",
            return_value=sftp_mock)
        with TemporaryDirectory() as tmp_dir:
            local_src = Path(tmp_dir) / "test_file.txt"
            local_src.touch()
            local_src.write_text("Some_text")
            remote_dst = Path("/tmp") / "test_file.txt"
            ssh.sftp_upload(
                host, username, pkey,
                str(local_src.resolve()), str(remote_dst.resolve()))
