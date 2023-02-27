import json

import hpc.api.utils.async_persistence as persistence
import hpc.api.utils.async_ssh as ssh

from hpc.api.openapi.models.infrastructure_telemetry import InfrastructureTelemetry
from hpc.api.openapi.models.node_state_code import NodeStateCode
from hpc.api.openapi.models.partition_telemetry import PartitionTelemetry
from hpc.api.openapi.models.job_status_code import JobStatusCode
from hpc.api.openapi.models.infrastructure_summary import InfrastructureSummary
from hpc.api.utils.scheduler_helper import SchedulerHelperFactory


def derive_slurm_telemetry(infrastructure, nodes, jobs):

    partitions = []
    partitions_dict = {}

    for node in nodes:
        if not (node.partition in partitions_dict):
            partitions_dict[node.partition] = {
                "name": node.partition,
                "total_nodes": 0,
                "avail_nodes": 0,
                "total_cpus": 0,
                "avail_cpus": 0,
                "running_jobs": 0,
                "queued_jobs": 0,
            }
        partitions_dict[node.partition]["total_nodes"] = partitions_dict[node.partition]["total_nodes"] + 1
        if node.state == NodeStateCode.IDLE:
            partitions_dict[node.partition]["avail_nodes"] = partitions_dict[node.partition]["avail_nodes"] + 1
        partitions_dict[node.partition]["total_cpus"] = partitions_dict[node.partition]["total_cpus"] + node.cpus
        partitions_dict[node.partition]["avail_cpus"] = partitions_dict[node.partition]["total_cpus"]
        partitions_dict[node.partition]["running_jobs"] = 0
        partitions_dict[node.partition]["queued_jobs"] = 0

    for job in jobs:
        if job.state == JobStatusCode.RUNNING:
            partitions_dict[job.partition]["avail_cpus"] = partitions_dict[job.partition]["avail_cpus"] - job.cpus
            partitions_dict[node.partition]["running_jobs"] = partitions_dict[node.partition]["running_jobs"] + 1
        elif job.state == JobStatusCode.QUEUED:
            partitions_dict[node.partition]["queued_jobs"] = partitions_dict[node.partition]["queued_jobs"] + 1

    for partition in partitions_dict:
        partitions.append(PartitionTelemetry.from_dict(
            partitions_dict[partition]))

    return InfrastructureTelemetry(
        name=infrastructure.name,
        host=infrastructure.host,
        hostname=infrastructure.hostname,
        scheduler=infrastructure.scheduler,
        partitions=partitions
    )


async def get(infrastructure_name: str):
    infrastructure = json.loads(await persistence.get(
        persistence.get_cluster_directory(infrastructure_name)))
    key_path = infrastructure["ssh_key"]["path"]
    key_password = infrastructure["ssh_key"]["password"]
    pkey = await ssh.get_pkey(key_path, key_password)
    host = infrastructure["host"]
    username = infrastructure["username"]
    scheduler = infrastructure["scheduler"]
    helper = SchedulerHelperFactory.helper(scheduler)
    command = helper.get_nodes_info_command()

    stdout, stderr = await ssh.exec_command(host, username, pkey, command)
    nodes = helper.get_nodes_info(stdout)

    command = helper.get_jobs_info_command()

    stdout, stderr = await ssh.exec_command(host, username, pkey, command)
    jobs = helper.get_jobs_info(stdout)

    # TODO: so far, only Slurm is supported
    return derive_slurm_telemetry(InfrastructureSummary.from_dict(infrastructure), nodes, jobs)
