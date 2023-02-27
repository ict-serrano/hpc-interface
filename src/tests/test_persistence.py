import pytest

import hpc.api.utils.persistence as persistence


@pytest.mark.asyncio
async def test_entry_creation():
    directory = "/a/b/c"
    data = {
        "a": 1,
        "b": 2,
        "c": 3
    }
    await persistence.save(directory, data)
    assert await persistence.get(directory) == data


@pytest.mark.asyncio
async def test_non_existent_entry():
    with pytest.raises(KeyError):
        await persistence.get("non-existent")
