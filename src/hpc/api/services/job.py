import json
from uuid import uuid4

import hpc.api.utils.async_ssh as ssh
import hpc.api.utils.async_persistence as persistence
from hpc.api.utils.scheduler_helper import SchedulerHelperFactory
from hpc.api.openapi.models.job_request import JobRequest
from hpc.api.openapi.models.job_status import JobStatus
from hpc.api.openapi.models.job_status_code import JobStatusCode


async def submit(job_request: JobRequest) -> JobStatus:
    infrastructure = json.loads(await persistence.get(
        persistence.get_cluster_directory(job_request.infrastructure)))
    key_path = infrastructure["ssh_key"]["path"]
    key_password = infrastructure["ssh_key"]["password"]
    pkey = await ssh.get_pkey(key_path, key_password)
    host = infrastructure["host"]
    username = infrastructure["username"]
    scheduler = infrastructure["scheduler"]
    helper = SchedulerHelperFactory.helper(scheduler)

    # TODO: Change to template and EOF submission, once the HPC services are deployed
    command = "cd test/ && {} test-job-openmpi-example.sh".format(
        helper.get_submit_command())

    stdout, stderr = await ssh.exec_command(host, username, pkey, command)
    job_id = str(uuid4())
    job_scheduler_id = helper.parse_job_scheduler_id(stdout)

    job_status = JobStatus(
        id=job_id,
        scheduler_id=job_scheduler_id,
        infrastructure=infrastructure["name"],
        status=JobStatusCode.QUEUED
    )

    await persistence.save(
        persistence.get_job_directory(job_id),
        json.dumps(job_status.to_dict())
    )

    return job_status


async def get(job_id: str) -> JobStatus:
    job_status = JobStatus.from_dict(
        json.loads(await persistence.get(persistence.get_job_directory(job_id))))
    infrastructure = json.loads(await persistence.get(
        persistence.get_cluster_directory(job_status.infrastructure)))
    key_path = infrastructure["ssh_key"]["path"]
    key_password = infrastructure["ssh_key"]["password"]
    pkey = await ssh.get_pkey(key_path, key_password)
    host = infrastructure["host"]
    username = infrastructure["username"]
    scheduler = infrastructure["scheduler"]
    helper = SchedulerHelperFactory.helper(scheduler)
    command = helper.get_job_status_code_command(job_status.scheduler_id)

    stdout, stderr = await ssh.exec_command(host, username, pkey, command)
    job_status_code = helper.get_job_status_code(stdout)

    job_status.status = job_status_code

    await persistence.save(
        persistence.get_job_directory(job_id),
        json.dumps(job_status.to_dict())
    )

    return job_status
