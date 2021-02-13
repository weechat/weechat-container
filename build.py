#!/usr/bin/env python3
#
# Copyright (C) 2021 Sébastien Helleu <flashcode@flashtux.org>
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

import argparse
import urllib.request
import subprocess

BUILDERS = ('docker', 'podman')
DISTROS = ('debian', 'alpine')


def get_parser():
    """Return the command line parser."""
    parser = argparse.ArgumentParser(description='Build of WeeChat container')
    parser.add_argument('-b', '--builder',
                        choices=BUILDERS,
                        default=BUILDERS[0],
                        help='program used to build the container image')
    parser.add_argument('-d', '--distro',
                        choices=DISTROS,
                        default=DISTROS[0],
                        help='base distro for the container')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help=('dry run: display command but do not run it'))
    parser.add_argument('-s', '--slim', action='store_true',
                        help=('slim version: build without plugins: '
                              'script, scripts, spell'))
    parser.add_argument('version',
                        help=('version to build: numeric (like "3.0") or '
                              'alias: "latest" (or "stable"), "devel"'))
    return parser


def get_tags_args(version, distro, slim):
    """
    Get tags to apply on the container image.

    :param str version: x.y, x.y.z, "latest", "stable", "devel"
    :param str distro: "debian" or "alpine"
    :paral bool slim: slim version
    :rtype: list
    :return: list of tag arguments for command line, for example:
       ['-t', 'weechat:3.0-alpine', '-t', 'weechat:3-alpine']
    """
    suffix = f'-{distro}' if distro != 'debian' else ''
    if slim:
        suffix += '-slim'
    tags = []
    if version == 'devel':
        tags.append(version)
    else:
        if version in ('latest', 'stable'):
            tags.append('latest')
            url = 'https://weechat.org/dev/info/stable/'
            with urllib.request.urlopen(url) as response:
                version = response.read().decode('utf-8').strip()
        numbers = version.split('.')
        for i in range(len(numbers)):
            tags.append('.'.join(numbers[:i + 1]))
    tags_args = []
    for tag in reversed(tags):
        tags_args.append('-t')
        tags_args.append(f'weechat:{tag}{suffix}')
    return tags_args


def main():
    """Main function."""
    args = get_parser().parse_args()
    slim = ['--build-arg', 'SLIM=1'] if args.slim else []
    tags = get_tags_args(args.version, args.distro, args.slim)
    command = [
        f'{args.builder}',
        'build',
        '-f', f'{args.distro}/Containerfile',
        '--build-arg', f'VERSION={args.version}',
        *slim,
        *tags,
        '.',
    ]
    print(f'Running: {" ".join(command)}')
    if not args.dry_run:
        try:
            subprocess.run(command, check=False)
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
