import aiohttp
import asyncio
from pathlib import Path

import infrastructure as infra

import hpc.api.utils.s3 as s3
from hpc.api.openapi.models.file_transfer_status_code import FileTransferStatusCode
from hpc.api.openapi.models.service_name import ServiceName
from hpc.api.openapi.models.job_status_code import JobStatusCode


DATA = Path(__file__).resolve().parent / "data" / "acceleration_cycle_26.csv"
DST = f"serrano/data/Init_Data/raw_data_input_fft/from_s3_{DATA.name}"
READ_INPUT_DATA = f"/Init_Data/raw_data_input_fft/from_s3_{DATA.name}"
RESULT = f"serrano/data/Output_Data/CSVFormate/FFT_Filter_output.csv"


def s3_client(s3_config):
    endpoint = s3_config.get("endpoint")
    region = s3_config.get("region")
    access_key = s3_config.get("access_key")
    secret_key = s3_config.get("secret_key")
    return s3.get_client(endpoint, region, access_key, secret_key)


def bucket_absent(bucket, list_of_buckets):
    for b in list_of_buckets:
        if b.get("Name") == bucket:
            return False
    return True


async def prepare_s3():
    config = infra.get_s3()[0]
    client = s3_client(config)
    bucket = config.get("bucket")
    storage_policy = config.get("region")
    bucket_config = {"LocationConstraint": storage_policy}
    # res = await s3.delete_object(client, bucket, DATA.name)
    # res = await s3.delete_object(client, bucket, f"result_{DATA.name}")
    res = await s3.list_buckets(client)
    if bucket_absent(bucket, res.get("Buckets", [])):
        print(f"Creating bucket - {bucket}")
        res = await s3.create_bucket(client, bucket, bucket_config)
    else:
        print(f"Bucket {bucket} already exists")
    print(f"Uploading file - {DATA}")
    res = await s3.upload_file(client, DATA, bucket, DATA.name)


async def s3_transfer_to_hpc():
    url = infra.get_url("/s3_data")
    hpc = infra.get_hpc()[1]
    s3 = infra.get_s3()[0]
    data = {
        "endpoint": s3.get("endpoint"),
        "bucket": s3.get("bucket"),
        "object": DATA.name,
        "region": s3.get("region"),
        "access_key": s3.get("access_key"),
        "secret_key": s3.get("secret_key"),
        "dst": DST,
        "infrastructure": hpc.get("name")
    }
    async with aiohttp.ClientSession() as session:
        print(f"Transferring file - {DATA}")
        async with session.post(url, json=data) as res:
            status = await res.json()
            print(status)
        await await_ft_response(session, status.get("id"))


async def await_ft_response(session, ft_id):
    while True:
        ft_url = infra.get_url(f"/s3_data/{ft_id}")
        async with session.get(ft_url) as res:
            ft_status = await res.json()
            print(f"Still transferring - {ft_status}")
            if ft_status.get("status") == FileTransferStatusCode.TRANSFERRING:
                await asyncio.sleep(1)
                continue
            else:
                break


async def submit_slurm_job_fft():
    url = infra.get_url("/job")
    slurm_hpc = infra.get_hpc()[1]
    data = {
        "services": [ServiceName.FFT],
        "infrastructure": slurm_hpc.get("name"),
        "params": {
            "read_input_data": READ_INPUT_DATA,
        },
        "watch_period": 1.0
    }
    async with aiohttp.ClientSession() as session:
        status = {}
        print(f"Submitting a slurm job: {data}")
        async with session.post(url, json=data) as res:
            status = await res.json()
            print(status)
        await await_job_response(session, status.get("id"))


async def await_job_response(session, job_id):
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


async def hpc_transfer_to_s3():
    url = infra.get_url("/s3_result")
    hpc = infra.get_hpc()[1]
    s3 = infra.get_s3()[0]
    data = {
        "endpoint": s3.get("endpoint"),
        "bucket": s3.get("bucket"),
        "object": f"result_{DATA.name}",
        "region": s3.get("region"),
        "access_key": s3.get("access_key"),
        "secret_key": s3.get("secret_key"),
        "src": RESULT,
        "infrastructure": hpc.get("name")
    }
    async with aiohttp.ClientSession() as session:
        print(f"Transferring result - {RESULT}")
        async with session.post(url, json=data) as res:
            status = await res.json()
            print(status)
        await await_rt_response(session, status.get("id"))


async def await_rt_response(session, ft_id):
    while True:
        ft_url = infra.get_url(f"/s3_result/{ft_id}")
        async with session.get(ft_url) as res:
            ft_status = await res.json()
            print(f"Still transferring - {ft_status}")
            if ft_status.get("status") == FileTransferStatusCode.TRANSFERRING:
                await asyncio.sleep(1)
                continue
            else:
                break


async def check_s3_result():
    config = infra.get_s3()[0]
    client = s3_client(config)
    bucket = config.get("bucket")
    obj = f"result_{DATA.name}"
    res = client.list_objects(Bucket=bucket)
    obj = [o for o in res["Contents"] if o["Key"] == obj][0]
    print(obj)


async def main():
    await infra.create_infrastructure()
    await prepare_s3()
    await s3_transfer_to_hpc()
    await submit_slurm_job_fft()
    await hpc_transfer_to_s3()
    await check_s3_result()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
