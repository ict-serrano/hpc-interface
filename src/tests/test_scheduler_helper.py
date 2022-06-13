import pytest

from hpc.api.openapi.models.job_status_code import JobStatusCode
from hpc.api.openapi.models.hpc_scheduler_type import HPCSchedulerType
from hpc.api.utils.scheduler_helper import SchedulerHelperFactory

def test_non_existent_scheduler():
    with pytest.raises(NotImplementedError):
        helper = SchedulerHelperFactory.helper("non-existent")

def test_scheduler_types_submit_command():
    helper = SchedulerHelperFactory.helper(HPCSchedulerType.PBS)
    assert helper.get_submit_command() == "qsub"
    helper = SchedulerHelperFactory.helper(HPCSchedulerType.SLURM)
    assert helper.get_submit_command() == "sbatch"

def test_scheduler_types_retrieve_command():
    helper = SchedulerHelperFactory.helper(HPCSchedulerType.PBS)
    assert helper.get_job_status_code_command("123").split()[0] == "qstat"
    helper = SchedulerHelperFactory.helper(HPCSchedulerType.SLURM)
    assert helper.get_job_status_code_command("123").split()[0] == "scontrol"

def test_parse_job_scheduler_id():
    helper = SchedulerHelperFactory.helper(HPCSchedulerType.PBS)
    assert helper.parse_job_scheduler_id("123.abc") == "123.abc"
    helper = SchedulerHelperFactory.helper(HPCSchedulerType.SLURM)
    assert helper.parse_job_scheduler_id("Submitted batch job 1763") == "1763"
    with pytest.raises(ValueError):
        helper.parse_job_scheduler_id("does not contain numerics")

def test_job_status_code_pbs():
    helper = SchedulerHelperFactory.helper(HPCSchedulerType.PBS)
    assert helper.get_job_status_code("C") == JobStatusCode.COMPLETED
    assert helper.get_job_status_code("Q") == JobStatusCode.QUEUED
    assert helper.get_job_status_code("R") == JobStatusCode.RUNNING
    with pytest.raises(NotImplementedError):
        helper.get_job_status_code("non-existent")

def test_job_status_code_slurm():
    helper = SchedulerHelperFactory.helper(HPCSchedulerType.SLURM)
    assert helper.get_job_status_code("COMPLETED") == JobStatusCode.COMPLETED
    assert helper.get_job_status_code("FAILED") == JobStatusCode.COMPLETED
    assert helper.get_job_status_code("PENDING") == JobStatusCode.QUEUED
    assert helper.get_job_status_code("COMPLETING") == JobStatusCode.RUNNING
    assert helper.get_job_status_code("RUNNING") == JobStatusCode.RUNNING
    with pytest.raises(NotImplementedError):
        helper.get_job_status_code("non-existent")