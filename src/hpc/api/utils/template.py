from jinja2 import Environment, PackageLoader, select_autoescape

from hpc.api.services.listing import Listing

from hpc.api.openapi.models.job_request import JobRequest
from hpc.api.openapi.models.service_name import ServiceName
from hpc.api.openapi.models.job_request_params import *


def generate_params(request: JobRequest) -> JobRequestParams:
    params = request.params
    params.icase = resolve_icase(request)
    params.filter = resolve_filters(request)
    params.kalman = resolve_kalman_config(request)
    params.fft = {}
    params.min_max = {}
    params.savitzky_golay = {}
    params.kmean = resolve_kmean_request(request)
    params.knn = resolve_knn_request(request)

    if not all(
        [
            params.read_input_data,
            params.input_data_double,
            params.input_data_float,
            params.inference_knn_path
        ]
    ):
        raise ValueError("One of the data paths is empty")

    return params


def resolve_icase(request: JobRequest) -> JobRequestParamsFilter:
    listing = Listing()
    filter_services = set(listing.get_filter_services())
    kmean_services = {ServiceName.KMEAN}
    knn_services = {ServiceName.KNN}
    req_services = set(request.services)
    if req_services.issubset(filter_services):
        return 1
    if req_services.issubset(kmean_services):
        return 2
    if req_services.issubset(knn_services):
        return 3
    raise ValueError("Cannot mix filter services with other services")


def resolve_filters(request: JobRequest) -> JobRequestParamsFilter:
    enable_kalman = 1 if ServiceName.KALMAN in request.services else 0
    enable_fft = 1 if ServiceName.FFT in request.services else 0
    enable_min_max = 1 if ServiceName.MIN_MAX in request.services else 0
    enable_savitzky_golay = 1 if ServiceName.SAVITZKY_GOLAY in request.services else 0
    return JobRequestParamsFilter(
        kalman=enable_kalman,
        fft=enable_fft,
        min_max=enable_min_max,
        savitzky_golay=enable_savitzky_golay,
    )


def resolve_kalman_config(request: JobRequest) -> JobRequestParamsKalman:
    r = request.params.kalman.r if request.params.kalman is not None else 200
    return JobRequestParamsKalman(r=r)


def resolve_kmean_request(request: JobRequest) -> JobRequestParamsKmean:
    cluster_number = request.params.kmean.cluster_number if request.params.kmean is not None else 2
    epsilon_criteria = request.params.kmean.epsilon_criteria if request.params.kmean is not None else 0.00001  # noqa
    return JobRequestParamsKmean(
        cluster_number=cluster_number,
        epsilon_criteria=epsilon_criteria)


def resolve_knn_request(request: JobRequest) -> JobRequestParamsKnn:
    cluster_number = request.params.knn.cluster_number if request.params.knn is not None else 2
    k_nearest_neighbor = request.params.knn.k_nearest_neighbor if request.params.knn is not None else 7  # noqa
    return JobRequestParamsKnn(
        cluster_number=cluster_number,
        k_nearest_neighbor=k_nearest_neighbor)


def render(request: JobRequest) -> str:
    env = Environment(
        loader=PackageLoader("hpc"),
        autoescape=select_autoescape()
    )
    template = env.get_template("exe.sh.j2")
    return template.render(params=generate_params(request))
