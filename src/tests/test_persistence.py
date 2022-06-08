import pytest

import hpc.api.utils.persistence as persistence

def test_entry_creation():
    directory = "/a/b/c"
    data = {
        "a": 1,
        "b": 2,
        "c": 3
    }
    persistence.save(directory, data)
    assert persistence.get(directory) == data

def test_non_existent_entry():
    with pytest.raises(KeyError):
        persistence.get("non-existent")