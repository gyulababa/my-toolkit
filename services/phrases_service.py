# services/phrases_service.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .domain import BaseDomainService
from .tags_service import TagsService
from helpers.validation import ValidationError

PhrasesDoc = object  # placeholder for your typed phrases doc


@dataclass
class PhrasesService(BaseDomainService[PhrasesDoc]):
    """
    Domain: 'phrases'

    Depends on TagsService for tag validation (composition stays app-level).
    """
    tags: TagsService | None = None
    scope: str = "phrases"

    def validate_current(self):
        # base validation (schema)
        cat = super().validate_current()

        # cross validation: tags (optional)
        if self.tags and self.current:
            for item in self.current.raw.get("items", []):
                tag_list = item.get("tags", []) or []
                if not isinstance(tag_list, list):
                    raise ValidationError("phrases.items[].tags must be a list")
                self.tags.validate_tags([str(t) for t in tag_list], scope=self.scope)

        return cat

    def add_phrase(self, text: str, tags: Optional[list[str]] = None) -> None:
        if self.current is None:
            raise ValidationError("phrases: not loaded")
        item = {"id": self._new_id(), "text": text, "tags": tags or []}
        items = self.current.raw.setdefault("items", [])
        idx = len(items)
        self.history.push_set(path=["items", idx], old=None, new=item)
        items.append(item)

    def _new_id(self) -> str:
        # App-specific id policy (could be universal later if it recurs)
        if self.current is None:
            return "p0001"
        n = len(self.current.raw.get("items", [])) + 1
        return f"p{n:04d}"
