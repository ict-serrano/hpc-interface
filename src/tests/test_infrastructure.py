import pytest

import hpc.api.services.infrastructure as infrastructure
from hpc.api.openapi.models.infrastructure import Infrastructure
import hpc.api.utils.persistence as persistence

def test_infrastructure_creation(ssh_infrastructures):
    data = ssh_infrastructures[0]
    infrastructure_request = Infrastructure.from_dict(data)
    new_infrastructure = infrastructure.create(infrastructure_request)
    assert new_infrastructure.name == data["name"]
    assert new_infrastructure.host == data["host"]
    assert new_infrastructure.hostname == data["hostname"]
    assert new_infrastructure.scheduler == data["scheduler"]
    assert persistence.get(persistence.get_cluster_directory(new_infrastructure.name))

def test_infrastructure_retrieval(ssh_infrastructures):
    data = ssh_infrastructures[0]
    new_infrastructure = infrastructure.get(data["name"])
    assert new_infrastructure.name == data["name"]
    assert new_infrastructure.host == data["host"]
    assert new_infrastructure.hostname == data["hostname"]
    assert new_infrastructure.scheduler == data["scheduler"]

def test_non_existent_infrastructure():
    with pytest.raises(KeyError):
        infrastructure.get("non_existent_infrastructure")