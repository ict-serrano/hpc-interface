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

To run tests:

```bash
pytest src/tests
```