from hpc.api.services.listing import Listing  # noqa: E501

def get_all_services():  # noqa: E501
    """Get all available services

     # noqa: E501


    :rtype: List[HPCService]
    """
    listing = Listing()
    return listing.get_all_services(), 200
