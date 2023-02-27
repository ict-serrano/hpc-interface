from aiohttp.web_request import Request

from hpc.api.services.listing import Listing
from hpc.api.openapi.models.job_request import JobRequest
import hpc.api.services.job as job
from hpc.api.openapi.models.infrastructure import Infrastructure
import hpc.api.services.infrastructure as infrastructure
import hpc.api.services.telemetry as telemetry
from hpc.api.log import get_logger
from hpc.api.openapi.models.file_transfer_request import FileTransferRequest
from hpc.api.openapi.models.s3_file_transfer_request import S3FileTransferRequest
from hpc.api.services.data_manager import DataManagerFactory

logger = get_logger(__name__)


async def get_all_services():
    listing = Listing()
    services = [s.to_dict() for s in await listing.get_all_services()]
    return services, 200


async def submit_new_job(request: Request):
    logger.debug("Submitting a new job")

    if request.content_type == "application/json":
        job_request = JobRequest.from_dict(await request.json())
        logger.debug(job_request)
    else:
        return {"Incorrect input, expected JSON"}, 400

    try:
        res = await job.submit(job_request)
        return res.to_dict(), 201
    except Exception as ex:
        logger.exception("An error occurred during submission of a new job")
        return {"message": str(ex)}, 500


async def get_job_status(job_id):
    logger.debug("Retrieving job status: {}".format(job_id))
    try:
        res = await job.get(job_id)
        return res.to_dict(), 200
    except KeyError as ex:
        logger.exception("Job not found: {}".format(job_id))
        return {"message": str(ex)}, 404
    except Exception as ex:
        logger.exception("An error occurred during retrieval of the job")
        return {"message": str(ex)}, 500


async def create_new_infrastructure(request: Request):
    logger.debug("Creating a new infrastructure")
    if request.content_type == "application/json":
        infrastructure_request = Infrastructure.from_dict(await request.json())
        logger.debug(infrastructure_request)
    else:
        return {"Incorrect input, expected JSON"}, 400

    try:
        res = await infrastructure.create(infrastructure_request)
        return res.to_dict(), 201
    except Exception as ex:
        logger.exception(
            "An error occurred during creation of a new infrastructure")
        return {"message": str(ex)}, 500


async def get_infrastructure(infrastructure_name):
    logger.debug("Retrieving infrastructure: {}".format(infrastructure_name))
    try:
        res = await infrastructure.get(infrastructure_name)
        return res.to_dict(), 200
    except KeyError as ex:
        logger.exception(
            "Infrastructure not found: {}".format(infrastructure_name))
        return {"message": str(ex)}, 404
    except Exception as ex:
        logger.exception(
            "An error occurred during retrieval of the infrastructure")
        return {"message": str(ex)}, 500


async def get_infrastructure_telemetry(infrastructure_name):
    logger.debug("Retrieving infrastructure telemetry: {}".format(
        infrastructure_name))
    try:
        res = await telemetry.get(infrastructure_name)
        return res.to_dict(), 200
    except KeyError as ex:
        logger.exception(
            "Infrastructure not found: {}".format(infrastructure_name))
        return {"message": str(ex)}, 404
    except Exception as ex:
        logger.exception(
            "An error occurred during retrieval of the infrastructure telemetry")
        return {"message": str(ex)}, 500


async def transfer_remote_file(request: Request):
    logger.debug("Transferring a file")

    if request.content_type == "application/json":
        ft_request = FileTransferRequest.from_dict(await request.json())
        logger.debug(ft_request)
    else:
        return {"Incorrect input, expected JSON"}, 400

    try:
        dm = DataManagerFactory.get_data_manager(DataManagerFactory.HTTP)
        res = await dm.transfer(ft_request)
        return res.to_dict(), 201
    except Exception as ex:
        logger.exception("An error occurred during transferring a file")
        return {"message": str(ex)}, 500


async def get_file_transfer_status(file_transfer_id):
    logger.debug("Retrieving file transfer: {}".format(file_transfer_id))
    try:
        dm = DataManagerFactory.get_data_manager(DataManagerFactory.HTTP)
        res = await dm.get(file_transfer_id)
        return res.to_dict(), 200
    except KeyError as ex:
        logger.exception(
            "File transfer not found: {}".format(file_transfer_id))
        return {"message": str(ex)}, 404
    except Exception as ex:
        logger.exception(
            "An error occurred during retrieval of the file transfer")
        return {"message": str(ex)}, 500


async def transfer_remote_s3_file(request: Request):
    logger.debug("Transferring an S3 file")

    if request.content_type == "application/json":
        ft_request = S3FileTransferRequest.from_dict(await request.json())
        logger.debug(ft_request)
    else:
        return {"Incorrect input, expected JSON"}, 400

    try:
        dm = DataManagerFactory.get_data_manager(DataManagerFactory.S3)
        res = await dm.transfer(ft_request)
        return res.to_dict(), 201
    except Exception as ex:
        logger.exception("An error occurred during transferring an S3 file")
        return {"message": str(ex)}, 500


async def get_s3_file_transfer_status(file_transfer_id):
    logger.debug("Retrieving S3 file transfer: {}".format(file_transfer_id))
    try:
        dm = DataManagerFactory.get_data_manager(DataManagerFactory.S3)
        res = await dm.get(file_transfer_id)
        return res.to_dict(), 200
    except KeyError as ex:
        logger.exception(
            "S3 file transfer not found: {}".format(file_transfer_id))
        return {"message": str(ex)}, 404
    except Exception as ex:
        logger.exception(
            "An error occurred during retrieval of the S3 file transfer")
        return {"message": str(ex)}, 500
