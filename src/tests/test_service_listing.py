import pytest

from hpc.api.services.listing import Listing


@pytest.mark.asyncio
async def test_get_all_services_size():
    listing = Listing()
    services = await listing.get_all_services()
    assert len(services) == 8


@pytest.mark.asyncio
async def test_get_filter_services_size():
    listing = Listing()
    services = listing.get_filter_services()
    assert len(services) == 6
