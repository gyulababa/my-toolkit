# helpers/persist/__init__.py
# Public, frontend-agnostic "persist" helpers: domain-specific persistence conventions built on top of helpers.fs primitives.

from .types import (
    PersistIndex,
    PersistHistoryEntry,
    PersistDocInfo,
    PersistDomainReport,
)
from .paths import domain_dir, index_path, doc_path
from .index import (
    ensure_domain,
    ensure_seeded,
    read_index,
    write_index,
    update_index,
    allocate_next_id,
    set_active,
    set_active_latest,
    get_active_path,
    resolve_doc_id,
    list_doc_ids,
    list_docs,
    get_doc_info,
    prune_docs,
    validate_domain_state,
    repair_domain_state,
    copy_domain,
    export_domain_zip,
    import_domain_zip,
    with_domain_lock,
)
from .persisted_catalog_loader import PersistedCatalogLoader

__all__ = [
    # types
    "PersistIndex",
    "PersistHistoryEntry",
    "PersistDocInfo",
    "PersistDomainReport",
    # paths
    "domain_dir",
    "index_path",
    "doc_path",
    # index / lifecycle
    "ensure_domain",
    "ensure_seeded",
    "read_index",
    "write_index",
    "update_index",
    "allocate_next_id",
    "set_active",
    "set_active_latest",
    "get_active_path",
    "resolve_doc_id",
    "list_doc_ids",
    "list_docs",
    "get_doc_info",
    "prune_docs",
    "validate_domain_state",
    "repair_domain_state",
    # packaging / migration
    "copy_domain",
    "export_domain_zip",
    "import_domain_zip",
    # concurrency
    "with_domain_lock",
    # adapters
    "PersistedCatalogLoader",
]
