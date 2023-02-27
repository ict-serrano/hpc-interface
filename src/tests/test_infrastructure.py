import pytest

import hpc.api.services.infrastructure as infrastructure
from hpc.api.openapi.models.infrastructure import Infrastructure
import hpc.api.utils.persistence as persistence


@pytest.mark.asyncio
async def test_infrastructure_creation(ssh_infrastructures):
    ssh_infrastructures = await ssh_infrastructures
    data = ssh_infrastructures[0]
    infrastructure_request = Infrastructure.from_dict(data)
    new_infrastructure = await infrastructure.create(infrastructure_request)
    assert new_infrastructure.name == data["name"]
    assert new_infrastructure.host == data["host"]
    assert new_infrastructure.hostname == data["hostname"]
    assert new_infrastructure.scheduler == data["scheduler"]
    assert await persistence.get(
        persistence.get_cluster_directory(new_infrastructure.name))


@pytest.mark.asyncio
async def test_infrastructure_retrieval(ssh_infrastructures):
    ssh_infrastructures = await ssh_infrastructures
    data = ssh_infrastructures[0]
    new_infrastructure = await infrastructure.get(data["name"])
    assert new_infrastructure.name == data["name"]
    assert new_infrastructure.host == data["host"]
    assert new_infrastructure.hostname == data["hostname"]
    assert new_infrastructure.scheduler == data["scheduler"]


@pytest.mark.asyncio
async def test_non_existent_infrastructure():
    with pytest.raises(KeyError):
        await infrastructure.get("non_existent_infrastructure")
