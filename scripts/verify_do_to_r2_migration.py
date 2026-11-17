#!/usr/bin/env python3
"""
Verify that every artifact referenced by the libxdaq/libxdaqnp recipes, which
currently lives under the DigitalOcean Spaces bucket
(https://xdaq.sgp1.cdn.digitaloceanspaces.com), also exists at the same path
under https://dl-conan.kontex.io, so the base_url in those conanfile.py files
can be safely swapped.

How it works:
1. Parse recipes/libxdaq/*/conanfile.py and recipes/libxdaqnp/*/conanfile.py
   to collect the set of versions declared in this repo.
2. List the DO Spaces bucket (it supports the public S3 ListObjectsV2 API)
   under the "libxdaq/" and "xdaq_npapi/" prefixes to get the real object
   keys that exist (avoids guessing os/arch/build_type combinations).
3. Keep only keys whose version segment matches a version declared in step 1.
4. For each matching key, HEAD both the old DO URL and the new dl-conan.kontex.io
   URL, and compare status code + Content-Length.
5. Print a report and exit non-zero if anything is missing/mismatched.

Usage:
    python3 scripts/verify_do_to_r2_migration.py
"""
from __future__ import annotations

import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree

OLD_HOST = "https://xdaq.sgp1.cdn.digitaloceanspaces.com"
NEW_HOST = "https://dl-conan.kontex.io"
LIST_ENDPOINT = f"{OLD_HOST}/?list-type=2"
S3_NS = "{http://s3.amazonaws.com/doc/2006-03-01/}"

REPO_ROOT = Path(__file__).resolve().parent.parent
RECIPES = {
    "libxdaq": REPO_ROOT / "recipes" / "libxdaq",
    "libxdaqnp": REPO_ROOT / "recipes" / "libxdaqnp",
}
# folder name inside the bucket for each recipe
PREFIXES = {
    "libxdaq": "libxdaq/",
    "libxdaqnp": "xdaq_npapi/",
}

TIMEOUT = 20


@dataclass
class CheckResult:
    key: str
    old_status: int | str
    new_status: int | str
    old_length: str | None
    new_length: str | None

    @property
    def ok(self) -> bool:
        return self.old_status == 200 and self.new_status == 200 and self.old_length == self.new_length


def get_declared_versions(recipe_dir: Path) -> set[str]:
    versions = set()
    for conanfile in recipe_dir.glob("*/conanfile.py"):
        versions.add(conanfile.parent.name)
    return versions


def list_bucket_keys(prefix: str) -> list[str]:
    keys: list[str] = []
    continuation_token = None
    while True:
        url = f"{LIST_ENDPOINT}&prefix={prefix}"
        if continuation_token:
            url += f"&continuation-token={urllib.parse.quote(continuation_token)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = resp.read()
        root = ElementTree.fromstring(data)
        for content in root.findall(f"{S3_NS}Contents"):
            key = content.findtext(f"{S3_NS}Key")
            if key:
                keys.append(key)
        is_truncated = root.findtext(f"{S3_NS}IsTruncated") == "true"
        if not is_truncated:
            break
        continuation_token = root.findtext(f"{S3_NS}NextContinuationToken")
        if not continuation_token:
            break
    return keys


def key_matches_versions(key: str, versions: set[str]) -> bool:
    # keys look like "<prefix>/<os>-<arch>[-<build_type>]-<version>.zip"
    m = re.search(r"-(\d+\.\d+\.\d+)\.zip$", key)
    return bool(m) and m.group(1) in versions


def head(url: str) -> tuple[int | str, str | None]:
    # Cloudflare (fronting dl-conan.kontex.io) blocks the default
    # "Python-urllib/x.y" user agent, so spoof a normal browser UA.
    req = urllib.request.Request(
        url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, resp.headers.get("Content-Length")
    except urllib.error.HTTPError as e:
        return e.code, None
    except urllib.error.URLError as e:
        return f"error: {e.reason}", None


def check_key(key: str) -> CheckResult:
    old_status, old_length = head(f"{OLD_HOST}/{key}")
    new_status, new_length = head(f"{NEW_HOST}/{key}")
    return CheckResult(key, old_status, new_status, old_length, new_length)


def main() -> int:
    all_ok = True
    for name, recipe_dir in RECIPES.items():
        versions = get_declared_versions(recipe_dir)
        print(f"\n=== {name}: {len(versions)} recipe version(s): {sorted(versions)} ===")

        keys = list_bucket_keys(PREFIXES[name])
        matching_keys = [k for k in keys if key_matches_versions(k, versions)]
        print(f"Bucket has {len(keys)} object(s) under '{PREFIXES[name]}', "
              f"{len(matching_keys)} match a declared recipe version.")

        if not matching_keys:
            print("  ! No matching objects found - cannot verify.")
            all_ok = False
            continue

        results: list[CheckResult] = []
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = {pool.submit(check_key, k): k for k in matching_keys}
            for fut in as_completed(futures):
                results.append(fut.result())

        results.sort(key=lambda r: r.key)
        for r in results:
            marker = "OK " if r.ok else "FAIL"
            print(f"  [{marker}] {r.key}  old={r.old_status} new={r.new_status} "
                  f"old_len={r.old_length} new_len={r.new_length}")
            if not r.ok:
                all_ok = False

    print()
    if all_ok:
        print("All checked artifacts exist under both URLs with matching sizes. "
              "Safe to replace the base_url.")
    else:
        print("Some artifacts are missing or mismatched at the new host. "
              "Do NOT replace the base_url until these are resolved.")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
