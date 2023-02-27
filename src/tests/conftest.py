import os
import pytest
import yaml
import json

import hpc.api.utils.persistence as apersistence


@pytest.fixture
async def ssh_infrastructures():
    default_fixture = "{}/{}".format(os.path.dirname(__file__),
                                     "fixture.infrastructure.yaml")
    fixture = os.getenv(
        "HPC_GATEWAY_TEST_INFRASTRUCTURE_FIXTURE", default_fixture)
    ssh_infrastructures = []
    with open(fixture, 'r') as stream:
        ssh_infrastructures = yaml.safe_load(stream)
    for infrastructure in ssh_infrastructures:
        await apersistence.save(apersistence.get_cluster_directory(
            infrastructure["name"]), json.dumps(infrastructure))
    return ssh_infrastructures
