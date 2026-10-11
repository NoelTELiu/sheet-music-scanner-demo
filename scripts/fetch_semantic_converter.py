#!/usr/bin/env python3
"""Download the public PrIMuS semantic converter archive and extract its JAR.

The binary is intentionally not committed to this portfolio repository.
"""

import argparse
import io
import tarfile
import urllib.request
from pathlib import Path

DEFAULT_URL = "https://grfia.dlsi.ua.es/primus/primus_converter.tgz"
JAR_NAME = "omr-3.0-SNAPSHOT.jar"


def main():
    parser = argparse.ArgumentParser(description="Fetch the third-party PrIMuS semantic converter.")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--output", default=f"assets/{JAR_NAME}")
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    print(f"Downloading converter archive from: {args.url}")
    try:
        with urllib.request.urlopen(args.url, timeout=60) as response:
            archive_bytes = response.read()
    except Exception as exc:
        raise SystemExit(
            "Download failed. The upstream research server may be temporarily unavailable. "
            f"You can manually place {JAR_NAME} at {output}.\nDetails: {exc}"
        )

    try:
        with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
            candidates = [m for m in archive.getmembers() if Path(m.name).name == JAR_NAME and m.isfile()]
            if not candidates:
                raise SystemExit(f"Archive did not contain {JAR_NAME}.")
            member = candidates[0]
            source = archive.extractfile(member)
            if source is None:
                raise SystemExit(f"Could not read {JAR_NAME} from archive.")
            output.write_bytes(source.read())
    except tarfile.TarError as exc:
        raise SystemExit(f"Downloaded file was not a valid .tgz archive: {exc}")

    print(f"Saved converter JAR to: {output}")
    print(f"Size: {output.stat().st_size / (1024 * 1024):.1f} MiB")


if __name__ == "__main__":
    main()
