import asyncio
from functools import partial
from pathlib import Path

import boto3
from botocore.client import Config


def get_client(endpoint, region, access_key, secret_key):
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        region_name=region,
        config=Config(signature_version='s3v4'),
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )


async def list_buckets(s3):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, s3.list_buckets)


async def create_bucket(s3, bucket, bucket_config):
    loop = asyncio.get_event_loop()
    create_bucket_partial = partial(
        s3.create_bucket,
        Bucket=bucket,
        CreateBucketConfiguration=bucket_config
    )
    return await loop.run_in_executor(None, create_bucket_partial)


async def delete_bucket(s3, bucket):
    loop = asyncio.get_event_loop()
    delete_bucket_partial = partial(
        s3.delete_bucket,
        Bucket=bucket
    )
    return await loop.run_in_executor(None, delete_bucket_partial)


async def upload_file(s3, src_path: Path, bucket, obj):
    loop = asyncio.get_event_loop()
    src = str(src_path.resolve())
    return await loop.run_in_executor(None, s3.upload_file, src, bucket, obj)


async def download_file(s3, bucket, obj, dst_path: Path):
    loop = asyncio.get_event_loop()
    dst = str(dst_path.resolve())
    return await loop.run_in_executor(None, s3.download_file, bucket, obj, dst)


async def delete_object(s3, bucket, obj):
    loop = asyncio.get_event_loop()
    delete_bucket_partial = partial(
        s3.delete_object,
        Bucket=bucket,
        Key=obj
    )
    return await loop.run_in_executor(None, delete_bucket_partial)
