import json
from uuid import uuid4
import re

import hpc.api.utils.ssh as ssh
import hpc.api.utils.persistence as persistence
from hpc.api.openapi.models.job_request import JobRequest
from hpc.api.openapi.models.job_status import JobStatus
from hpc.api.openapi.models.job_status_code import JobStatusCode
from hpc.api.openapi.models.hpc_scheduler_type import HPCSchedulerType

def submit(job_request: JobRequest):
    infrastructure = json.loads(persistence.get(persistence.get_cluster_directory(job_request.infrastructure)))
    key_type = infrastructure["ssh_key"]["type"]
    key_path = infrastructure["ssh_key"]["path"]
    key_password = infrastructure["ssh_key"]["password"]
    pkey = ssh.get_pkey(key_type, key_path, key_password)
    host = infrastructure["host"]
    username = infrastructure["username"]
    scheduler = infrastructure["scheduler"]
    command = "cd test/ && {} test-job-openmpi-example.sh".format(get_submit_command(scheduler))

    stdout, stderr = ssh.exec_command(host, username, pkey, command)
    job_id = str(uuid4())
    job_scheduler_id = parse_job_scheduler_id(scheduler, stdout) 

    job_status = JobStatus(
        id=job_id,
        scheduler_id=job_scheduler_id,
        infrastructure=infrastructure["name"],
        status=JobStatusCode.QUEUED
    )

    persistence.save(persistence.get_job_directory(job_id), json.dumps(job_status.to_dict()))

    return job_status

def get_submit_command(scheduler):
    if scheduler == HPCSchedulerType.PBS:
        return "qsub"
    elif scheduler == HPCSchedulerType.SLURM:
        return "sbatch"
    else:
        raise NotImplementedError("Unknown scheduler: {}".format(scheduler))

def parse_job_scheduler_id(scheduler, data):
    if scheduler == HPCSchedulerType.SLURM:
        result = re.search(r"\d+|$", data).group()
        if len(result) == 0:
            raise ValueError("Slurm job ID is incorrect")
        return result
    return data

def get(job_id: str):
    job_status = JobStatus.from_dict(json.loads(persistence.get(persistence.get_job_directory(job_id))))
    infrastructure = json.loads(persistence.get(persistence.get_cluster_directory(job_status.infrastructure)))
    key_type = infrastructure["ssh_key"]["type"]
    key_path = infrastructure["ssh_key"]["path"]
    key_password = infrastructure["ssh_key"]["password"]
    pkey = ssh.get_pkey(key_type, key_path, key_password)
    host = infrastructure["host"]
    username = infrastructure["username"]
    scheduler = infrastructure["scheduler"]
    command = get_job_status_code_command(scheduler, job_status.scheduler_id)

    stdout, stderr = ssh.exec_command(host, username, pkey, command)
    job_status_code = get_job_status_code(scheduler, stdout)

    job_status.status = job_status_code

    persistence.save(persistence.get_job_directory(job_id), json.dumps(job_status.to_dict()))

    return job_status

def get_job_status_code_command(scheduler, scheduler_id):
    if scheduler == HPCSchedulerType.PBS:
        return "qstat -f {} | grep 'job_state' | grep -o '.$'".format(scheduler_id)
    elif scheduler == HPCSchedulerType.SLURM:
        return "scontrol show job -dd {} | grep -o 'JobState=[A-Z]*'".format(scheduler_id)
    else:
        raise NotImplementedError("Unknown scheduler: {}".format(scheduler))

def get_job_status_code(scheduler, status):
    if scheduler == HPCSchedulerType.PBS:
        return get_job_status_code_pbs(status)
    elif scheduler == HPCSchedulerType.SLURM:
        return get_job_status_code_slurm(status)
    else:
        raise NotImplementedError("Unknown scheduler: {}".format(scheduler))

def get_job_status_code_pbs(status):
    if status == 'C':
        return JobStatusCode.COMPLETED
    elif status == 'Q':
        return JobStatusCode.QUEUED
    elif status == 'R':
        return JobStatusCode.RUNNING
    else:
        raise NotImplementedError("PBS status is undefined or not supported: {}".format(status))

def get_job_status_code_slurm(status):
    if status in ["COMPLETED", "FAILED"]:
        return JobStatusCode.COMPLETED
    elif status == "PENDING":
        return JobStatusCode.QUEUED
    elif status in ["COMPLETING", "RUNNING"]:
        return JobStatusCode.RUNNING
    else:
        raise NotImplementedError("Slurm status is undefined or not supported: {}".format(status))