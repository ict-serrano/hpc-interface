import os
import yaml
import aiohttp
import asyncio

LOCAL_URL = "http://localhost:8080"
REMOTE_URL = "https://hpc-interface.services.cloud.ict-serrano.eu"


def get_infrastructures():
    default_fixture = "{}/{}".format(os.path.dirname(__file__),
                                     "fixture.infrastructure.yaml")
    fixture = os.getenv(
        "HPC_GATEWAY_TEST_INFRASTRUCTURE_FIXTURE", default_fixture)
    with open(fixture, 'r') as stream:
        return yaml.safe_load(stream)


def get_hpc():
    return get_infrastructures().get("hpc", [])


def get_s3():
    return get_infrastructures().get("s3", [])


def get_url(path):
    remote = os.getenv("HPC_GATEWAY_REMOTE_TEST", False)
    if remote:
        return f"{REMOTE_URL}{path}"
    else:
        return f"{LOCAL_URL}{path}"


async def create_infrastructure():
    url = get_url("/infrastructure")
    data = get_hpc()[1]
    remote = os.getenv("HPC_GATEWAY_REMOTE_TEST", False)
    if remote:
        data["ssh_key"]["path"] = "/etc/ssh/hpc-interface/ssh-key-HPC_GATEWAY_EXCESS_PRIVATE_KEY"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as res:
            print(await res.json())


async def main():
    await create_infrastructure()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
