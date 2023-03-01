# HPC Interface

This is an HPC interface used by SERRANO orchestrator to interact with an HPC cluster. To run, use the following commands:

```bash
# OpenAPI generator requires java runtime
sudo apt install default-jre

# Generate the OpenAPI models 
./generate.sh

# Create a virtual environment 
python3 -m venv .venv
source .venv/bin/activate

# Install the dependencies
pip install -r requirements.txt

cd src/

# Running the service
python3 -m hpc.api.run
```

The examples of usage can be found in the Swagger UI `/ui` path.

## Unit tests

Before running tests, please provide a fixture (fixture.infrastructure.yaml) with the list of infrastructures and put in `src/tests`. The format for the fixture is the following:
```yaml
- name: cluster_1
  host: some.cluster.com
  username: user_a
  hostname: some.cluster
  scheduler: slurm
  ssh_key:
    type: ssh-ed25519
    path: /path/to/ssh/key
    password: private-key-password
```

To run tests:

```bash
pytest src/tests
```

## Examples

First of all, install locally hpc-gateway, as the examples are using modules of hpc-gateway:

```bash
pip install -e .
```

In order to toggle local and remote execution of examples use `HPC_GATEWAY_REMOTE_TEST` environment variable.

Before running examples, please provide a fixture (fixture.infrastructure.yaml) with the list of infrastructures and put in `examples`. The format for the fixture is the following:
```yaml
hpc:
  - name: cluster_1
    host: some.cluster.com
    username: user_a
    hostname: some.cluster
    scheduler: slurm
    ssh_key:
      type: ssh-ed25519
      path: /path/to/ssh/key
      password: private-key-password
s3:
  - endpoint: s3-endpoint
    bucket: some-bucket
    region: local
    access_key: your_access_key
    secret_key: your_secret_key
    small_file: "small-file.txt"
    large_file: "large-file.txt"
```

To run, select individual example, e.g.:

```bash
python examples/job_submission.py
```

## Data management

One can upload remote data into the target cluster via `/data` and `/s3_data` API call of the HPC interface.

### Performance and storage considerations

The HPC interface will firstly copy the source file into its own filesystem and then upload it into the filesystem of HPC cluster via SFTP. The reason for this approach is that it is not often possible to make HTTP and S3 calls from an HPC infrastructure due to strict firewall rules, and only a certain endpoints are open, such as SSH and GridFTP. Therefore, one should consider the performance implications of a copy of the source file, e.g. transfer time from source to HPC interface and from the interface to HPC infrastructure. It should be noted that the HPC interface itself may have a limited storage capacity, therefore one should consult the deployer of the HPC interface on the maximum possible size of source file to be transferred. 