from uuid import UUID

from hpc.api.services.listing import Listing
from hpc.api.openapi.models.hpc_service import HPCService

def test_get_all_services_size():
    listing = Listing()
    services = listing.get_all_services()
    assert len(services) == 4

def test_get_all_service_types():
    listing = Listing()
    types = listing.get_all_service_types()
    assert len(types) == 1

def test_get_all_service_names():
    listing = Listing()
    names = listing.get_all_service_names()
    assert len(names) == 4

def test_get_all_services_values():
    listing = Listing()
    for service in listing.get_all_services():
        assert isinstance(service, HPCService)
        assert service.id != None
        assert UUID(service.id, version=4)
        assert service.version != None
        assert service.name in listing.get_all_service_names()
        assert service.type in listing.get_all_service_types()