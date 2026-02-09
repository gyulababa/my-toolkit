# helpers/vision/overlays/filters.py

from __future__ import annotations

from typing import Iterable, List, Optional, Set

from helpers.vision.overlays.models import Annotation, LayerFilter


def match_filter(a: Annotation, f: LayerFilter) -> bool:
    if f.kinds is not None and len(f.kinds) > 0:
        if a.kind not in f.kinds:
            return False

    tags: Set[str] = set(a.tags or [])

    if f.exclude_tags_any:
        for t in f.exclude_tags_any:
            if t in tags:
                return False

    if f.require_tags_all:
        for t in f.require_tags_all:
            if t not in tags:
                return False

    if f.require_tags_any:
        ok = any(t in tags for t in f.require_tags_any)
        if not ok:
            return False

    return True


def filter_annotations(annotations: List[Annotation], f: LayerFilter) -> List[Annotation]:
    return [a for a in annotations if match_filter(a, f)]
