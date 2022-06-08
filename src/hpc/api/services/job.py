import json
from uuid import uuid4

import hpc.api.utils.ssh as ssh
import hpc.api.utils.persistence as persistence
from hpc.api.openapi.models.job_request import JobRequest
from hpc.api.openapi.models.job_status import JobStatus
from hpc.api.openapi.models.job_status_code import JobStatusCode

def submit(job_request: JobRequest):

    infrastructure = json.loads(persistence.get(persistence.get_cluster_directory(job_request.infrastructure)))
    key_type = infrastructure["ssh-key"]["type"]
    key_path = infrastructure["ssh-key"]["path"]
    key_password = infrastructure["ssh-key"]["password"]
    pkey = ssh.get_pkey(key_type, key_path, key_password)
    host = infrastructure["host"]
    username = infrastructure["username"]
    command = "cd test/ && qsub test-job-openmpi-example.sh"

    stdout, stderr = ssh.exec_command(host, username, pkey, command)
    job_id = str(uuid4())
    job_scheduler_id = stdout

    job_status = JobStatus(
        id=job_id,
        scheduler_id=job_scheduler_id,
        status=JobStatusCode.QUEUED
    )

    persistence.save(persistence.get_job_directory(job_id), json.dumps(job_status.to_dict()))

    return job_status