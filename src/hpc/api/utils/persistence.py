__storage = {}

def get_cluster_directory(name):
    return "/serrano/orchestrator/clusters/cluster/hpc/{}".format(name)

def get_job_directory(id):
    return "/serrano/orchestrator/jobs/job/hpc/{}".format(id)

def get_file_transfer_directory(id):
    return "/serrano/orchestrator/file_transfers/file_transfer/hpc/{}".format(id)

def save(directory, data):
    __storage[directory] = data

def get(directory):
    return __storage[directory]