<!-- helpers/catalog/README.md -->
helpers/catalog
Purpose

Typed catalog containers:

Catalog: validated, schema-tagged, immutable container around a typed doc

EditableCatalog: editable raw dict with optional undo/redo, plus validation bridge

Belongs here

The typed container (Catalog)

The editable raw representation (EditableCatalog)

Schema tagging (name/version)

Validation bridge (validate raw → typed; typed → raw via dump)

Does not belong here

Disk IO, JSON reading/writing → helpers/catalogloader + helpers/fs

Path conventions, file naming rules → helpers/catalogloader

In-memory patching logic itself → helpers/history

Public API (flat list)

Catalog

Catalog.load(raw, validate, schema_name="catalog", schema_version=1)

dump(dump_fn) -> dict

schema_tag() -> str

EditableCatalog

EditableCatalog.from_catalog(catalog_or_doc, dump_fn, schema_name=..., schema_version=..., history=None)

validate(validate_fn) -> DocT

to_catalog(validate=...) -> Catalog[DocT]