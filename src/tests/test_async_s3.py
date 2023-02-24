import pytest
from io import BytesIO
from pathlib import Path

import aiofiles.tempfile

from botocore.response import StreamingBody
from botocore.stub import Stubber
from botocore.exceptions import ClientError
from boto3.exceptions import S3UploadFailedError

import hpc.api.utils.async_s3 as s3


bucket = "test-bucket"
obj = "test-file.txt"
text_bytes = b"Some text"

storage_policy = "local"
bucket_config = {"LocationConstraint": storage_policy}


@pytest.fixture
def client():
    endpoint = "https://some-s3-endpoint.com/s3"
    region = "some-region"
    access_key = "access-key"
    secret_key = "secret-key"
    return s3.get_client(endpoint, region, access_key, secret_key)


@pytest.fixture
def list_buckets():
    return {
        "Owner": {
            "ID": "XYZ"
        },
        "Buckets": [
            {
                "CreationDate": "2023-02-23T14:49:37.000Z",
                "Name": "bucket-a"
            },
            {
                "CreationDate": "2023-02-23T14:49:37.000Z",
                "Name": "bucket-b"
            },
        ]
    }


@pytest.fixture
def create_bucket():
    return {
        "Location": f"/{bucket}"
    }


@pytest.fixture
def put_object():
    return {
        "Expiration": "string",
        "ETag": "string",
        "ChecksumCRC32": "string",
        "ChecksumCRC32C": "string",
        "ChecksumSHA1": "string",
        "ChecksumSHA256": "string",
        "ServerSideEncryption": "AES256",
        "VersionId": "string",
        "SSECustomerAlgorithm": "string",
        "SSECustomerKeyMD5": "string",
        "SSEKMSKeyId": "string",
        "SSEKMSEncryptionContext": "string",
        "BucketKeyEnabled": True,
        "RequestCharged": "requester"
    }


@pytest.fixture
def get_object():
    return {
        "Body": StreamingBody(BytesIO(text_bytes), len(text_bytes)),
        "DeleteMarker": True,
        "AcceptRanges": "string",
        "Expiration": "string",
        "Restore": "string",
        "LastModified": "2023-02-23T14:49:37.000Z",
        "ContentLength": 123,
        "ETag": "string",
        "ChecksumCRC32": "string",
        "ChecksumCRC32C": "string",
        "ChecksumSHA1": "string",
        "ChecksumSHA256": "string",
        "MissingMeta": 123,
        "VersionId": "string",
        "CacheControl": "string",
        "ContentDisposition": "string",
        "ContentEncoding": "string",
        "ContentLanguage": "string",
        "ContentRange": "string",
        "ContentType": "string",
        "Expires": "2023-02-23T14:49:37.000Z",
        "WebsiteRedirectLocation": "string",
        "ServerSideEncryption": "AES256",
        "Metadata": {
            "string": "string"
        },
        "SSECustomerAlgorithm": "string",
        "SSECustomerKeyMD5": "string",
        "SSEKMSKeyId": "string",
        "BucketKeyEnabled": True,
        "StorageClass": "STANDARD",
        "RequestCharged": "requester",
        "ReplicationStatus": "COMPLETE",
        "PartsCount": 123,
        "TagCount": 123,
        "ObjectLockMode": "GOVERNANCE",
        "ObjectLockRetainUntilDate": "2023-02-23T14:49:37.000Z",
        "ObjectLockLegalHoldStatus": "OFF"
    }


@pytest.mark.asyncio
async def test_list_buckets(client, list_buckets):
    stubber = Stubber(client)
    stubber.add_response("list_buckets", list_buckets)
    stubber.activate()
    res = await s3.list_buckets(client)
    assert res == list_buckets


@pytest.mark.asyncio
async def test_list_buckets_failure(client):
    stubber = Stubber(client)
    stubber.add_client_error('list_buckets')
    stubber.activate()
    with pytest.raises(ClientError):
        await s3.list_buckets(client)


@pytest.mark.asyncio
async def test_create_bucket(client, create_bucket):
    stubber = Stubber(client)
    stubber.add_response("create_bucket", create_bucket)
    stubber.activate()
    res = await s3.create_bucket(client, bucket, bucket_config)
    assert res == create_bucket


@pytest.mark.asyncio
async def test_create_bucket_failure(client):
    stubber = Stubber(client)
    stubber.add_client_error('create_bucket')
    stubber.activate()
    with pytest.raises(ClientError):
        await s3.create_bucket(client, bucket, bucket_config)


@pytest.mark.asyncio
async def test_delete_bucket(client):
    stubber = Stubber(client)
    stubber.add_response("delete_bucket", {})
    stubber.activate()
    res = await s3.delete_bucket(client, bucket)
    assert res == {}


@pytest.mark.asyncio
async def test_delete_bucket_failure(client):
    stubber = Stubber(client)
    stubber.add_client_error('delete_bucket')
    stubber.activate()
    with pytest.raises(ClientError):
        await s3.delete_bucket(client, bucket)


@pytest.mark.asyncio
async def test_upload_file(client, put_object):
    stubber = Stubber(client)
    stubber.add_response("put_object", put_object)
    stubber.activate()
    async with aiofiles.tempfile.TemporaryDirectory() as d:
        path = Path(d) / obj
        path.write_bytes(text_bytes)
        res = await s3.upload_file(client, path, bucket, obj)
        assert res is None


@pytest.mark.asyncio
async def test_upload_file_failure(client):
    stubber = Stubber(client)
    stubber.add_client_error('put_object')
    stubber.activate()
    with pytest.raises(S3UploadFailedError):
        async with aiofiles.tempfile.TemporaryDirectory() as d:
            path = Path(d) / obj
            path.write_bytes(text_bytes)
            await s3.upload_file(client, path, bucket, obj)


@pytest.mark.asyncio
async def test_download_file(client, get_object):
    stubber = Stubber(client)
    stubber.add_response("head_object", {"ContentLength": 123})
    stubber.add_response("get_object", get_object)
    stubber.activate()
    async with aiofiles.tempfile.TemporaryDirectory() as d:
        dst = Path(d) / obj
        res = await s3.download_file(client, bucket, obj, dst)
        assert res is None
        dst.read_bytes() == text_bytes


@pytest.mark.asyncio
async def test_download_file_failure(client):
    stubber = Stubber(client)
    stubber.add_response("head_object", {"ContentLength": 123})
    stubber.add_client_error('get_object')
    stubber.activate()
    with pytest.raises(ClientError):
        async with aiofiles.tempfile.TemporaryDirectory() as d:
            dst = Path(d) / obj
            await s3.download_file(client, bucket, obj, dst)


@pytest.mark.asyncio
async def test_delete_object(client):
    stubber = Stubber(client)
    stubber.add_response("delete_object", {})
    stubber.activate()
    res = await s3.delete_object(client, bucket, obj)
    assert res == {}


@pytest.mark.asyncio
async def test_delete_object_failure(client):
    stubber = Stubber(client)
    stubber.add_client_error('delete_object')
    stubber.activate()
    with pytest.raises(ClientError):
        await s3.delete_object(client, bucket, obj)
