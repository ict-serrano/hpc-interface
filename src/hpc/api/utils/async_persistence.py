from typing import Any

from hpc.api.log import get_logger
logger = get_logger(__name__)

_storage = {}

def get_cluster_directory(name: str) -> str:
    return f"/serrano/orchestrator/clusters/cluster/hpc/{name}"

def get_job_directory(id: str) -> str:
    return f"/serrano/orchestrator/jobs/job/hpc/{id}"

def get_file_transfer_directory(id: str) -> str:
    return f"/serrano/orchestrator/file_transfers/file_transfer/hpc/{id}"

async def save(directory: str, data: Any) -> None:
    _storage[directory] = data

async def get(directory: str) -> Any:
    return _storage[directory]