import re
import hpc.api.utils.resource_parser as parser
from hpc.api.openapi.models.job_status_code import JobStatusCode
from hpc.api.openapi.models.hpc_scheduler_type import HPCSchedulerType

class SchedulerHelperFactory():
    @classmethod
    def helper(cls, scheduler):
        if scheduler == HPCSchedulerType.PBS:
            return PBSHelper()
        elif scheduler == HPCSchedulerType.SLURM:
            return SlurmHelper()
        else:
            raise NotImplementedError("Unknown scheduler: {}".format(scheduler))

class PBSHelper():
    def get_submit_command(self):
        return "qsub"

    def parse_job_scheduler_id(self, data):
        return data

    def get_job_status_code_command(self, scheduler_id):
        return "qstat -f {} | grep 'job_state' | grep -o '.$'".format(scheduler_id)

    def get_job_status_code(self, status):
        if status == 'C':
            return JobStatusCode.COMPLETED
        elif status == 'Q':
            return JobStatusCode.QUEUED
        elif status == 'R':
            return JobStatusCode.RUNNING
        else:
            raise NotImplementedError("PBS status is undefined or not supported: {}".format(status))

    def get_nodes_info_command(self):
        return "pbsnodes -a"

    def get_jobs_info_command(self):
        return "qstat -a"

    def get_nodes_info(self, data):
        return []

    def get_jobs_info(self, data):
        return []

class SlurmHelper():
    def get_submit_command(self):
        return "sbatch"

    def parse_job_scheduler_id(self, data):
        result = re.search(r"\d+|$", data).group()
        if len(result) == 0:
            raise ValueError("Slurm job ID is incorrect")
        return result

    def get_job_status_code_command(self, scheduler_id):
        return "scontrol show job -dd {} | grep -o 'JobState=[A-Z]*'".format(scheduler_id)

    def get_job_status_code(self, status):
        if status in ["COMPLETED", "FAILED"]:
            return JobStatusCode.COMPLETED
        elif status == "PENDING":
            return JobStatusCode.QUEUED
        elif status in ["COMPLETING", "RUNNING"]:
            return JobStatusCode.RUNNING
        else:
            raise NotImplementedError("Slurm status is undefined or not supported: {}".format(status))

    def get_nodes_info_command(self):
        return "sinfo -h -o '%n,%N,%R,%T,%c,%X,%Y,%Z,%m'"

    def get_jobs_info_command(self):
        return "squeue -h -o '%A,%C,%D,%e,%H,%I,%J,%L,%m,%N,%P,%T,%Y'"
    
    def get_nodes_info(self, data):
        return parser.get_slurm_nodes_info(data)
    
    def get_jobs_info(self, data):
        return parser.get_slurm_jobs_info(data)