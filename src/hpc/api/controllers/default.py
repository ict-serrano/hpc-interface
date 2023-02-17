import connexion
from aiohttp.web_request import Request

from hpc.api.services.listing import Listing
from hpc.api.openapi.models.job_request import JobRequest
import hpc.api.services.job as job
from hpc.api.openapi.models.infrastructure import Infrastructure
import hpc.api.services.infrastructure as infrastructure
import hpc.api.services.async_infrastructure as ainfrastructure
import hpc.api.services.telemetry as telemetry
from hpc.api.log import get_logger
from hpc.api.openapi.models.file_transfer_request import FileTransferRequest
import hpc.api.services.data_manager as data_manager
import hpc.api.services.async_data_manager as adata_manager

logger = get_logger(__name__)


def get_all_services():
    listing = Listing()
    return listing.get_all_services(), 200


def submit_new_job(body):
    logger.debug("Submitting a new job")
    logger.debug(body)

    if connexion.request.is_json:
        job_request = JobRequest.from_dict(connexion.request.get_json())
    else:
        return {"Incorrect input, expected JSON"}, 400

    try:
        return job.submit(job_request), 201
    except Exception as ex:
        logger.exception("An error occurred during submission of a new job")
        return {"message": str(ex)}, 500


def get_job_status(job_id):
    logger.debug("Retrieving job status: {}".format(job_id))
    try:
        return job.get(job_id), 200
    except KeyError as ex:
        logger.exception("Job not found: {}".format(job_id))
        return {"message": str(ex)}, 404
    except Exception as ex:
        logger.exception("An error occurred during retrieval of the job")
        return {"message": str(ex)}, 500


def create_new_infrastructure(body):
    logger.debug("Creating a new infrastructure")
    logger.debug(body)

    if connexion.request.is_json:
        infrastructure_request = Infrastructure.from_dict(connexion.request.get_json())
    else:
        return {"Incorrect input, expected JSON"}, 400

    try:
        return infrastructure.create(infrastructure_request), 201
    except Exception as ex:
        logger.exception("An error occurred during creation of a new infrastructure")
        return {"message": str(ex)}, 500


def get_infrastructure(infrastructure_name):
    logger.debug("Retrieving infrastructure: {}".format(infrastructure_name))
    try:
        return infrastructure.get(infrastructure_name), 200
    except KeyError as ex:
        logger.exception("Infrastructure not found: {}".format(infrastructure_name))
        return {"message": str(ex)}, 404
    except Exception as ex:
        logger.exception("An error occurred during retrieval of the infrastructure")
        return {"message": str(ex)}, 500


async def async_create_new_infrastructure(request: Request):
    logger.debug("Creating a new infrastructure")
    if request.content_type == "application/json":
        infrastructure_request = Infrastructure.from_dict(await request.json())
        logger.debug(infrastructure_request)
    else:
        return {"Incorrect input, expected JSON"}, 400

    try:
        res = await ainfrastructure.create(infrastructure_request)
        return res.to_dict(), 201
    except Exception as ex:
        logger.exception("An error occurred during creation of a new infrastructure")
        return {"message": str(ex)}, 500


async def async_get_infrastructure(infrastructure_name):
    logger.debug("Retrieving infrastructure: {}".format(infrastructure_name))
    try:
        res = await ainfrastructure.get(infrastructure_name)
        return res.to_dict(), 200
    except KeyError as ex:
        logger.exception("Infrastructure not found: {}".format(infrastructure_name))
        return {"message": str(ex)}, 404
    except Exception as ex:
        logger.exception("An error occurred during retrieval of the infrastructure")
        return {"message": str(ex)}, 500


def get_infrastructure_telemetry(infrastructure_name):
    logger.debug("Retrieving infrastructure telemetry: {}".format(infrastructure_name))
    try:
        return telemetry.get(infrastructure_name), 200
    except KeyError as ex:
        logger.exception("Infrastructure not found: {}".format(infrastructure_name))
        return {"message": str(ex)}, 404
    except Exception as ex:
        logger.exception("An error occurred during retrieval of the infrastructure telemetry")
        return {"message": str(ex)}, 500


def transfer_remote_file(body):
    logger.debug("Transferring a file")
    logger.debug(body)

    if connexion.request.is_json:
        ft_request = FileTransferRequest.from_dict(connexion.request.get_json())
    else:
        return {"Incorrect input, expected JSON"}, 400

    try:
        return data_manager.transfer(ft_request), 201
    except Exception as ex:
        logger.exception("An error occurred during transferring a file")
        return {"message": str(ex)}, 500


def get_file_transfer_status(file_transfer_id):
    logger.debug("Retrieving file transfer: {}".format(file_transfer_id))
    try:
        return data_manager.get(file_transfer_id), 200
    except KeyError as ex:
        logger.exception("File transfer not found: {}".format(file_transfer_id))
        return {"message": str(ex)}, 404
    except Exception as ex:
        logger.exception("An error occurred during retrieval of the file transfer")
        return {"message": str(ex)}, 500


async def async_transfer_remote_file(request: Request):
    logger.debug("Transferring a file")

    if request.content_type == "application/json":
        ft_request = FileTransferRequest.from_dict(await request.json())
        logger.debug(ft_request)
    else:
        return {"Incorrect input, expected JSON"}, 400

    try:
        res = await adata_manager.transfer(ft_request)
        return res.to_dict(), 201
    except Exception as ex:
        logger.exception("An error occurred during transferring a file")
        return {"message": str(ex)}, 500


async def async_get_file_transfer_status(file_transfer_id):
    logger.debug("Retrieving file transfer: {}".format(file_transfer_id))
    try:
        res = await adata_manager.get(file_transfer_id)
        return res.to_dict(), 200
    except KeyError as ex:
        logger.exception("File transfer not found: {}".format(file_transfer_id))
        return {"message": str(ex)}, 404
    except Exception as ex:
        logger.exception("An error occurred during retrieval of the file transfer")
        return {"message": str(ex)}, 500
