# helpers/toolkits/ui/runtime/spec_resolve.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from helpers.validation import ValidationError
from helpers.fs import read_json_strict
from helpers.fs.paths import join_safe

from helpers.toolkits.ui.spec.models import WindowSpec


def resolve_window_factory_args(
    window: WindowSpec,
    *,
    helpers_root: Optional[Path],
) -> Dict[str, Any]:
    base: Dict[str, Any] = {}

    if window.factory_args_ref:
        base = _load_args_ref(window.factory_args_ref, helpers_root=helpers_root)

    inline = dict(window.factory_args or {})
    # Inline overrides base
    merged = dict(base)
    merged.update(inline)
    return merged


def _load_args_ref(ref: str, *, helpers_root: Optional[Path]) -> Dict[str, Any]:
    ref = str(ref)

    if ref.startswith("path:"):
        p = Path(ref[len("path:") :]).expanduser()
        raw = read_json_strict(p, root_types=(dict,))
        return dict(raw)

    if ref.startswith("configs:"):
        if helpers_root is None:
            raise ValidationError(
                f"factory_args_ref={ref!r} requires helpers_root (to resolve helpers/configs/<app>/...)"
            )
        tail = ref[len("configs:") :]
        # Expect "<app>/<relpath>"
        if "/" not in tail:
            raise ValidationError(f"configs: ref must be 'configs:<app>/<path>', got {ref!r}")
        app, rel = tail.split("/", 1)
        p = join_safe(Path(helpers_root), "configs", app, rel)
        raw = read_json_strict(p, root_types=(dict,))
        return dict(raw)

    raise ValidationError(f"Unsupported factory_args_ref scheme: {ref!r}")
