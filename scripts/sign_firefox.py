#!/usr/bin/env python3
"""Build and sign the Firefox add-on (.xpi) for a permanent local install.

  $ python3 scripts/sign_firefox.py [--lint-only]

Signs extension/ as an unlisted add-on on addons.mozilla.org and saves the
signed .xpi in dist/. Install it from about:addons > gear menu >
"Install Add-on From File".

Needs Node.js (npx runs web-ext) and AMO API credentials
(https://addons.mozilla.org/developers/addon/api/key/) in WEB_EXT_API_KEY and
WEB_EXT_API_KEY_SECRET, from the environment, or a .env file in the repo root.

The signed copy's version is <manifest_version>.<commit_count> because AMO signs
each version only once: commit before signing again. Chrome-only manifest fields
are left out of the copy; extension/manifest.json is unchanged.
"""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
CREDENTIALS = ("WEB_EXT_API_KEY", "WEB_EXT_API_KEY_SECRET")
IGNORE = shutil.ignore_patterns(
    "test", "node_modules", "package.json", "bun.lock"
)  # Keep in sync with fw.py setup
WEB_EXT = ["npx", "--yes", "web-ext"]


def run(cmd, **kwargs):
    try:
        return subprocess.run(cmd, cwd=ROOT, check=True, **kwargs)
    except subprocess.CalledProcessError as error:
        sys.exit(error.returncode)


def git(*args):
    return run(["git", *args], capture_output=True, text=True).stdout.strip()


def firefox_manifest(manifest, build):
    """The signed copy's manifest: a version AMO hasn't seen, and no Chrome-only
    fields."""
    parts = manifest["version"].split(".")
    if len(parts) > 3:
        sys.exit(
            f"Version {manifest['version']} already has 4+ parts; Firefox allows no room for a build number."
        )
    out = {k: v for k, v in manifest.items() if k != "key"}
    out["version"] = ".".join(parts + [str(build)])
    out["background"] = {
        k: v for k, v in manifest["background"].items() if k != "service_worker"
    }
    return out


def load_env():
    """The AMO credentials from <repo>/.env (KEY=value lines), unless the
    environment already has them."""
    path = ROOT / ".env"
    if not path.is_file():
        return
    for line in path.read_text().splitlines():
        name, sep, value = line.strip().removeprefix("export ").partition("=")
        if sep and name.strip() in CREDENTIALS and not os.environ.get(name.strip()):
            os.environ[name.strip()] = value.strip().strip("\"'")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--lint-only", action="store_true", help="build and lint the copy, sign nothing"
    )
    args = parser.parse_args(argv)

    if not shutil.which("npx"):
        sys.exit("Needs Node.js: npx runs web-ext.")
    if not args.lint_only and git("status", "--porcelain", "--", "extension"):
        sys.exit(
            "extension/ has uncommitted changes; commit them first so each signed version matches a commit."
        )

    built = firefox_manifest(
        json.loads((ROOT / "extension" / "manifest.json").read_text()),
        int(git("rev-list", "--count", "HEAD")),
    )
    version = built["version"]
    signed = sorted(DIST.glob(f"*{version}*.xpi"))

    if signed and not args.lint_only:
        print(f"Version {version} is already signed: {signed[-1]}")
        return

    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "extension"
        shutil.copytree(ROOT / "extension", source, ignore=IGNORE)
        (source / "manifest.json").write_text(json.dumps(built, indent=2) + "\n")

        run(WEB_EXT + ["lint", "--source-dir", str(source)])

        if args.lint_only:
            return

        load_env()

        missing = [name for name in CREDENTIALS if not os.environ.get(name)]
        if missing:
            sys.exit(
                f"Set {' and '.join(missing)} (environment or .env); keys: "
                "https://addons.mozilla.org/developers/addon/api/key/"
            )

        DIST.mkdir(exist_ok=True)
        print(
            f"Signing {version} as unlisted on AMO; this waits for the automatic review."
        )

        run(
            WEB_EXT
            + [
                "sign",
                "--channel",
                "unlisted",
                "--source-dir",
                str(source),
                "--artifacts-dir",
                str(DIST),
            ]
        )

    signed = sorted(DIST.glob(f"*{version}*.xpi")) or sorted(
        DIST.glob("*.xpi"), key=lambda p: p.stat().st_mtime
    )
    print(f"Signed: {signed[-1]}")
    print(
        'Install: about:addons > gear menu > "Install Add-on From File" > that file (on each machine).'
    )
    print(
        "Updating later: commit, rerun this script, install the new .xpi over the old one; settings and key are kept."
    )


if __name__ == "__main__":
    main()
