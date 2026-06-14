from collections import OrderedDict

_MAX_ENTRIES = 5
_MAX_PUZZLES = 100

_store: OrderedDict[str, list] = OrderedDict()


def get(row_id: str) -> list | None:
    if row_id in _store:
        _store.move_to_end(row_id)
        return _store[row_id]
    return None


def put(row_id: str, puzzles: list) -> None:
    if len(puzzles) > _MAX_PUZZLES:
        return
    if row_id in _store:
        _store.move_to_end(row_id)
    _store[row_id] = puzzles
    while len(_store) > _MAX_ENTRIES:
        _store.popitem(last=False)


def delete(row_id: str) -> None:
    _store.pop(row_id, None)
