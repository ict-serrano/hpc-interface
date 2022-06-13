import hpc.api.utils.scheduler_helper as scheduler_helper
from hpc.api.openapi.models.hpc_scheduler_type import HPCSchedulerType

class SlurmNode():
    def __init__(self,
        hostname, node, partition, state, cpus, 
        sockets, cores, threads, memory
    ):
        self.hostname = hostname
        self.node = node
        self.partition = partition
        self.state = state
        self.cpus = int(cpus)
        self.sockets = int(sockets)
        self.cores = int(cores)
        self.threads = int(threads)
        self.memory = int(memory)

class SlurmJob():
    def __init__(self,
        scheduler_id, cpus, nodes, end_time, sockets_per_node, 
        cores_per_socket, threads_per_core, time_left, min_memory,
        nodelist, partition, state, schednodes
    ):
        self.scheduler_id = scheduler_id
        self.cpus = int(cpus)
        self.nodes = int(nodes)
        self.end_time = end_time
        self.sockets_per_node = sockets_per_node
        self.cores_per_socket = cores_per_socket
        self.threads_per_core = threads_per_core
        self.time_left = time_left
        self.min_memory = int(min_memory)
        self.nodelist = nodelist
        self.partition = partition
        helper = scheduler_helper.SchedulerHelperFactory.helper(HPCSchedulerType.SLURM)
        self.state = helper.get_job_status_code(state)
        self.schednodes = schednodes

def get_slurm_nodes_info(data):
    nodes = []
    if data:
        for node_line in data.splitlines():
            nodes.append(SlurmNode(*node_line.split(",")))
    return nodes

def get_slurm_jobs_info(data):
    jobs = []
    if data:
        for job_line in data.splitlines():
            jobs.append(SlurmJob(*job_line.split(",")))
    return jobs