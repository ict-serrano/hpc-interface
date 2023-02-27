import pytest

from uuid import UUID

from hpc.api.services.listing import Listing
from hpc.api.openapi.models.hpc_service import HPCService


@pytest.mark.asyncio
async def test_get_all_services_size():
    listing = Listing()
    services = await listing.get_all_services()
    assert len(services) == 4


@pytest.mark.asyncio
async def test_get_all_service_types():
    listing = Listing()
    types = await listing.get_all_service_types()
    assert len(types) == 1


@pytest.mark.asyncio
async def test_get_all_service_names():
    listing = Listing()
    names = await listing.get_all_service_names()
    assert len(names) == 4


@pytest.mark.asyncio
async def test_get_all_services_values():
    listing = Listing()
    for service in await listing.get_all_services():
        assert isinstance(service, HPCService)
        assert service.id != None
        assert UUID(service.id, version=4)
        assert service.version != None
        assert service.name in await listing.get_all_service_names()
        assert service.type in await listing.get_all_service_types()
