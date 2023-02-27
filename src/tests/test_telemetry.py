import pytest

import hpc.api.services.telemetry as telemetry

from hpc.api.utils.resource_parser import SlurmNode, SlurmJob
from hpc.api.openapi.models.infrastructure import Infrastructure


async def mock_ssh_command(*args, **kwargs):
    return "", ""


def mock_slurm_nodes_info(*args, **kwargs):
    return [
        SlurmNode(
            "node01", "node01", "profile", "allocated", 128, 1, 64, 2, 128
        ),

        SlurmNode(
            "node02", "node02", "profile", "idle", 32, 2, 8, 2, 64
        ),
    ]


def mock_slurm_jobs_info(*args, **kwargs):
    return [
        SlurmJob(
            "1775", 128, 1, "2022-06-13T14:15:46", "*", "*", "*", "59:51", 0, "node01", "profile", "RUNNING", "(null)"
        ),
        SlurmJob(
            "1776", 128, 1, "N/A", "*", "*", "*", "1:00:00", 0, "", "profile", "PENDING", "node01"
        ),
        SlurmJob(
            "1777", 128, 1, "N/A", "*", "*", "*", "1:00:00", 0, "", "profile", "PENDING", "node01"
        ),
    ]


@pytest.mark.asyncio
async def test_slurm_idle_resources(assh_infrastructures):
    ssh_infrastructures = await assh_infrastructures
    nodes = [
        SlurmNode(
            "node01", "node01", "profile", "idle", 128, 1, 64, 2, 128
        ),

        SlurmNode(
            "node02", "node02", "profile", "idle", 32, 2, 8, 2, 64
        ),
    ]

    jobs = []

    infrastructure = Infrastructure.from_dict(ssh_infrastructures[1])
    telemetry_data = telemetry.derive_slurm_telemetry(
        infrastructure, nodes, jobs)

    assert telemetry_data.name == infrastructure.name
    assert telemetry_data.host == infrastructure.host
    assert telemetry_data.hostname == infrastructure.hostname
    assert telemetry_data.scheduler == infrastructure.scheduler
    assert telemetry_data.partitions[0].name == "profile"
    assert telemetry_data.partitions[0].total_nodes == 2
    assert telemetry_data.partitions[0].avail_nodes == 2
    assert telemetry_data.partitions[0].total_cpus == 160
    assert telemetry_data.partitions[0].avail_cpus == 160
    assert telemetry_data.partitions[0].running_jobs == 0
    assert telemetry_data.partitions[0].queued_jobs == 0


@pytest.mark.asyncio
async def test_slurm_allocated_resources(assh_infrastructures):
    ssh_infrastructures = await assh_infrastructures
    nodes = mock_slurm_nodes_info()
    jobs = mock_slurm_jobs_info()

    infrastructure = Infrastructure.from_dict(ssh_infrastructures[1])
    telemetry_data = telemetry.derive_slurm_telemetry(
        infrastructure, nodes, jobs)

    assert telemetry_data.name == infrastructure.name
    assert telemetry_data.host == infrastructure.host
    assert telemetry_data.hostname == infrastructure.hostname
    assert telemetry_data.scheduler == infrastructure.scheduler
    assert telemetry_data.partitions[0].name == "profile"
    assert telemetry_data.partitions[0].total_nodes == 2
    assert telemetry_data.partitions[0].avail_nodes == 1
    assert telemetry_data.partitions[0].total_cpus == 160
    assert telemetry_data.partitions[0].avail_cpus == 32
    assert telemetry_data.partitions[0].running_jobs == 1
    assert telemetry_data.partitions[0].queued_jobs == 2


@pytest.mark.asyncio
async def test_get_slurm_telemetry(assh_infrastructures, mocker):
    ssh_infrastructures = await assh_infrastructures
    mocker.patch('hpc.api.utils.async_ssh.exec_command', new=mock_ssh_command)
    mocker.patch('hpc.api.utils.resource_parser.get_slurm_nodes_info',
                 new=mock_slurm_nodes_info)
    mocker.patch('hpc.api.utils.resource_parser.get_slurm_jobs_info',
                 new=mock_slurm_jobs_info)
    telemetry_data = await telemetry.get(ssh_infrastructures[1]["name"])
    assert telemetry_data.name == ssh_infrastructures[1]["name"]
    assert telemetry_data.host == ssh_infrastructures[1]["host"]
    assert telemetry_data.hostname == ssh_infrastructures[1]["hostname"]
    assert telemetry_data.scheduler == ssh_infrastructures[1]["scheduler"]
    assert telemetry_data.partitions[0].name == "profile"
    assert telemetry_data.partitions[0].total_nodes == 2
    assert telemetry_data.partitions[0].avail_nodes == 1
    assert telemetry_data.partitions[0].total_cpus == 160
    assert telemetry_data.partitions[0].avail_cpus == 32
    assert telemetry_data.partitions[0].running_jobs == 1
    assert telemetry_data.partitions[0].queued_jobs == 2
