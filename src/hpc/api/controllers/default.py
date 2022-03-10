import uuid

from hpc.api.openapi.models.hpc_service import HPCService  # noqa: E501
from hpc.api.openapi.models.service_name import ServiceName
from hpc.api.openapi.models.service_type import ServiceType

def get_all_services():  # noqa: E501
    """Get all available services

     # noqa: E501


    :rtype: List[HPCService]
    """

    services = [
        HPCService(
            id=str(uuid.uuid4()),
            name=ServiceName.KALMAN_FILTER,
            version="0.0.1",
            type=ServiceType.FILTER
        ),
        HPCService(
            id=str(uuid.uuid4()),
            name=ServiceName.MIN_MAX_FILTER,
            version="0.0.1",
            type=ServiceType.FILTER
        ),
        HPCService(
            id=str(uuid.uuid4()),
            name=ServiceName.FFT_FILTER,
            version="0.0.1",
            type=ServiceType.FILTER
        ),
    ]

    return services, 200
