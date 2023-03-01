import aiohttp
import asyncio

import infrastructure as infra

from hpc.api.openapi.models.service_name import ServiceName
from hpc.api.openapi.models.job_status_code import JobStatusCode


async def submit_slurm_job_fft():
    url = infra.get_url("/job")
    slurm_hpc = infra.get_hpc()[1]
    data = {
        "services": [ServiceName.FFT],
        "infrastructure": slurm_hpc.get("name"),
        "params": {
            "read_input_data": "/Init_Data/raw_data_input_fft/acceleration_cycle_260.csv",
            "input_data_double": "/Input_Data/Double_Data_Type/signalFilter",
            "input_data_float": "/Input_Data/Float_Data_Type/signalFilter",
            "inference_knn_path": "/Init_Data/inference_data_position/",
        },
        "watch_period": 1.0
    }
    async with aiohttp.ClientSession() as session:
        status = {}
        print(f"Submitting a slurm job: {data}")
        async with session.post(url, json=data) as res:
            status = await res.json()
            print(status)
        await await_response(session, status.get("id"))


async def await_response(session, job_id):
    while True:
        url = infra.get_url(f"/job/{job_id}")
        async with session.get(url) as res:
            job_status = await res.json()
            print(f"Still transferring - {job_status}")
            if job_status.get("status") != JobStatusCode.COMPLETED:
                await asyncio.sleep(1)
                continue
            else:
                break


async def main():
    await infra.create_infrastructure()
    await submit_slurm_job_fft()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
