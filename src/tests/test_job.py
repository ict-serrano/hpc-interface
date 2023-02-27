import pytest
from unittest.mock import patch
from uuid import UUID
import asyncio

import hpc.api.services.job as job
from hpc.api.openapi.models.job_request import JobRequest
from hpc.api.openapi.models.service_name import ServiceName
from hpc.api.openapi.models.job_status_code import JobStatusCode
import hpc.api.utils.persistence as persistence


async def mock_ssh_command_new_scheduler_id_pbs(*args, **kwargs):
    return "some_id", ""


async def mock_ssh_command_new_scheduler_id_slurm(*args, **kwargs):
    return "Submitted batch job 1763", ""


async def mock_ssh_command_job_status_pbs(*args, **kwargs):
    return "C", ""


async def mock_ssh_command_job_status_slurm(*args, **kwargs):
    return "COMPLETED", ""


def ssh_pbs_calls_responses(n):
    i = 0
    while i < n:
        if i == 0:
            yield "some_id", ""
        elif i < 3:
            yield "Q", ""
        elif i < 5:
            yield "R", ""
        else:
            yield "C", ""
        i += 1


def ssh_slurm_calls_responses(n):
    i = 0
    while i < n:
        if i == 0:
            yield "Submitted batch job 1763", ""
        elif i < 3:
            yield "PENDING", ""
        elif i < 5:
            yield "RUNNING", ""
        else:
            yield "COMPLETED", ""
        i += 1


@pytest.fixture
async def submit_pbs_job(ssh_infrastructures):
    ssh_infrastructures = await ssh_infrastructures
    job_request = JobRequest(
        services=[
            {"name": ServiceName.KALMAN_FILTER, "version": "0.0.1"},
            {"name": ServiceName.FFT_FILTER, "version": "0.0.1"}
        ],
        infrastructure=ssh_infrastructures[0]["name"],
        params={},
        watch_period=0.1
    )
    job_status = await job.submit(job_request)
    return job_request, job_status


@pytest.fixture
async def submit_slurm_job(ssh_infrastructures):
    ssh_infrastructures = await ssh_infrastructures
    job_request = JobRequest(
        services=[
            {"name": ServiceName.KALMAN_FILTER, "version": "0.0.1"},
            {"name": ServiceName.FFT_FILTER, "version": "0.0.1"}
        ],
        infrastructure=ssh_infrastructures[1]["name"],
        params={},
        watch_period=0.1
    )
    job_status = await job.submit(job_request)
    return job_request, job_status


@patch("hpc.api.utils.ssh.exec_command", side_effect=ssh_pbs_calls_responses(10))
@pytest.mark.asyncio
async def test_job_submission_pbs(ssh_mock, submit_pbs_job):
    job_request, job_status = await submit_pbs_job
    assert UUID(job_status.id, version=4)
    assert job_status.scheduler_id
    assert job_status.infrastructure == job_request.infrastructure
    assert job_status.status == JobStatusCode.QUEUED
    # TODO: PBS does not have exit code as the output -> find a way to retrieve the exit code
    # assert job_status.exit_code is None
    # assert job_status.success is None
    assert await persistence.get(persistence.get_job_directory(job_status.id))
    while True:
        job_status = await job.get(job_status.id)
        if job_status.status in [JobStatusCode.QUEUED, JobStatusCode.RUNNING]:
            await asyncio.sleep(0.1)
            continue
        else:
            assert job_status.scheduler_id
            assert job_status.infrastructure
            assert job_status.status in [JobStatusCode.COMPLETED]
            break


@patch("hpc.api.utils.ssh.exec_command", side_effect=ssh_slurm_calls_responses(10))
@pytest.mark.asyncio
async def test_job_submission_slurm(ssh_mock, submit_slurm_job):
    job_request, job_status = await submit_slurm_job
    assert UUID(job_status.id, version=4)
    assert len(job_status.scheduler_id) > 0
    assert job_status.scheduler_id.isnumeric()
    assert job_status.infrastructure == job_request.infrastructure
    assert job_status.status == JobStatusCode.QUEUED
    # TODO: PBS does not have exit code as the output -> find a way to retrieve the exit code
    # assert job_status.exit_code is None
    # assert job_status.success is None
    assert await persistence.get(persistence.get_job_directory(job_status.id))
    while True:
        job_status = await job.get(job_status.id)
        if job_status.status in [JobStatusCode.QUEUED, JobStatusCode.RUNNING]:
            await asyncio.sleep(0.1)
            continue
        else:
            assert job_status.scheduler_id
            assert job_status.infrastructure
            assert job_status.status in [JobStatusCode.COMPLETED]
            break


@pytest.mark.asyncio
async def test_non_existent_job():
    with pytest.raises(KeyError):
        await job.get("non_existent_infrastructure")
