import asyncio
from functools import partial
from pathlib import Path

import boto3
from botocore.client import Config
from boto3.s3.transfer import TransferConfig


MB = 1048576  # 1 MB in bytes


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
    """
    TODO: here we disable multipart by setting a threshold
    ideally S3 backend should support multipart
    TODO: files are double in size, therefore trying to use put_object
    """
    """
    loop = asyncio.get_event_loop()
    src = str(src_path.resolve())
    multipart_threshold = src_path.stat().st_size + MB
    upload_file_partial = partial(
        s3.upload_file,
        Filename=src,
        Bucket=bucket,
        Key=obj,
        Config=TransferConfig(multipart_threshold=multipart_threshold)
    )
    return await loop.run_in_executor(None, upload_file_partial)
    """
    loop = asyncio.get_event_loop()
    with src_path.open("rb") as src:
        put_object_partial = partial(
            s3.put_object,
            Body=src,
            Bucket=bucket,
            Key=obj,
        )
        return await loop.run_in_executor(None, put_object_partial)


async def download_file(s3, bucket, obj, dst_path: Path):
    """
    TODO: here again we disable multipart by setting a threshold
    but in this case we should determine the object size first to set the threshold
    ideally S3 backend should support multipart
    TODO: Somehow this does not work on download. Use previous version. Raises:
        boto ResponseParserError(\'Unable to parse response
        (not well-formed (invalid token): line 1, column 0),
        invalid XML received. Further retries may succeed
    TODO: use get_object version, as the download double in size
    """
    """ 
    res = await get_object_attributes(s3, bucket, obj)
    multipart_threshold = res["ObjectSize"] + MB
    loop = asyncio.get_event_loop()
    dst = str(dst_path.resolve())
    download_file_partial = partial(
        s3.download_file,
        Bucket=bucket,
        Key=obj,
        Filename=dst,
        Config=TransferConfig(multipart_threshold=multipart_threshold)
    )
    return await loop.run_in_executor(None, download_file_partial)
    """
    """
    loop = asyncio.get_event_loop()
    dst = str(dst_path.resolve())
    return await loop.run_in_executor(None, s3.download_file, bucket, obj, dst)
    """
    loop = asyncio.get_event_loop()
    with dst_path.open("wb") as dst:
        get_object_partial = partial(
            s3.get_object,
            Bucket=bucket,
            Key=obj,
        )
        res = await loop.run_in_executor(None, get_object_partial)
        for d in res["Body"]:
            dst.write(d)
        return res

async def delete_object(s3, bucket, obj):
    loop = asyncio.get_event_loop()
    delete_object_partial = partial(
        s3.delete_object,
        Bucket=bucket,
        Key=obj
    )
    return await loop.run_in_executor(None, delete_object_partial)


async def get_object_attributes(s3, bucket, obj):
    loop = asyncio.get_event_loop()
    get_object_attributes_partial = partial(
        s3.get_object_attributes,
        Bucket=bucket,
        Key=obj,
        ObjectAttributes=[
            "ETag", "Checksum", "ObjectParts", "StorageClass", "ObjectSize",
        ]
    )
    return await loop.run_in_executor(None, get_object_attributes_partial)
