import asyncio
import connexion

from hpc.api.openapi import encoder
from hpc.api.log import get_logger


logger = get_logger(__name__)

async def get_app():
    app = connexion.AioHttpApp(
        __name__,
        specification_dir="./openapi/openapi/",
        # server="flask",
        only_one_api=True,
        options=dict(
            serve_spec=True,
            swagger_ui=True)
        )

    app.app.json_encoder = encoder.JSONEncoder
    app.add_api(
        "openapi.yaml",
        arguments={"title": "HPC Gateway Interface"},
        pythonic_params=True,
        pass_context_arg_name="request",
        strict_validation=True
        )

    return app

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(get_app())
    app.run(port=8080, debug=True)
