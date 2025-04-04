#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: 2021-2025 Sébastien Helleu <flashcode@flashtux.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""Build WeeChat container image."""

from typing import List, Sequence, Tuple

import argparse
import urllib.request
import subprocess  # nosec

DISTROS: Sequence[str] = (
    "debian",
    "alpine",
)


def get_parser() -> argparse.ArgumentParser:
    """Return the command line parser."""
    parser = argparse.ArgumentParser(description="Build of WeeChat container")
    parser.add_argument(
        "-b",
        "--builder",
        default="docker",
        help=(
            "program used to build the container image, "
            "like docker (default) or podman"
        ),
    )
    parser.add_argument(
        "-d",
        "--distro",
        choices=DISTROS,
        default=DISTROS[0],
        help="base Linux distribution for the container",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help=("dry run: display command but do not run it"),
    )
    parser.add_argument(
        "-s",
        "--slim",
        action="store_true",
        help=(
            "slim version: build without plugins: " "script, scripts, spell"
        ),
    )
    parser.add_argument(
        "version",
        help=(
            'version to build: numeric (like "3.0") or '
            'alias: "latest" (or "stable"), "devel"'
        ),
    )
    return parser


def get_version_tags(
    version: str, distro: str, slim: bool
) -> Tuple[str, List[str]]:
    """
    Get WeeChat version and tags to apply on the container image.

    :param version: x.y, x.y.z, "latest", "stable", "devel"
    :param distro: "debian" or "alpine"
    :paral slim: slim version
    :return: tuple (version, tags) where version if the version of WeeChat
        to build and tags is a list of tag arguments for command line,
        for example: ['-t', 'weechat:3.0-alpine',
                      '-t', 'weechat/weechat:3.0-alpine',
                      '-t', 'weechat:3-alpine',
                      '-t', 'weechat/weechat:3-alpine']
    """
    str_slim = "-slim" if slim else ""
    if distro == "debian":
        suffixes = [str_slim, f"-{distro}{str_slim}"]
    else:
        suffixes = [f"-{distro}{str_slim}"]
    tags = []
    if version == "devel":
        tags.append(version)
    else:
        if version in ("latest", "stable"):
            tags.append("latest")
            url = "https://weechat.org/dev/info/stable/"
            with urllib.request.urlopen(url) as response:  # nosec
                version = response.read().decode("utf-8").strip()
        else:
            tags.append(version)
        numbers = version.split(".")
        for i in range(len(numbers)):
            tags.append(".".join(numbers[: i + 1]))
    tags_args = []
    for tag in reversed(tags):
        for suffix in suffixes:
            tags_args.extend(
                [
                    "-t",
                    f"weechat:{tag}{suffix}",
                    "-t",
                    f"weechat/weechat:{tag}{suffix}",
                ]
            )
    return (version, tags_args)


def main() -> None:
    """Main function."""
    args = get_parser().parse_args()
    slim = ["--build-arg", "SLIM=1"] if args.slim else []
    version, tags = get_version_tags(args.version, args.distro, args.slim)
    command = [
        f"{args.builder}",
        "build",
        "-f",
        f"{args.distro}/Containerfile",
        "--build-arg",
        f"VERSION={version}",
        *slim,
        *tags,
        ".",
    ]
    print(f'Running: {" ".join(command)}')
    if not args.dry_run:
        try:
            subprocess.run(command, check=False)  # nosec
        except KeyboardInterrupt:
            pass
        except Exception as exc:  # pylint: disable=broad-except
            print(exc)


if __name__ == "__main__":
    main()
