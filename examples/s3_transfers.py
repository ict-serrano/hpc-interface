import os
import aiohttp
import asyncio
import tempfile
from pathlib import Path

import infrastructure as infra

import hpc.api.utils.s3 as s3
from hpc.api.openapi.models.file_transfer_status_code import FileTransferStatusCode


def s3_client(s3_config):
    endpoint = s3_config.get("endpoint")
    region = s3_config.get("region")
    access_key = s3_config.get("access_key")
    secret_key = s3_config.get("secret_key")
    return s3.get_client(endpoint, region, access_key, secret_key)


def gen_files(file, size=1):
    MB = size*1024*1024  # size*1MB
    with open(file, 'wb') as f:
        f.write(os.urandom(MB))


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
    res = await s3.list_buckets(client)
    if bucket_absent(bucket, res.get("Buckets", [])):
        print(f"Creating bucket - {bucket}")
        res = await s3.create_bucket(client, bucket, bucket_config)
        with tempfile.TemporaryDirectory() as d:
            # small file upload
            small_file = Path(d) / config.get("small_file")
            print(f"Generating file - {small_file}")
            gen_files(small_file, 1)
            print(f"Uploading file - {small_file}")
            res = await s3.upload_file(client, small_file, bucket, config.get("small_file"))
            # large file upload
            large_file = Path(d) / config.get("large_file")
            print(f"Generating file - {large_file}")
            gen_files(large_file, 50)
            print(f"Uploading file - {large_file}")
            res = await s3.upload_file(client, large_file, bucket, config.get("large_file"))
    else:
        print(f"Bucket {bucket} already exists")


async def s3_transfer_to_hpc():
    url = infra.get_url("/s3_data")
    hpc = infra.get_hpc()[1]
    s3 = infra.get_s3()[0]
    data = {
        "endpoint": s3.get("endpoint"),
        "bucket": s3.get("bucket"),
        "object": "",
        "region": s3.get("region"),
        "access_key": s3.get("access_key"),
        "secret_key": s3.get("secret_key"),
        "dst": "",
        "infrastructure": hpc.get("name")
    }
    small_file = s3.get("small_file")
    small_file_dst = f"/tmp/{small_file}"
    large_file = s3.get("large_file")
    large_file_dst = f"/tmp/{large_file}"
    async with aiohttp.ClientSession() as session:
        # small file transfer
        data["object"] = small_file
        data["dst"] = small_file_dst
        status = {}
        print(f"Transferring small file - {small_file}")
        async with session.post(url, json=data) as res:
            status = await res.json()
            print(status)
        await await_response(session, status.get("id"))
        # large file transfer
        data["object"] = large_file
        data["dst"] = large_file_dst
        status = {}
        print(f"Transferring large file - {large_file}")
        async with session.post(url, json=data) as res:
            status = await res.json()
            print(status)
        await await_response(session, status.get("id"))


async def await_response(session, ft_id):
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


async def main():
    await infra.create_infrastructure()
    await prepare_s3()
    await s3_transfer_to_hpc()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
