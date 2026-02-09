<!-- helpers/validation/README.md -->
helpers/validation
Purpose

Small, explicit validation utilities for input hygiene (config files, schemas, user inputs). Provides:

scalar validators (ensure_*)

mapping readers (require_* and optional_*)

network input helpers (host/port/url parsing)

time parsing helpers for time-of-day and durations

Belongs here

Type + range checking of input values

Reading typed values from dict-like mappings

Friendly errors for invalid inputs (ValidationError)

Parsing/normalization helpers where the primary goal is validation

Does not belong here

Filesystem IO → helpers/fs

Domain persistence/versioning → helpers/persist

In-memory patch/path semantics → helpers/history

Business rules (project-specific logic) → project code

Error type

ValidationError: raised for validation failures (bad values, missing required fields)

Public API (flat list)
Errors

ValidationError

type_name(x)

qpath(path)

Scalar validators (scalars.py)

ensure_dict(v, path="value")

ensure_list(v, path="value")

ensure_non_empty_list(v, path="value")

ensure_str(v, path="value", allow_empty=False)

ensure_bool(v, path="value")

ensure_int(v, path="value", min_v=None, max_v=None)

ensure_float(v, path="value", min_v=None, max_v=None)

ensure_one_of(value, allowed, path="value")

ensure_list_of_dicts(v, path="value")

ensure_list_of_str(v, path="value", allow_empty_items=False)

ensure_dict_of_str(v, path="value", allow_empty_values=False)

ensure_unique(items, key_fn, what="value", path="items")

ensure_ip(ip, path="ip", version=None)

ensure_pathlike(v, path="value", expanduser=True, resolve=False)

ensure_enum_name(v, path="value")

ensure_regex(v, path="value")

Network validators (net.py)

ensure_port(v, path="port")

ensure_host(v, path="host", allow_localhost=True)

ensure_endpoint(v, path="endpoint") -> (host, port)

ensure_http_url(v, path="url")

Mapping readers (mapping.py)

path_join(path, key)

require_str(d, key, path="", allow_empty=False, default=_MISSING)

require_int(d, key, path="", min_v=None, max_v=None, default=_MISSING)

require_float(d, key, path="", min_v=None, max_v=None, default=_MISSING)

require_bool(d, key, path="", default=_MISSING)

require_list_of_dicts(d, key, path="", default=_MISSING)

require_list_of_str(d, key, path="", allow_empty_items=False, default=_MISSING)

require_dict_of_str(d, key, path="", allow_empty_values=False, default=_MISSING)

require_one_of(d, key, allowed, path="", default=_MISSING)

require_path(d, key, path="", expanduser=True, resolve=False, default=_MISSING)

require_regex(d, key, path="", default=_MISSING)

require_ip(d, key, path="", version=None, default=_MISSING)

require_port(d, key, path="", default=_MISSING)

require_host(d, key, path="", allow_localhost=True, default=_MISSING)

require_endpoint(d, key, path="", default=_MISSING)

require_http_url(d, key, path="", default=_MISSING)

optional_str(d, key, path="", allow_empty=False, default=None)

optional_int(d, key, path="", min_v=None, max_v=None, default=None)

optional_float(d, key, path="", min_v=None, max_v=None, default=None)

optional_bool(d, key, path="", default=None)

optional_list_of_str(d, key, path="", allow_empty_items=False, default=None)

optional_path(d, key, path="", expanduser=True, resolve=False, default=None)

Time validation/parsing (time.py)

ensure_tz(dt, tz=UTC)

parse_time_of_day("HH:MM[:SS]")

dt(value, tz=UTC)

resolve_time_like(value, tz, reference=None)

ensure_end_after_start(start, end)

parse_duration("1h30m" | "90m" | "45s" | "2d" | "1w")