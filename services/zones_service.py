# services/zones_service.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .domain import BaseDomainService
from helpers.validation import ValidationError

ZoneDoc = object  # placeholder for your typed zones doc


@dataclass
class ZonesService(BaseDomainService[ZoneDoc]):
    """
    Domain: 'zones'
    """

    def add_zone(self, zone_raw: dict) -> None:
        if self.current is None:
            raise ValidationError("zones: not loaded")
        # Typically: append to current.raw["zones"]
        # Record in history as an operation with path tokens.
        zones = self.current.raw.setdefault("zones", [])
        idx = len(zones)
        self.history.push_set(path=["zones", idx], old=None, new=zone_raw)  # example API
        zones.append(zone_raw)

    def rename_zone(self, zone_id: str, new_name: str) -> None:
        if self.current is None:
            raise ValidationError("zones: not loaded")
        zones = self.current.raw.get("zones", [])
        for i, z in enumerate(zones):
            if z.get("id") == zone_id:
                old = z.get("name")
                self.history.push_set(path=["zones", i, "name"], old=old, new=new_name)
                z["name"] = new_name
                return
        raise ValidationError(f"zones: unknown id {zone_id!r}")
