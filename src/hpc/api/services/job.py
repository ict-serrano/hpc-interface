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
        infrastructure=infrastructure["name"],
        status=JobStatusCode.QUEUED
    )

    persistence.save(persistence.get_job_directory(job_id), json.dumps(job_status.to_dict()))

    return job_status

def get(job_id: str):
    job_status = JobStatus.from_dict(json.loads(persistence.get(persistence.get_job_directory(job_id))))
    infrastructure = json.loads(persistence.get(persistence.get_cluster_directory(job_status.infrastructure)))
    key_type = infrastructure["ssh-key"]["type"]
    key_path = infrastructure["ssh-key"]["path"]
    key_password = infrastructure["ssh-key"]["password"]
    pkey = ssh.get_pkey(key_type, key_path, key_password)
    host = infrastructure["host"]
    username = infrastructure["username"]
    command = "qstat -f {} | grep 'job_state' | grep -o '.$'".format(job_status.scheduler_id)

    stdout, stderr = ssh.exec_command(host, username, pkey, command)
    job_status_code = get_pbs_job_status_code(stdout)

    job_status.status = job_status_code

    persistence.save(persistence.get_job_directory(job_id), json.dumps(job_status.to_dict()))

    return job_status

def get_pbs_job_status_code(status):
    if status == 'C':
        return JobStatusCode.COMPLETED
    elif status == 'Q':
        return JobStatusCode.QUEUED
    elif status == 'R':
        return JobStatusCode.RUNNING
    else:
        raise NotImplementedError("PBS status is undefined or not supported: {}".format(status))