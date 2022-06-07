import os

from paramiko.rsakey import RSAKey
from paramiko.ed25519key import Ed25519Key
from paramiko.client import SSHClient
from paramiko import AutoAddPolicy

def get_key_types():
    return ["ssh-rsa", "ssh-ed25519"]

def key_exists(key_path):
    return os.path.exists(key_path)

def get_pkey(key_type, key_path, key_password):
    if key_type == "ssh-rsa":
        return RSAKey.from_private_key_file(key_path, key_password)
    elif key_type == "ssh-ed25519":
        return Ed25519Key.from_private_key_file(key_path, key_password)
    else:
        raise NotImplementedError("Currently only RSA and Ed25519 key types are supported")

def exec_command(host, username, pkey, command):
    client = SSHClient()
    # TODO: security concern
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(hostname=host, username=username, pkey=pkey)
    stdin, stdout, stderr = client.exec_command(command)
    stdout = "".join(stdout.readlines()).rstrip()
    stderr = "".join(stderr.readlines()).rstrip()
    client.close()
    return stdout, stderr