# scripts/CSVcleaner/clean_csv_generic.py
from __future__ import annotations

import argparse
import csv
import html as _html
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple, Union

import pandas as pd
from pandas.errors import ParserError

from helpers.persist.catalog_loader import CatalogLoader
from helpers.validation import ValidationError
# Reuse your robust reader ideas from clean_kb.py :contentReference[oaicite:2]{index=2}
COMMON_ENCODINGS = ["utf-8", "cp1252", "latin-1", "iso-8859-1", "cp1250", "iso-8859-2"]

# ----------------------------- robust read -----------------------------

def read_csv_with_fallback(path: Union[str, Path], **kwargs) -> Tuple[pd.DataFrame, str]:
    last_err = None
    for enc in COMMON_ENCODINGS:
        try:
            return pd.read_csv(path, encoding=enc, **kwargs), enc
        except UnicodeDecodeError as e:
            last_err = e
        except ParserError:
            raise
    # last resort
    try:
        return pd.read_csv(path, encoding="utf-8", encoding_errors="replace", **kwargs), "utf-8+replace"
    except TypeError:
        return pd.read_csv(path, encoding="latin-1", **kwargs), "latin-1"


def read_csv_best_effort(path: Union[str, Path]) -> Tuple[pd.DataFrame, str, bool]:
    """
    Try normal read first; on ParserError, retry with python engine and skip bad lines.
    """
    try:
        df, enc = read_csv_with_fallback(
            path,
            sep=None,
            engine="python",
            dtype=str,
            keep_default_na=False,
        )
        return df, enc, False
    except ParserError:
        df, enc = read_csv_with_fallback(
            path,
            header=0,
            sep=None,
            engine="python",
            dtype=str,
            keep_default_na=False,
            on_bad_lines="skip",
        )
        return df, enc, True


def dedupe_header(cols: Sequence[str]) -> List[str]:
    out: List[str] = []
    seen: Dict[str, int] = {}
    for i, c in enumerate(cols, start=1):
        base = re.sub(r"\s+", " ", str(c or "").strip())
        if base == "":
            base = f"col{i}"
        key = base.lower()
        n = seen.get(key, 0) + 1
        seen[key] = n
        out.append(base if n == 1 else f"{base}_{n}")
    return out


# ----------------------------- HTML transforms -----------------------------

def _try_bs4():
    try:
        from bs4 import BeautifulSoup  # type: ignore
        return BeautifulSoup
    except Exception:
        return None

BS4 = _try_bs4()

def html_to_text_bs4(s: str) -> str:
    """
    Better HTML -> text using BeautifulSoup if installed.
    Preserves bullet-ish structure a bit via separators; strips scripts/styles.
    """
    if not isinstance(s, str):
        s = "" if pd.isna(s) else str(s)

    if not s.strip():
        return ""

    if BS4 is None:
        return html_to_text_regex(s)

    soup = BS4(s, "html.parser")

    # remove noisy parts
    for tag in soup(["script", "style"]):
        tag.decompose()

    # <br> -> newline, paragraphs -> blank line
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for p in soup.find_all("p"):
        # ensure paragraph ends with blank line
        if p.contents:
            p.append("\n\n")

    # list items -> "- "
    for li in soup.find_all("li"):
        li.insert(0, "- ")
        li.append("\n")

    text = soup.get_text()
    text = _html.unescape(text)
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t\f\v]+", " ", text)
    text = re.sub(r"\s*\n\s*", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_links_bs4(s: str) -> List[str]:
    if not isinstance(s, str):
        s = "" if pd.isna(s) else str(s)
    if not s.strip():
        return []
    if BS4 is None:
        # best-effort regex fallback
        return re.findall(r'href="([^"]+)"', s)

    soup = BS4(s, "html.parser")
    links = []
    for a in soup.find_all("a"):
        href = (a.get("href") or "").strip()
        if href:
            links.append(href)
    # dedupe preserving order
    seen = set()
    out = []
    for u in links:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def html_to_text_regex(s: str) -> str:
    """
    Your existing approach (kept as fallback).
    Similar spirit to clean_kb.py::html_to_text :contentReference[oaicite:3]{index=3}
    """
    if not isinstance(s, str):
        s = "" if pd.isna(s) else str(s)
    s = re.sub(r"(?i)<\s*br\s*/?\s*>", "\n", s)
    s = re.sub(r"(?i)</\s*p\s*>", "\n\n", s)
    s = re.sub(r"(?is)<\s*script[^>]*>.*?</\s*script\s*>", "", s)
    s = re.sub(r"(?is)<\s*style[^>]*>.*?</\s*style\s*>", "", s)
    s = re.sub(r"(?is)</?\w+[^>]*>", "", s)
    s = _html.unescape(s)
    s = s.replace("\u00a0", " ")
    s = re.sub(r"[ \t\f\v]+", " ", s)
    s = re.sub(r"\s*\n\s*", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def looks_like_html(s: str) -> bool:
    if not isinstance(s, str):
        return False
    return bool(re.search(r"<[^>]+>", s))


# ----------------------------- normalizers -----------------------------

def normalize_meta(s: str) -> str:
    if not isinstance(s, str):
        s = "" if pd.isna(s) else str(s)
    tmp = re.sub(r"[;|/]", ",", s).replace("\u00a0", " ")
    parts = re.split(r"[,\s]+", tmp)
    out, seen = [], set()
    for p in parts:
        p2 = p.strip().strip("#").strip()
        if not p2:
            continue
        k = p2.lower()
        if k not in seen:
            seen.add(k)
            out.append(p2)
    return "; ".join(out)


# ----------------------------- recipe -----------------------------

@dataclass(frozen=True)
class HtmlDeriveSpec:
    source_col: str
    out_html_col: str = "text_html"
    out_text_col: str = "text_text"
    out_links_col: str = "text_links"
    out_has_html_col: str = "text_has_html"
    out_word_count_col: Optional[str] = "text_word_count"  # set None to disable


@dataclass(frozen=True)
class CleanRecipe:
    keep_cols: Optional[List[str]] = None      # if None: keep all
    rename_map: Optional[Dict[str, str]] = None
    html_derive: Optional[List[HtmlDeriveSpec]] = None
    meta_cols: Optional[List[str]] = None      # normalize these as meta/tag strings
    drop_empty_rows: bool = True


@dataclass(frozen=True)
class CleanCsvSidecar:
    columns: List[str]
    rows: int
    encoding: str
    ragged: bool


def validate_clean_csv_sidecar(raw: Dict[str, object]) -> CleanCsvSidecar:
    if not isinstance(raw, dict):
        raise ValidationError("Doc must be an object")

    cols = raw.get("columns") or []
    if not isinstance(cols, list) or not all(isinstance(c, str) for c in cols):
        raise ValidationError("columns must be a list of strings")

    rows = raw.get("rows")
    if not isinstance(rows, int) or rows < 0:
        raise ValidationError("rows must be a non-negative integer")

    encoding = raw.get("encoding")
    if not isinstance(encoding, str) or not encoding:
        raise ValidationError("encoding must be a non-empty string")

    ragged = raw.get("ragged")
    if not isinstance(ragged, bool):
        raise ValidationError("ragged must be a boolean")

    return CleanCsvSidecar(columns=list(cols), rows=rows, encoding=encoding, ragged=ragged)


def dump_clean_csv_sidecar(doc: CleanCsvSidecar) -> Dict[str, object]:
    return {
        "columns": list(doc.columns),
        "rows": doc.rows,
        "encoding": doc.encoding,
        "ragged": doc.ragged,
    }


SIDECAR_LOADER: CatalogLoader[CleanCsvSidecar] = CatalogLoader(
    app_name="CSVcleaner",
    schema_name="clean_csv_sidecar",
    schema_version=1,
    validate=validate_clean_csv_sidecar,
    dump=dump_clean_csv_sidecar,
)


def write_sidecar(path: Path, doc: CleanCsvSidecar) -> None:
    raw = dump_clean_csv_sidecar(doc)
    _ = validate_clean_csv_sidecar(raw)
    SIDECAR_LOADER.save_raw(path, raw)


def apply_recipe(df: pd.DataFrame, recipe: CleanRecipe) -> pd.DataFrame:
    df = df.copy()

    # header cleanup
    df.columns = dedupe_header([str(c) for c in df.columns])

    # keep / select
    if recipe.keep_cols:
        missing = [c for c in recipe.keep_cols if c not in df.columns]
        if missing:
            raise KeyError(f"Missing columns: {missing}. Available: {list(df.columns)}")
        df = df[recipe.keep_cols].copy()

    # rename
    if recipe.rename_map:
        df = df.rename(columns=recipe.rename_map)

    # html derive
    if recipe.html_derive:
        for spec in recipe.html_derive:
            if spec.source_col not in df.columns:
                raise KeyError(f"HTML source column not found: {spec.source_col}")
            src = df[spec.source_col].astype(str)

            df[spec.out_html_col] = src
            df[spec.out_has_html_col] = src.map(looks_like_html).astype(int)
            df[spec.out_text_col] = src.map(html_to_text_bs4)
            df[spec.out_links_col] = src.map(lambda x: json.dumps(extract_links_bs4(x), ensure_ascii=False))

            if spec.out_word_count_col:
                df[spec.out_word_count_col] = df[spec.out_text_col].map(lambda t: len(str(t).split()))

    # meta normalization
    if recipe.meta_cols:
        for c in recipe.meta_cols:
            if c in df.columns:
                df[c] = df[c].map(normalize_meta)

    # drop empty rows
    if recipe.drop_empty_rows and not df.empty:
        mask = df.astype(str).apply(lambda r: "".join(r).strip() != "", axis=1)
        df = df.loc[mask].reset_index(drop=True)

    return df


# ----------------------------- CLI -----------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Generic CSV cleaner with HTML-derived columns.")
    ap.add_argument("--in", dest="input_path", required=True)
    ap.add_argument("--out", dest="output_path", required=True)

    ap.add_argument("--keep", default="", help="Comma-separated columns to keep (optional).")
    ap.add_argument("--rename", default="", help="JSON dict for renames, e.g. '{\"A\":\"a\",\"B\":\"b\"}'")
    ap.add_argument("--html-col", default="", help="Column to derive HTML columns from (optional).")
    ap.add_argument("--meta-cols", default="", help="Comma-separated meta/tag columns to normalize (optional).")
    ap.add_argument("--sidecar", default="", help="Optional JSON sidecar path for metadata.")

    args = ap.parse_args()

    df, enc, ragged = read_csv_best_effort(args.input_path)
    print(f"[read] enc={enc} ragged={ragged} shape={df.shape}")

    keep_cols = [c.strip() for c in args.keep.split(",") if c.strip()] or None
    rename_map = json.loads(args.rename) if args.rename.strip() else None
    meta_cols = [c.strip() for c in args.meta_cols.split(",") if c.strip()] or None

    html_derive = None
    if args.html_col.strip():
        html_derive = [HtmlDeriveSpec(source_col=args.html_col.strip())]

    recipe = CleanRecipe(
        keep_cols=keep_cols,
        rename_map=rename_map,
        html_derive=html_derive,
        meta_cols=meta_cols,
    )

    out = apply_recipe(df, recipe)
    Path(args.output_path).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output_path, index=False, encoding="utf-8", lineterminator="\n")
    print(f"[write] {args.output_path} rows={len(out)}")

    if args.sidecar.strip():
        sidecar_path = Path(args.sidecar)
        sidecar = CleanCsvSidecar(
            columns=[str(c) for c in out.columns],
            rows=int(len(out)),
            encoding=enc,
            ragged=ragged,
        )
        write_sidecar(sidecar_path, sidecar)
        print(f"[sidecar] {sidecar_path}")

if __name__ == "__main__":
    main()
