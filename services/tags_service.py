# services/tags_service.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .domain import BaseDomainService
from helpers.persist import PersistedCatalogLoader
from helpers.persist import CatalogLoader

# These will come from helpers.tags.* once you implement them
# validate_tag_catalog(raw) -> TagCatalogDoc
# dump_tag_catalog(doc) -> dict
# plus Tag parsing helpers: parse_tag("ns:val") etc.

TagCatalogDoc = object  # placeholder


@dataclass
class TagsService(BaseDomainService[TagCatalogDoc]):
    """
    Domain: 'tags'

    Other services may call:
      tags_service.get_catalog()  -> validated TagCatalogDoc
      tags_service.validate_tags([...]) -> raises ValidationError if invalid
    """

    def get_catalog(self) -> TagCatalogDoc:
        cat = self.validate_current() if self.current else self.persisted.load_active_catalog(self.persist_root)
        return cat.doc  # if Catalog stores typed doc as .doc (adjust to your Catalog API)

    def validate_tags(self, tags: list[str], *, scope: str = "*") -> None:
        """
        Validate a list of tag strings against the active TagCatalog.

        - scope is an app-defined string; TagCatalog may filter namespaces by applies_to.
        """
        catalog = self.get_catalog()
        # helpers.tags.validate_tagset(tags, catalog, scope=scope)
        return
