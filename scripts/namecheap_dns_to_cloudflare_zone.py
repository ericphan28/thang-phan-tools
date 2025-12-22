#!/usr/bin/env python3
"""Convert Namecheap AdvancedDNS JSON to a BIND zone file suitable for Cloudflare import.

Usage:
  python scripts/namecheap_dns_to_cloudflare_zone.py input.json giakiemso.com > giakiemso.com.zone

Notes:
- This script only converts Namecheap "CustomHostRecords".
- Cloudflare TTL will typically become "Auto" on import; we preserve the integer TTL if present.
- Supports RecordType:
    1 = A
    2 = CNAME
    5 = TXT
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


NAMECHEAP_TYPE_MAP: dict[int, str] = {
    1: "A",
    2: "CNAME",
    5: "TXT",
}


def _normalize_host(host: str) -> str:
    host = host.strip()
    if host == "@":
        return "@"
    # Namecheap sometimes returns empty host for apex; treat as @
    if host == "":
        return "@"
    return host


def _normalize_target(rr_type: str, value: str) -> str:
    value = (value or "").strip()
    if rr_type == "CNAME":
        # Namecheap stores CNAME values with trailing dot; Cloudflare accepts both.
        return value.rstrip(".")
    if rr_type == "TXT":
        # Ensure quoted TXT (escape inner quotes)
        escaped = value.replace('"', r'\"')
        return f'"{escaped}"'
    return value


def _safe_ttl(ttl: int | None) -> int:
    if not isinstance(ttl, int) or ttl <= 0:
        return 300
    return ttl


def convert(namecheap_json: dict, origin: str) -> list[str]:
    origin = origin.strip().rstrip(".")

    records = (
        namecheap_json.get("Result", {})
        .get("CustomHostRecords", {})
        .get("Records", [])
    )
    if not isinstance(records, list):
        raise ValueError("Unexpected JSON shape: Result.CustomHostRecords.Records is not a list")

    lines: list[str] = []
    lines.append(f"$ORIGIN {origin}.")
    lines.append("$TTL 300")

    emitted = 0
    for rec in records:
        try:
            if not rec.get("IsActive", True):
                continue
            record_type_id = rec.get("RecordType")
            rr_type = NAMECHEAP_TYPE_MAP.get(int(record_type_id))
            if rr_type is None:
                # Skip unsupported record types
                continue

            host = _normalize_host(str(rec.get("Host", "@")))
            ttl = _safe_ttl(rec.get("Ttl"))
            data = _normalize_target(rr_type, str(rec.get("Data", "")))
            if not data:
                continue

            # BIND format: <name> <ttl> IN <type> <rdata>
            lines.append(f"{host}\t{ttl}\tIN\t{rr_type}\t{data}")
            emitted += 1
        except Exception:
            # Skip malformed record; keep going
            continue

    if emitted == 0:
        raise ValueError("No supported records found to convert (A/CNAME/TXT)")

    return lines


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path, help="Path to Namecheap JSON export")
    ap.add_argument("domain", help="Domain origin, e.g. giakiemso.com")
    args = ap.parse_args()

    try:
        raw = json.loads(args.input.read_text(encoding="utf-8"))
        lines = convert(raw, args.domain)
        sys.stdout.write("\n".join(lines) + "\n")
        return 0
    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
