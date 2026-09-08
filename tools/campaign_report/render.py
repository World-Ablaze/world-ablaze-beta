"""Assemble a self-contained document; save content is data, never executable HTML."""
from __future__ import annotations

import html
import base64
import gzip
import json
import re
from pathlib import Path

WEB = Path(__file__).with_name("web")
REPO = Path(__file__).resolve().parents[2]
DEFAULT_TITLE = "World Ablaze · Campaign overview"
LOC_LINE = re.compile(r'^\s*([A-Za-z0-9_.\-]+):\d*\s*"(.*)"\s*(?:#.*)?$')


def equipment_names(definitions, root: Path = REPO) -> dict:
    """Display names for equipment definition keys, read from the mod's English localisation.

    A save's equipment registry names only the designed variants (`name="M36 Jackson"`); the base
    entry of the same chassis carries no name and the game shows the localised key instead. The
    report resolves that key the same way, and keeps the raw key visible beside it."""
    wanted = {d for d in definitions if d}
    names = {}
    if not wanted:
        return names
    for path in sorted((root / "localisation/replace").glob("*_l_english.yml")):
        try:
            text = path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            match = LOC_LINE.match(line)
            if match and match.group(1) in wanted and match.group(1) not in names:
                names[match.group(1)] = match.group(2)
        if len(names) == len(wanted):
            break
    return names


def variant_definitions(data: dict) -> set:
    return {v.get("definition") for snap in data.get("snapshots", []) for c in snap.get("countries", {}).values()
            for v in (c.get("equipment", {}) or {}).get("variants", []) or []}


def presentation(data: dict) -> dict:
    """Presentation metadata added over the cached observations: title, language, display names."""
    return {**data, "title": data.get("title") or DEFAULT_TITLE, "language": "en",
            "equipment_names": equipment_names(variant_definitions(data))}


def document(data: dict) -> str:
    data = presentation(data)
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    if len(payload) > 1_000_000:
        compressed = gzip.compress(payload.encode("utf-8"), compresslevel=9, mtime=0)
        payload = json.dumps({"encoding": "gzip-base64", "payload": base64.b64encode(compressed).decode("ascii")})
    payload = payload.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    payload = payload.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    substitutions = {
        "__REPORT_TITLE__": html.escape(data.get("title", DEFAULT_TITLE)),
        "/*__REPORT_STYLE__*/": WEB.joinpath("style.css").read_text(encoding="utf-8"),
        "/*__REPORT_DATA__*/": payload,
        "/*__REPORT_APP__*/": WEB.joinpath("app.js").read_text(encoding="utf-8"),
    }
    # One substitution pass: placeholders inside a save's names remain ordinary data.
    pattern = "|".join(re.escape(key) for key in substitutions)
    return re.sub(pattern, lambda m: substitutions[m.group()], WEB.joinpath("index.html").read_text(encoding="utf-8"))


def write_report(data: dict, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document(data), encoding="utf-8", newline="\n")
