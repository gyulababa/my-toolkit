# helpers/catalogloader/loader.py
# Convention-based loader for app-scoped JSON templates/configs under helpers/templates/<app>/ and helpers/configs/<app>/.

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Generic, Optional, Sequence, TypeVar

from helpers.catalog import Catalog, EditableCatalog
from helpers.fs import (
    atomic_write_json,
    find_upwards,
    ls,
    read_json_strict,
    safe_join,
)
from helpers.validation import ValidationError, ensure_str

DocT = TypeVar("DocT")
ValidateFn = Callable[[Any], DocT]
DumpFn = Callable[[DocT], Dict[str, Any]]


def _repo_helpers_root() -> Path:
    """
    Resolve helpers/ root based on this file location.

    Assumes:
      helpers/catalogloader/loader.py
    """
    return Path(__file__).resolve().parents[1]


def _find_helpers_root_from_cwd() -> Optional[Path]:
    """
    Best-effort helpers root discovery from current working directory.

    Uses find_upwards to locate a directory containing a "helpers" folder.
    This is optional and only used if callers do not provide helpers_root.
    """
    cwd = Path.cwd()
    found = find_upwards(cwd, markers=["helpers"])
    if found is None:
        return None
    helpers_dir = found / "helpers"
    return helpers_dir if helpers_dir.is_dir() else None


def _safe_filename(name: str, *, what: str) -> str:
    """
    Validate a user-provided file name to prevent path traversal.

    Rules:
      - must be a non-empty string
      - must not contain path separators
      - must not be "." or ".."
    """
    s = ensure_str(name, path=what, allow_empty=False)
    if s in {".", ".."}:
        raise ValidationError(f"{what} must not be '.' or '..' (got {s!r})")
    if any(sep in s for sep in ("/", "\\", "\0")):
        raise ValidationError(f"{what} must be a filename, not a path (got {s!r})")
    return s


@dataclass
class CatalogLoader(Generic[DocT]):
    """
    CatalogLoader

    Responsibilities:
      - resolve template/config paths under:
          helpers/templates/<app_name>/ and helpers/configs/<app_name>/
      - load JSON to raw dict
      - optionally validate into Catalog
      - optionally create EditableCatalog for in-memory editing
      - save JSON back to disk (atomic write recommended)

    This is schema-pluggable via validate/dump functions.
    """
    app_name: str
    validate: ValidateFn[DocT]
    dump: DumpFn[DocT]
    schema_name: str = "catalog"
    schema_version: int = 1
    helpers_root: Optional[Path] = None

    @property
    def root(self) -> Path:
        """
        The helpers/ root directory.

        Resolution order:
          1) helpers_root (explicit)
          2) attempt to locate "helpers" folder from CWD using find_upwards
          3) repo-relative fallback based on this file location
        """
        if self.helpers_root is not None:
            return self.helpers_root.resolve()

        discovered = _find_helpers_root_from_cwd()
        if discovered is not None:
            return discovered.resolve()

        return _repo_helpers_root().resolve()

    @property
    def templates_dir(self) -> Path:
        """Directory for templates for this app."""
        return self.root / "templates" / self.app_name

    @property
    def configs_dir(self) -> Path:
        """Directory for configs for this app."""
        return self.root / "configs" / self.app_name

    # ------------------------
    # Low-level JSON IO (delegates to helpers.fs)
    # ------------------------
    def load_raw(self, path: Path) -> Dict[str, Any]:
        """
        Load JSON from disk and ensure the root is a dict.

        Raises:
          ValidationError with a clear message on:
            - IO errors
            - JSON parse errors
            - root type mismatch
        """
        try:
            return read_json_strict(path, root_types=(dict,))
        except ValidationError:
            # Preserve validation errors as-is.
            raise
        except Exception as e:
            raise ValidationError(f"Failed to load JSON from {path}") from e

    def save_raw(
        self,
        path: Path,
        raw: Dict[str, Any],
        *,
        indent: int = 2,
        sort_keys: bool = True,
        overwrite: bool = True,
    ) -> None:
        """
        Save JSON to disk atomically.

        Uses helpers.fs.atomic_write_json to ensure:
          - parents created
          - UTF-8 encoding
          - atomic replace (where supported)
          - stable formatting (indent/sort_keys)
        """
        try:
            atomic_write_json(path, raw, indent=indent, sort_keys=sort_keys, overwrite=overwrite)
        except Exception as e:
            raise ValidationError(f"Failed to save JSON to {path}") from e

    # ------------------------
    # Templates / configs conventions
    # ------------------------
    def template_path(self, name: str) -> Path:
        """
        Compute a safe template file path.

        Example:
          loader.template_path("zone.json") -> helpers/templates/<app_name>/zone.json
        """
        fname = _safe_filename(name, what="template name")
        return safe_join(self.templates_dir, fname)

    def config_path(self, name: str = "default.json") -> Path:
        """
        Compute a safe config file path.

        Example:
          loader.config_path() -> helpers/configs/<app_name>/default.json
        """
        fname = _safe_filename(name, what="config name")
        return safe_join(self.configs_dir, fname)

    def list_templates(self, *, pattern: str = "*.json") -> list[Path]:
        """
        List template files for this app.

        Returns:
          Paths (absolute, resolved) sorted by name.
        """
        items = ls(self.templates_dir, pattern=pattern, recursive=False)
        return sorted([p.resolve() for p in items], key=lambda p: p.name)

    def list_configs(self, *, pattern: str = "*.json") -> list[Path]:
        """
        List config files for this app.

        Returns:
          Paths (absolute, resolved) sorted by name.
        """
        items = ls(self.configs_dir, pattern=pattern, recursive=False)
        return sorted([p.resolve() for p in items], key=lambda p: p.name)

    # ------------------------
    # Loaders into Catalog or EditableCatalog
    # ------------------------
    def load_template_editable(self, name: str, *, history=None) -> EditableCatalog[DocT]:
        """Load template JSON into an EditableCatalog."""
        raw = self.load_raw(self.template_path(name))
        return EditableCatalog(
            raw=raw,
            schema_name=self.schema_name,
            schema_version=self.schema_version,
            history=history,
        )

    def load_config_editable(self, name: str = "default.json", *, history=None) -> EditableCatalog[DocT]:
        """Load config JSON into an EditableCatalog."""
        raw = self.load_raw(self.config_path(name))
        return EditableCatalog(
            raw=raw,
            schema_name=self.schema_name,
            schema_version=self.schema_version,
            history=history,
        )

    def load_template_catalog(self, name: str) -> Catalog[DocT]:
        """Load template JSON and validate into a Catalog."""
        raw = self.load_raw(self.template_path(name))
        return Catalog.load(raw, validate=self.validate, schema_name=self.schema_name, schema_version=self.schema_version)

    def load_config_catalog(self, name: str = "default.json") -> Catalog[DocT]:
        """Load config JSON and validate into a Catalog."""
        raw = self.load_raw(self.config_path(name))
        return Catalog.load(raw, validate=self.validate, schema_name=self.schema_name, schema_version=self.schema_version)

    def save_editable(self, path: Path, editable: EditableCatalog[DocT], *, validate_before_save: bool = True) -> None:
        """
        Save an EditableCatalog raw document to disk.

        validate_before_save:
          - True: validate using self.validate prior to saving
          - False: save raw as-is (useful during iterative editing)
        """
        if validate_before_save:
            _ = self.validate(editable.raw)
        self.save_raw(path, editable.raw)

    def save_catalog(self, path: Path, catalog: Catalog[DocT]) -> None:
        """Dump and save a validated Catalog to disk."""
        raw = catalog.dump(self.dump)
        self.save_raw(path, raw)
