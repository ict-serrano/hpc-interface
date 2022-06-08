import json

from hpc.api.openapi.models.infrastructure import Infrastructure
from hpc.api.openapi.models.infrastructure_summary import InfrastructureSummary
import hpc.api.utils.persistence as persistence

def create(infrastructure: Infrastructure):
    persistence.save(persistence.get_cluster_directory(infrastructure.name), json.dumps(infrastructure.to_dict()))
    return InfrastructureSummary.from_dict(infrastructure.to_dict())

def get(name: str):
    infrastructure = json.loads(persistence.get(persistence.get_cluster_directory(name)))
    return InfrastructureSummary.from_dict(infrastructure)