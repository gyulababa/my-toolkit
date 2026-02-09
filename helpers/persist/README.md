<!-- helpers/persist/README.md -->
helpers/persist
Purpose

Opinionated local persistence helpers for “domain documents” stored as JSON files, with:

an index.json registry per domain

monotonically allocated doc ids (0001.json, 0002.json, …)

active/latest doc selection

pruning, validation, and repair utilities

import/export via ZIP

Belongs here

Domain directory conventions and doc naming

Index lifecycle (seed, next_id allocation, active pointer)

“Latest/active” selectors and listing doc ids

Integrity checks and repair functions

ZIP import/export for sharing/backups

Does not belong here

General JSON/text IO → helpers/fs

Schema validation of doc content → helpers/validation

Undo/redo in-memory history → helpers/history

App-specific storage policies → project code

Public API (flat list)
Path conventions

domain_dir(persist_root, domain)

index_path(persist_root, domain)

doc_path(persist_root, domain, doc_id)

Index lifecycle / selectors

ensure_seeded(persist_root, domain, seed_raw=None, seed_note="seed")

read_index(persist_root, domain)

write_index(persist_root, domain, index)

allocate_next_id(persist_root, domain, note="allocate")

set_active(persist_root, domain, doc_id, note="set_active")

set_active_latest(persist_root, domain)

resolve_doc_id(persist_root, domain, selector) (e.g. "active", "latest", "0007")

get_active_path(persist_root, domain)

Listing / pruning

list_doc_ids(persist_root, domain)

prune_docs(persist_root, domain, keep_last=..., keep_active=True)

Integrity

validate_domain_state(persist_root, domain)

repair_domain_state(persist_root, domain, ensure_seed_doc=True)

Import / export

export_domain_zip(persist_root, domain, zip_path, overwrite=False)

import_domain_zip(zip_path, persist_root, domain, strategy="merge")

Types

PersistIndex

PersistHistoryEntry

DomainReport (if present in your types module)