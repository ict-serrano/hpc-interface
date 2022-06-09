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

Before running tests, please provide a fixture (fixture.infrastructure.yaml) with the list of infrastructures and put in src/tests. The format for the fixture is the following:
```yaml
- name: cluster_1
  host: some.cluster.com
  username: user_a
  hostname: some.cluster
  ssh_key:
    type: ssh-ed25519
    path: /path/to/ssh/key
    password: private-key-password
```

To run tests:

```bash
pytest src/tests
```

The examples of usage can be found in the Swagger UI `/ui` path.