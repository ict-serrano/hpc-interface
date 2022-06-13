import pytest
import hpc.api.utils.resource_parser as parser
from hpc.api.openapi.models.node_state_code import NodeStateCode
from hpc.api.openapi.models.job_status_code import JobStatusCode

@pytest.fixture
def slurm_nodes():
    return """\
node01,node01,profile,idle,128,1,64,2,128
node02,node02,profile,allocated,32,2,8,2,64
node03,node03,profile,mixed,32,2,8,2,64"""

@pytest.fixture
def slurm_jobs():
    return """\
1775,128,1,2022-06-13T14:15:46,*,*,*,59:51,0,node01,profile,RUNNING,(null)
1776,128,1,2022-06-13T13:15:56,*,*,*,59:50,0,node01,profile,COMPLETING,(null)
1777,128,1,N/A,*,*,*,1:00:00,0,,profile,PENDING,node01"""

def test_slurm_nodes_parser_empty_string():
    assert [] == parser.get_slurm_nodes_info("")

def test_slurm_nodes_parser(slurm_nodes):
    nodes = parser.get_slurm_nodes_info(slurm_nodes)
    assert nodes[0].hostname == "node01"
    assert nodes[0].node == "node01"
    assert nodes[0].partition == "profile"
    assert nodes[0].state == NodeStateCode.IDLE
    assert nodes[0].cpus == 128
    assert nodes[0].sockets == 1
    assert nodes[0].cores == 64
    assert nodes[0].threads == 2
    assert nodes[0].memory == 128

    assert nodes[1].hostname == "node02"
    assert nodes[1].node == "node02"
    assert nodes[1].partition == "profile"
    assert nodes[1].state == NodeStateCode.ALLOCATED
    assert nodes[1].cpus == 32
    assert nodes[1].sockets == 2
    assert nodes[1].cores == 8
    assert nodes[1].threads == 2
    assert nodes[1].memory == 64

    assert nodes[2].hostname == "node03"
    assert nodes[2].node == "node03"
    assert nodes[2].partition == "profile"
    assert nodes[2].state == NodeStateCode.MIXED
    assert nodes[2].cpus == 32
    assert nodes[2].sockets == 2
    assert nodes[2].cores == 8
    assert nodes[2].threads == 2
    assert nodes[2].memory == 64

def test_slurm_jobs_parser_empty_string():
    assert [] == parser.get_slurm_jobs_info("")


def test_slurm_jobs_parser(slurm_jobs):
    jobs = parser.get_slurm_jobs_info(slurm_jobs)
    assert jobs[0].scheduler_id == "1775"
    assert jobs[0].cpus == 128
    assert jobs[0].nodes == 1
    assert jobs[0].end_time == "2022-06-13T14:15:46"
    assert jobs[0].sockets_per_node == "*"
    assert jobs[0].cores_per_socket == "*"
    assert jobs[0].threads_per_core == "*"
    assert jobs[0].time_left == "59:51"
    assert jobs[0].min_memory == 0
    assert jobs[0].nodelist == "node01"
    assert jobs[0].partition == "profile"
    assert jobs[0].state == JobStatusCode.RUNNING
    assert jobs[0].schednodes == "(null)"

    assert jobs[1].scheduler_id == "1776"
    assert jobs[1].cpus == 128
    assert jobs[1].nodes == 1
    assert jobs[1].end_time == "2022-06-13T13:15:56"
    assert jobs[1].sockets_per_node == "*"
    assert jobs[1].cores_per_socket == "*"
    assert jobs[1].threads_per_core == "*"
    assert jobs[1].time_left == "59:50"
    assert jobs[1].min_memory == 0
    assert jobs[1].nodelist == "node01"
    assert jobs[1].partition == "profile"
    assert jobs[1].state == JobStatusCode.RUNNING
    assert jobs[1].schednodes == "(null)"

    assert jobs[2].scheduler_id == "1777"
    assert jobs[2].cpus == 128
    assert jobs[2].nodes == 1
    assert jobs[2].end_time == "N/A"
    assert jobs[2].sockets_per_node == "*"
    assert jobs[2].cores_per_socket == "*"
    assert jobs[2].threads_per_core == "*"
    assert jobs[2].time_left == "1:00:00"
    assert jobs[2].min_memory == 0
    assert jobs[2].nodelist == ""
    assert jobs[2].partition == "profile"
    assert jobs[2].state == JobStatusCode.QUEUED
    assert jobs[2].schednodes == "node01"