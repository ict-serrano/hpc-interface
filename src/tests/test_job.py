import json
from uuid import UUID

import hpc.api.services.job as job
from hpc.api.openapi.models.job_request import JobRequest
from hpc.api.openapi.models.service_name import ServiceName
from hpc.api.openapi.models.job_status_code import JobStatusCode
import hpc.api.utils.persistence as persistence

def test_job_submission(ssh_infrastructures):
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
    assert job_status.status == JobStatusCode.QUEUED
    assert job_status.exit_code is None
    assert job_status.success is None

    assert persistence.get(persistence.get_job_directory(job_status.id))