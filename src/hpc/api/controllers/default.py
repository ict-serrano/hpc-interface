import connexion

from hpc.api.services.listing import Listing
from hpc.api.openapi.models.job_request import JobRequest
import hpc.api.services.job as job
from hpc.api.openapi.models.infrastructure import Infrastructure
import hpc.api.services.infrastructure as infrastructure
import hpc.api.services.telemetry as telemetry
from hpc.api.log import get_logger

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
        return job.submit(job_request), 200
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
        return infrastructure.create(infrastructure_request), 200
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