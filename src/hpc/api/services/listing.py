from hpc.api.openapi.models.hpc_service import HPCService
from hpc.api.openapi.models.service_name import ServiceName


class Listing():
    async def get_all_services(self):
        return [
            HPCService(
                name=ServiceName.KALMAN
            ),
            HPCService(
                name=ServiceName.FFT,
            ),
            HPCService(
                name=ServiceName.MIN_MAX,
            ),
            HPCService(
                name=ServiceName.SAVITZKY_GOLAY,
            ),
            HPCService(
                name=ServiceName.BLACK_SCHOLES,
            ),
            HPCService(
                name=ServiceName.WAVELET,
            ),
            HPCService(
                name=ServiceName.KMEAN,
            ),
            HPCService(
                name=ServiceName.KNN,
            ),
        ]

    def get_filter_services(self):
        return [
            ServiceName.KALMAN,
            ServiceName.FFT,
            ServiceName.MIN_MAX,
            ServiceName.SAVITZKY_GOLAY,
            ServiceName.BLACK_SCHOLES,
            ServiceName.WAVELET
        ]
