import pytest
import hpc.api.utils.template as template

from hpc.api.openapi.models.job_request import JobRequest
from hpc.api.openapi.models.service_name import ServiceName
from hpc.api.openapi.models.job_request_params import *


def test_non_existent_filter():
    with pytest.raises(ValueError):
        template.generate_params(
            JobRequest(
                services=["non_existent"],
                infrastructure="some_infra",
                params=JobRequestParams(
                    read_input_data="abc"
                )
            ))


def test_params_filters_generated_correctly_from_request():
    request = JobRequest(
        services=[
            ServiceName.KALMAN, ServiceName.FFT, ServiceName.BLACK_SCHOLES,
            ServiceName.WAVELET, ServiceName.SAVITZKY_GOLAY],
        infrastructure="some_infra",
        params=JobRequestParams(
            read_input_data="abc",
            input_data_double="abc",
            input_data_float="abc",
            inference_knn_path="abc",
        )
    )
    params = template.generate_params(request)
    assert params.icase == 1
    assert params.filter.kalman == 1
    assert params.filter.fft == 1
    assert params.filter.min_max == 0
    assert params.filter.black_scholes == 1
    assert params.filter.wavelet == 1
    assert params.filter.savitzky_golay == 1
    assert params.kalman.r == 200


def test_params_kmean_generated_correctly_from_request():
    request = JobRequest(
        services=[ServiceName.KMEAN],
        infrastructure="some_infra",
        params=JobRequestParams(
            kmean=JobRequestParamsKmean(
                epsilon_criteria=0.1,
            ),
            read_input_data="abc",
            input_data_double="abc",
            input_data_float="abc",
            inference_knn_path="abc",
        )
    )
    params = template.generate_params(request)
    assert params.icase == 2
    assert params.filter.kalman == 0
    assert params.filter.fft == 0
    assert params.filter.min_max == 0
    assert params.filter.savitzky_golay == 0
    assert params.kmean.cluster_number == 2
    assert params.kmean.epsilon_criteria == 0.1


def test_params_knn_generated_correctly_from_request():
    request = JobRequest(
        services=[ServiceName.KNN],
        infrastructure="some_infra",
        params=JobRequestParams(
            read_input_data="abc",
            input_data_double="abc",
            input_data_float="abc",
            inference_knn_path="abc",
        )
    )
    params = template.generate_params(request)
    assert params.icase == 3
    assert params.filter.kalman == 0
    assert params.filter.fft == 0
    assert params.filter.min_max == 0
    assert params.filter.savitzky_golay == 0
    assert params.knn.cluster_number == 2
    assert params.knn.k_nearest_neighbor == 7


def test_params_mixed_filters_failure():
    with pytest.raises(ValueError):
        template.generate_params(
            JobRequest(
                services=[ServiceName.KALMAN, ServiceName.KMEAN],
                infrastructure="some_infra",
                params=JobRequestParams(
                    read_input_data="abc",
                    input_data_double="abc",
                    input_data_float="abc",
                    inference_knn_path="abc",
                )
            ))
    with pytest.raises(ValueError):
        template.generate_params(
            JobRequest(
                services=[ServiceName.KALMAN, ServiceName.KNN],
                infrastructure="some_infra",
                params=JobRequestParams(
                    read_input_data="abc",
                    input_data_double="abc",
                    input_data_float="abc",
                    inference_knn_path="abc",
                )
            ))
    with pytest.raises(ValueError):
        template.generate_params(
            JobRequest(
                services=[ServiceName.KMEAN, ServiceName.KNN],
                infrastructure="some_infra",
                params=JobRequestParams(
                    read_input_data="abc",
                    input_data_double="abc",
                    input_data_float="abc",
                    inference_knn_path="abc",
                )
            ))


def test_default_execution_params():
    request = JobRequest(
        services=[ServiceName.KNN],
        infrastructure="some_infra",
        params=JobRequestParams(
            read_input_data="abc",
            input_data_double="abc",
            input_data_float="abc",
            inference_knn_path="abc",
        )
    )
    params = template.generate_params(request)
    assert params.benchmark_state == 0
    assert params.num_mpi_procs == 4
    assert params.num_thread == 1
    assert params.perforation_stride == 1
    assert params.precision_scenario == 1
    assert params.num_numa == 8
    assert params.num_core_numa == 16
    assert params.root_dir == "${HOME}/serrano"
    assert params.workspace == "/data"
    assert params.profiling_workspace == "/profile"
    assert params.exe == "build/SERRANO"

    request = JobRequest(
        services=[ServiceName.KNN],
        infrastructure="some_infra",
        params=JobRequestParams(
            benchmark_state=1,
            read_input_data="abc",
            input_data_double="abc",
            input_data_float="abc",
            inference_knn_path="abc",
        )
    )
    params = template.generate_params(request)
    assert params.benchmark_state == 1


def test_data_path_params():
    with pytest.raises(ValueError):
        template.generate_params(
            JobRequest(
                services=[ServiceName.KMEAN],
                infrastructure="some_infra",
                params=JobRequestParams(
                    input_data_double="abc",
                    input_data_float="abc",
                    inference_knn_path="abc",
                )
            ))
    with pytest.raises(ValueError):
        template.generate_params(
            JobRequest(
                services=[ServiceName.KMEAN],
                infrastructure="some_infra",
                params=JobRequestParams(
                    read_input_data="",
                    input_data_double="abc",
                    input_data_float="abc",
                    inference_knn_path="abc",
                )
            ))
    with pytest.raises(ValueError):
        template.generate_params(
            JobRequest(
                services=[ServiceName.KMEAN],
                infrastructure="some_infra",
                params=JobRequestParams(
                    read_input_data="abc",
                    input_data_double="",
                    input_data_float="abc",
                    inference_knn_path="abc",
                )
            ))
    with pytest.raises(ValueError):
        template.generate_params(
            JobRequest(
                services=[ServiceName.KMEAN],
                infrastructure="some_infra",
                params=JobRequestParams(
                    read_input_data="abc",
                    input_data_double="abc",
                    input_data_float="",
                    inference_knn_path="abc",
                )
            ))
    with pytest.raises(ValueError):
        template.generate_params(
            JobRequest(
                services=[ServiceName.KMEAN],
                infrastructure="some_infra",
                params=JobRequestParams(
                    read_input_data="abc",
                    input_data_double="abc",
                    input_data_float="abc",
                    inference_knn_path="",
                )
            ))


def test_hpc_service_params_included():
    request = JobRequest(
        services=[ServiceName.KNN],
        infrastructure="some_infra",
        params=JobRequestParams(
            benchmark_state=1,
            read_input_data="abc",
            input_data_double="abc",
            input_data_float="abc",
            inference_knn_path="abc",
        )
    )
    rendered_template = template.render(request)
    assert "BenchmarkState=1" in rendered_template


def test_csv_output_command_rendering_depending_on_csv_output_flag():
    request = JobRequest(
        services=[ServiceName.KNN],
        infrastructure="some_infra",
        params=JobRequestParams(
            benchmark_state=1,
            read_input_data="abc",
            input_data_double="abc",
            input_data_float="abc",
            inference_knn_path="abc",
        )
    )
    rendered_template = template.render(request)
    assert "# generate csv output data: icase=0" in rendered_template
    request = JobRequest(
        services=[ServiceName.KNN],
        infrastructure="some_infra",
        params=JobRequestParams(
            benchmark_state=1,
            csv_output=0,
            read_input_data="abc",
            input_data_double="abc",
            input_data_float="abc",
            inference_knn_path="abc",
        )
    )
    rendered_template = template.render(request)
    assert "# generate csv output data: icase=0" not in rendered_template
