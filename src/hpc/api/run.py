import connexion
import os

from hpc.api.openapi import encoder
from hpc.api.log import get_logger


logger = get_logger(__name__)

def get_app():
    app = connexion.App(
        __name__,
        specification_dir="./openapi/openapi/",
        server="flask",
        options=dict(
            serve_spec=True,
            swagger_ui=True)
        )

    app.app.json_encoder = encoder.JSONEncoder
    app.add_api(
        "openapi.yaml",
        arguments={"title": "HPC Gateway Interface"},
        pythonic_params=True
        )

    return app

if __name__ == "__main__":
    get_app().run(port=8080, debug=True)
