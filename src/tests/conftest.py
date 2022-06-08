import os
import pytest
import yaml
import json

import hpc.api.utils.persistence as persistence

@pytest.fixture
def ssh_infrastructures():
    fixture = "{}/{}".format(os.path.dirname(__file__), "fixture.infrastructure.yaml")
    ssh_infrastructures = []
    with open(fixture, 'r') as stream:
        ssh_infrastructures = yaml.safe_load(stream)
    for infrastructure in ssh_infrastructures:
        persistence.save(persistence.get_cluster_directory(infrastructure["name"]), json.dumps(infrastructure))
    return ssh_infrastructures