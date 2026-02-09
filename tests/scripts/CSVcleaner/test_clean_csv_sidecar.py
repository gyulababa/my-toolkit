from __future__ import annotations

import sys
from pathlib import Path

from helpers.fs import read_json_strict


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import CSVcleaner.clean_csv_generic as clean_csv_generic  # noqa: E402
from CSVcleaner.clean_csv_generic import (  # noqa: E402
    CleanCsvSidecar,
    CleanRecipe,
    apply_recipe,
    write_sidecar,
)
from pandas.errors import ParserError  # noqa: E402


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _read_sidecar(path: Path) -> dict:
    return read_json_strict(path, root_types=(dict,))


def test_sidecar_metadata_normal_parse(tmp_path: Path) -> None:
    src = tmp_path / "input.csv"
    out_path = tmp_path / "output.csv"
    sidecar_path = tmp_path / "output.sidecar.json"

    _write_text(src, "a,b\n1,2\n3,4\n")

    df, enc, ragged = clean_csv_generic.read_csv_best_effort(src)
    assert ragged is False

    out = apply_recipe(df, CleanRecipe())
    out.to_csv(out_path, index=False, encoding="utf-8", lineterminator="\n")

    sidecar = CleanCsvSidecar(
        columns=[str(c) for c in out.columns],
        rows=int(len(out)),
        encoding=enc,
        ragged=ragged,
    )
    write_sidecar(sidecar_path, sidecar)

    raw = _read_sidecar(sidecar_path)
    assert raw["columns"] == [str(c) for c in out.columns]
    assert raw["rows"] == len(out)
    assert raw["encoding"] == enc
    assert raw["ragged"] is False


def test_sidecar_metadata_ragged_parse(tmp_path: Path, monkeypatch) -> None:
    src = tmp_path / "input_ragged.csv"
    out_path = tmp_path / "output_ragged.csv"
    sidecar_path = tmp_path / "output_ragged.sidecar.json"

    _write_text(src, "a,b\n1,2,3\n4,5\n")

    original = clean_csv_generic.read_csv_with_fallback
    calls = {"n": 0}

    def fake_read(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            raise ParserError("forced ragged parse")
        return original(*args, **kwargs)

    monkeypatch.setattr(clean_csv_generic, "read_csv_with_fallback", fake_read)

    df, enc, ragged = clean_csv_generic.read_csv_best_effort(src)
    assert ragged is True

    out = apply_recipe(df, CleanRecipe())
    out.to_csv(out_path, index=False, encoding="utf-8", lineterminator="\n")

    sidecar = CleanCsvSidecar(
        columns=[str(c) for c in out.columns],
        rows=int(len(out)),
        encoding=enc,
        ragged=ragged,
    )
    write_sidecar(sidecar_path, sidecar)

    raw = _read_sidecar(sidecar_path)
    assert raw["columns"] == [str(c) for c in out.columns]
    assert raw["rows"] == len(out)
    assert raw["encoding"] == enc
    assert raw["ragged"] is True
