import os
import pytest
import yaml

import hpc.api.utils.ssh as ssh

@pytest.fixture
def ssh_infrastructures():
    fixture = "{}/{}".format(os.path.dirname(__file__), "fixture.infrastructure.yaml")
    with open(fixture, 'r') as stream:
        return yaml.safe_load(stream)

def test_ssh_key_existence(ssh_infrastructures):
    for infrastructure in ssh_infrastructures:
        key_path = infrastructure["ssh-key"]["path"]
        assert ssh.key_exists(key_path)

def test_ssh_key_password_requirement(ssh_infrastructures):
    for infrastructure in ssh_infrastructures:
        key_type = infrastructure["ssh-key"]["type"]
        key_path = infrastructure["ssh-key"]["path"]
        key_password = infrastructure["ssh-key"]["password"]
        pkey = ssh.get_pkey(key_type, key_path, key_password)
        assert pkey.get_name() == key_type

def test_ssh_key_types(ssh_infrastructures):
    for infrastructure in ssh_infrastructures:
        key_type = "ssh-not-supported-type"
        key_path = infrastructure["ssh-key"]["path"]
        key_password = infrastructure["ssh-key"]["password"]
        with pytest.raises(NotImplementedError):
            pkey = ssh.get_pkey(key_type, key_path, key_password)

@pytest.mark.online
def test_ssh_command(ssh_infrastructures):
    for infrastructure in ssh_infrastructures:
        key_type = infrastructure["ssh-key"]["type"]
        key_path = infrastructure["ssh-key"]["path"]
        key_password = infrastructure["ssh-key"]["password"]
        pkey = ssh.get_pkey(key_type, key_path, key_password)
        host = infrastructure["host"]
        username = infrastructure["username"]
        hostname = infrastructure["hostname"]
        command = "hostname"
        stdout, stderr = ssh.exec_command(host, username, pkey, command)
        assert stdout == hostname