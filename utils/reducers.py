from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from schemas import Section


def merge_sections(current: list[Section], update: list[Section]) -> list[Section]:
    """Replace by index."""
    by_index = {s.index: s for s in current}
    for s in update:
        by_index[s.index] = s
    return sorted(by_index.values(), key=lambda s: s.index)
