from hpc.api.openapi.models.hpc_service import HPCService
from hpc.api.openapi.models.service_name import ServiceName
from hpc.api.openapi.models.service_type import ServiceType

class Listing():
    def get_all_services(self):
        return [
            HPCService(
                id="75f54ad7-caad-4c70-9227-f0395f30dc5d",
                type=ServiceType.FILTER,
                name=ServiceName.KALMAN_FILTER,
                version="0.0.1",
            ),
            HPCService(
                id="5cb99ee3-36cf-4015-872f-f6227a429202",
                type=ServiceType.FILTER,
                name=ServiceName.MIN_MAX_FILTER,
                version="0.0.1",
            ),
            HPCService(
                id="6b0489a9-6e64-4f6c-b4e8-b39f71b18a76",
                type=ServiceType.FILTER,
                name=ServiceName.FFT_FILTER,
                version="0.0.1",
            ),
            HPCService(
                id="3165580e-5f5a-4c1b-94fc-05da08af725d",
                type=ServiceType.FILTER,
                name=ServiceName.TEST_FILTER,
                version="0.0.1",
            ),
        ]

    def get_all_service_types(self):
        return [
            ServiceType.FILTER,
        ]

    def get_all_service_names(self):
        return [
            ServiceName.KALMAN_FILTER,
            ServiceName.MIN_MAX_FILTER,
            ServiceName.FFT_FILTER,
            ServiceName.TEST_FILTER,
        ]