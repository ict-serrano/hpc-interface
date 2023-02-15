import pytest
from uuid import UUID

import hpc.api.services.job as job
from hpc.api.openapi.models.job_request import JobRequest
from hpc.api.openapi.models.service_name import ServiceName
from hpc.api.openapi.models.job_status_code import JobStatusCode
from hpc.api.openapi.models.hpc_scheduler_type import HPCSchedulerType
import hpc.api.utils.persistence as persistence

def mock_ssh_command_new_scheduler_id_pbs(*args, **kwargs):
    return "some_id", ""

def mock_ssh_command_new_scheduler_id_slurm(*args, **kwargs):
    return "Submitted batch job 1763", ""

def mock_ssh_command_job_status_pbs(*args, **kwargs):
    return "C", ""

def mock_ssh_command_job_status_slurm(*args, **kwargs):
    return "COMPLETED", ""

def test_job_submission_pbs(ssh_infrastructures, mocker):
    mocker.patch('hpc.api.utils.ssh.exec_command', new=mock_ssh_command_new_scheduler_id_pbs)
    job_request = JobRequest(
        services=[
            { "name": ServiceName.KALMAN_FILTER, "version": "0.0.1" },
            { "name": ServiceName.FFT_FILTER, "version": "0.0.1" }
        ],
        infrastructure=ssh_infrastructures[0]["name"],
        params={}
    )
    job_status = job.submit(job_request)
    assert UUID(job_status.id, version=4)
    assert len(job_status.scheduler_id) > 0
    assert job_status.infrastructure == ssh_infrastructures[0]["name"]
    assert job_status.status == JobStatusCode.QUEUED
    # TODO: PBS does not have exit code as the output -> find a way to retrieve the exit code
    # assert job_status.exit_code is None
    # assert job_status.success is None
    assert persistence.get(persistence.get_job_directory(job_status.id))
    pytest.pbs_job_id = job_status.id

def test_job_submission_slurm(ssh_infrastructures, mocker):
    mocker.patch('hpc.api.utils.ssh.exec_command', new=mock_ssh_command_new_scheduler_id_slurm)
    job_request = JobRequest(
        services=[
            { "name": ServiceName.KALMAN_FILTER, "version": "0.0.1" },
            { "name": ServiceName.FFT_FILTER, "version": "0.0.1" }
        ],
        infrastructure=ssh_infrastructures[1]["name"],
        params={}
    )
    job_status = job.submit(job_request)
    assert UUID(job_status.id, version=4)
    assert len(job_status.scheduler_id) > 0
    assert job_status.scheduler_id.isnumeric()
    assert job_status.infrastructure == ssh_infrastructures[1]["name"]
    assert job_status.status == JobStatusCode.QUEUED
    # TODO: PBS does not have exit code as the output -> find a way to retrieve the exit code
    # assert job_status.exit_code is None
    # assert job_status.success is None
    assert persistence.get(persistence.get_job_directory(job_status.id))
    pytest.slurm_job_id = job_status.id

def test_job_retrieval_pbs(ssh_infrastructures, mocker):
    mocker.patch('hpc.api.utils.ssh.exec_command', new=mock_ssh_command_job_status_pbs)
    job_status = job.get(pytest.pbs_job_id)
    assert len(job_status.scheduler_id) > 0
    assert job_status.infrastructure == ssh_infrastructures[0]["name"]
    assert job_status.status in [JobStatusCode.QUEUED, JobStatusCode.COMPLETED, JobStatusCode.RUNNING]
    # assert job_status.exit_code == 0
    # assert job_status.success == True

def test_job_retrieval_slurm(ssh_infrastructures, mocker):
    mocker.patch('hpc.api.utils.ssh.exec_command', new=mock_ssh_command_job_status_slurm)
    job_status = job.get(pytest.slurm_job_id)
    assert len(job_status.scheduler_id) > 0
    assert job_status.infrastructure == ssh_infrastructures[1]["name"]
    assert job_status.status in [JobStatusCode.QUEUED, JobStatusCode.COMPLETED, JobStatusCode.RUNNING]
    # assert job_status.exit_code == 0
    # assert job_status.success == True

def test_non_existent_job():
    with pytest.raises(KeyError):
        job.get("non_existent_infrastructure")