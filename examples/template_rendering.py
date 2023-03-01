import asyncio

import hpc.api.utils.template as template

from hpc.api.openapi.models.service_name import ServiceName
from hpc.api.openapi.models.job_request import JobRequest
from hpc.api.openapi.models.service_name import ServiceName
from hpc.api.openapi.models.job_request_params import *


async def render_fft_templates():
    request = JobRequest(
        services=[ServiceName.FFT],
        infrastructure="some_infra",
        params=JobRequestParams(
            read_input_data="/Init_Data/raw_data_input_fft/acceleration_cycle_260.csv",
            input_data_double="/Input_Data/Double_Data_Type/signalFilter",
            input_data_float="/Input_Data/Float_Data_Type/signalFilter",
            inference_knn_path="/Init_Data/inference_data_position/",
        ),
    )
    rendered_template = template.render(request)
    batch_cmd = "sbatch"
    cmd = f"{batch_cmd} <<\EOF\n{rendered_template}\nEOF"
    print(cmd)


async def main():
    await render_fft_templates()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
