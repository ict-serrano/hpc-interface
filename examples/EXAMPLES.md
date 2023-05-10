# Docs on examples and usage of HPC Gateway

A usual workflow consist of the following steps:

1. Data upload from a source into SERRANO Secure Storage;
1. Data movement from SERRANO Secure Storage to an HPC infrastructure;
1. Execution of kernels on the data, producing resulting data;
1. Resulting data movement from the HPC infrastructure to SERRANO Secure Storage.

The following is the brief explanation with code samples of how to execute this workflow. Please refer to the [complete example of IDEKO use case](end_to_end_ideko.py). In this example, FFT filter on the acceleration data is performed.

## Data upload from a source into SERRANO Secure Storage

A user (or client) should have an access and valid credentials (access and secret keys) to SERRANO Secure Storage (S3-based), which is located on this endpoint: https://on-premise-storage-gateway.services.cloud.ict-serrano.eu/s3.

One can install and use boto3 python client in order to upload source data into the Storage. But before that one should create a bucket. A complete example of this step is provided below:

```python
import boto3
from botocore.client import Config
from pathlib import Path

client = boto3.client(
    "s3",
    endpoint_url="https://on-premise-storage-gateway.services.cloud.ict-serrano.eu/s3",
    region_name="local",
    config=Config(signature_version='s3v4'),
    aws_access_key_id="<ACCESS_KEY>",
    aws_secret_access_key="<SECRET_KEY>"
)

client.create_bucket(
    Bucket="test-bucket",
    CreateBucketConfiguration={"LocationConstraint": "local"})

DATA = Path(...path to your source data...) # pathlib Path

with DATA.open("rb") as src:
    s3.put_object(Body=src, Bucket="test-bucket", Key="my-data.csv")
```

## Data movement from SERRANO Secure Storage to an HPC infrastructure

This step can be performed using the `/s3_data` HPC Gateway REST API call (full endpoint path: https://hpc-interface.services.cloud.ict-serrano.eu/s3_data). One can use any web client to perform that. In this snippet, `aiohttp` python client is used, but it can be adapted to any other sync python clients, such as `requests`, or CLI tools, such as curl.

`/s3_data` call is non-blocking and returns `id` of the file transfer that can be monitored on `/s3_data/{id}` endpoint. This endpoint in turn returns the status of the transfer (`transferring`, `completed` or `failure`). A respective action can be taken, depending on the transfer status, e.g. stop execution of client jobs or log the error, when file transfer was completed with `failure` status. It is up to the client what to do next.

`dst` relative path is where the object (source data) will be stored on the HPC infrastructure. For consistency of directories structure for HPC services, the `dst` should within `serrano/data/Init_Data` directory. 

```python
url = "https://hpc-interface.services.cloud.ict-serrano.eu/s3_data"
data = {
    "endpoint": "https://on-premise-storage-gateway.services.cloud.ict-serrano.eu/s3",
    "bucket": "test-bucket",
    "object": "my-data.csv",
    "region": "local",
    "access_key": "<ACCESS_KEY>",
    "secret_key": "<SECRET_KEY>",
    "dst": "serrano/data/Init_Data/raw_data_input_fft/from_s3_my_data.csv",
    "infrastructure": "excess_slurm"
}
async with aiohttp.ClientSession() as session:
    async with session.post(url, json=data) as res:
        status = await res.json()
    while True:
        ft_url = infra.get_url(f"/s3_data/{status.get("id")}")
        async with session.get(ft_url) as res:
            ft_status = await res.json()
            if ft_status.get("status") == "transferring":
                await asyncio.sleep(1)
                continue
            else:
                break
```

## Execution of kernels on the data

In order to execute the kernel, one should send request to `/job` endpoint of HPC Gateway. In this request, one specifies kernels to execute, HPC infrastructure and job parameters. These parameters will be described below. In the similar way as file transfers, the `/job` call is non-blocking, returns `id` and can be monitored in `/job/{id}`.

As a response, the call returns job statuses, which are `queued`, `running` and `completed`. `Queued` means that the job is submitted and is awaiting execution: oftentimes, an HPC job does not start due to high occupancy of the HPC cluster. `Running` and `completed` statuses represent the job being run and completed successfully or with failure. As a future work, we will address job failures.

In the simplest example (running an FFT filter), the request will look like the one below. One must specify `params.read_input_data` path, which points to the data to be processed by the kernels. Due to specifics of implementation of the kernels manager, this path does not require `serrano/data` prefix, as done in the `/s3_data` endpoint, therefore be careful when specifying this path.

```python
url = "https://hpc-interface.services.cloud.ict-serrano.eu/job"
data = {
    "services": ["fft"],
    "infrastructure": "excess_slurm",
    "params": {
        "read_input_data": "/Init_Data/raw_data_input_fft/from_s3_my_data.csv",
    }
}
async with aiohttp.ClientSession() as session:
    status = {}
    async with session.post(url, json=data) as res:
        status = await res.json()
    while True:
        url = infra.get_url(f"/job/{status.get("id")}")
        async with session.get(url) as res:
            job_status = await res.json()
            if job_status.get("status") != "completed":
                await asyncio.sleep(1)
                continue
            else:
                break
```

### Kernels

There are three classes of kernels and they should not be mixed: signal processing (`kalman`, `fft`, `min_max`, `savitzky_golay`, `black_scholes`, `wavelet`), classification (`knn`) and inference (`kmean`). Therefore, one must not specify incompatible kernels in `/job` request, such as:
- `"services": ["fft", "knn"]`
- `"services": ["fft", "kmean"]`
- `"services": ["kmean", "knn"]`

### Job parameters

There are multiple job parameters (`params`), however, the only required parameter is `read_input_data`, which is a path to the input data. The default values of other parameters are sufficient for execution of an HPC job. One can refer to the [OpenAPI specification](../openapi-spec.yaml) for the list of available parameters under `components.schemas.JobRequestParams`.


## Resulting data movement from the HPC infrastructure to SERRANO Secure Storage

Once the job is executed, the resulting data is available in CSV format. Depending on the kernel executed, a filename of resulting data varies. By default, a directory that contains the data is: `serrano/data/Output_Data/CSVFormate/`. A filename for each kernel is

| Filter            | Filename                  |
| -------------     | ---------------------     |
| Kalman            | Kalman_Filter_output.csv  |
| FFT               | FFT_Filter_output.csv     |
| Savitzky Golay    | SavitzkeyGolay_output.csv |
| Other kernels     | TBD                       |


In the similar way, the resulting data can be transferred back to the Secure Storage via `/s3_result` endpoint and this transfer can be monitored via `/s3_result/{id}`:

```python
url = "https://hpc-interface.services.cloud.ict-serrano.eu/s3_result"
data = {
    "endpoint": "https://on-premise-storage-gateway.services.cloud.ict-serrano.eu/s3",
    "bucket": "test-bucket",
    "object": "my-resulting-fft-data.csv",
    "region": "local",
    "access_key": "<ACCESS_KEY>",
    "secret_key": "<SECRET_KEY>",
    "src": "serrano/data/Output_Data/CSVFormate/FFT_Filter_output.csv",
    "infrastructure": "excess_slurm"
}
async with aiohttp.ClientSession() as session:
    async with session.post(url, json=data) as res:
        status = await res.json()
    while True:
        ft_url = infra.get_url(f"/s3_result/{status.get("id")}")
        async with session.get(ft_url) as res:
            ft_status = await res.json()
            if ft_status.get("status") == "transferring":
                await asyncio.sleep(1)
                continue
            else:
                break
```

From the Secure Storage, the data can be downloaded with any S3 client, e.g. boto3.