#!/usr/bin/env python3
#
# Copyright (C) 2021-2022 Sébastien Helleu <flashcode@flashtux.org>
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

from typing import List, Sequence, Tuple, Dict

import argparse
import urllib.request
import subprocess  # nosec

BUILDERS: Sequence[str] = (
    "docker",
    "podman",
)

DISTROS: Sequence[str] = (
    "debian",
    "alpine",
)

SUPPORTED_PLATFORMS: Dict[str, Dict[str, List[str]]] = {
  "linux": {
    "386": [],
    "amd64": [],
    "arm": ["v6", "v7"],
    "arm64": [],
    "ppc64le": [],
    "s390x": [],
  },
}


def generate_valid_platforms() -> list[str]:
    """Return the list of supported platforms."""
    valid_platforms = []
    for os_name, archs in SUPPORTED_PLATFORMS.items():
        for arch, variants in archs.items():
            if not variants:
                valid_platforms.append(f"{os_name}/{arch}")
            for variant in variants:
                valid_platforms.append(f"{os_name}/{arch}/{variant}")
    return valid_platforms


def get_parser() -> argparse.ArgumentParser:
    """Return the command line parser."""
    parser = argparse.ArgumentParser(description="Build of WeeChat container")
    parser.add_argument(
        "-b",
        "--builder",
        choices=BUILDERS,
        default=BUILDERS[0],
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
        help="base Linux distribution for the container, default %(default)s",
    )
    parser.add_argument(
        "-p",
        "--platforms",
        default="linux/amd64",
        choices=generate_valid_platforms(),
        nargs="+",
        help="build platforms",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        default=False,
        help=(
            "push the images to the registry, default: %(default)s"
        ),
    )
    parser.add_argument(
        "-r",
        "--registry-project",
        default="docker.io/weechat",
        help="registry project, default: %(default)s",
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
    :param slim: slim version
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
            numbers = version.split(".")
            for i in range(len(numbers)):
                tags.append(".".join(numbers[: i + 1]))
        else:
            tags.append(version)
    tags_args = []
    for tag in reversed(tags):
        for suffix in suffixes:
            tags_args.append(
                    f"weechat:{tag}{suffix}",
            )
    return (version, tags_args)


def run_command(command: List[str], dry_run: bool) -> None:
    """
    Prints the command to run and runs it if 'dry_run=False'

    :param command: ["docker", "images"]
    :param dry_run: True
    :return: None
    """
    print(f'Running: {" ".join(command)}')
    if not dry_run:
        try:
            subprocess.run(command, check=False)  # nosec
        except KeyboardInterrupt:
            pass
        except Exception as exc:  # pylint: disable=broad-except
            print(exc)


def main() -> None:
    """Main function."""
    build_args = ["buildx", "build"]
    args = get_parser().parse_args()
    slim = ["--build-arg", "SLIM=1"] if args.slim else []
    version, tags = get_version_tags(args.version, args.distro, args.slim)

    if args.builder == "docker":
        docker_tags = []
        for tag in tags:
            docker_tags.extend(["-t", f"{args.registry_project}/{tag}"])
        tags = docker_tags
        if args.push:
            build_args.append("--push")

    podman_slim = ""
    if args.slim:
        podman_slim = "-slim"
    podman_manifest_image = f"localhost/weechat:{version}" \
        + f"-{args.distro}{podman_slim}-manifest"
    podman_tags = [tag for tag in tags if tag.startswith("weechat:")]

    if args.builder == "podman":
        build_args = ["build", "--jobs", "0"]
        tags = ["--manifest", podman_manifest_image]

    command = [
        f"{args.builder}",
        *build_args,
        "--platform",
        ",".join(args.platforms),
        "-f",
        f"{args.distro}/Containerfile",
        "--build-arg",
        f"VERSION={version}",
        *slim,
        *tags,
        ".",
    ]
    run_command(command, args.dry_run)

    if args.builder == "podman":
        command = [
              f"{args.builder}",
              "tag",
              podman_manifest_image,
              *[f"localhost/{tag}" for tag in podman_tags]
        ]
        run_command(command, args.dry_run)

        if args.push:
            for tag in podman_tags:
                command = [
                      f"{args.builder}",
                      "manifest",
                      "push",
                      f"localhost/{tag}",
                      f"{args.registry_project}/{tag}"
                ]
                run_command(command, args.dry_run)


if __name__ == "__main__":
    main()
