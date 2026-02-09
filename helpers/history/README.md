<!-- helpers/history/README.md -->
helpers/history
Purpose

Frontend-agnostic undo/redo and patch application for tree-like documents (dict/list/primitive), with:

a compact Operation type

optional Batch grouping (undo as one step)

a History stack (undo/redo)

appliers: mutable (fast) and immutable (copy-on-write)

Belongs here

In-memory path semantics for JSON-like trees (dict/list)

Apply/invert operations

Undo/redo stacks and batching

Copy-on-write applier for snapshot-safe state

Does not belong here

Filesystem paths and IO → helpers/fs

Schema/config validation → helpers/validation

Domain persistence/versioning → helpers/persist

Project-specific semantics of “what operations mean” → project code

Public API (flat list)
Types

PathToken (str | int)

Path (list[PathToken])

OpMeta

Operation

Batch

Paths (tree navigation)

PathError

get_at(doc, path)

set_at(doc, path, value)

del_at(doc, path)

exists_at(doc, path)

Appliers

DocumentApplier (protocol)

TreeApplier (mutable)

ImmutableTreeApplier (copy-on-write)

History stack

HistoryEntry

History

begin_batch(label="")

end_batch()

apply(doc, op) -> doc

undo(doc) -> doc

redo(doc) -> doc

clear()