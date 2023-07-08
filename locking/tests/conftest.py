
def pytest_collection_modifyitems(session, config, items):
    def _sortkey(item):
        return (item.cls.__name__, item.location)

    items_copy = [item for item in items if item.cls.__name__ != "LockTClass"]
    items_copy.sort(key=_sortkey)
    items[:] = items_copy
