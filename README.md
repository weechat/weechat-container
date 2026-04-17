<!--
SPDX-FileCopyrightText: 2021-2025 Sébastien Helleu <flashcode@flashtux.org>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Containerized WeeChat

[![Build Status](https://github.com/weechat/weechat-container/workflows/CI/badge.svg)](https://github.com/weechat/weechat-container/actions?query=workflow%3A%22CI%22)
[![REUSE status](https://api.reuse.software/badge/github.com/weechat/weechat-container)](https://api.reuse.software/info/github.com/weechat/weechat-container)

Build of WeeChat images using [Docker](https://www.docker.com/) (default) or [Podman](https://podman.io/).

## Requirements

The following packages are required to build images:

- Docker or Podman

Optional dependencies:

- Python ≥ 3.6 if you use the provided Makefile or build.py script

## Image types

Images are based on Debian or Alpine (smaller size, with same features):

- Debian:
  - `debian` (~ 327 MB)
  - `debian-slim`: slim version (~ 125 MB)
- Alpine:
  - `alpine` (~ 217 MB)
  - `alpine-slim`: slim version (~ 41 MB)

The slim version includes all plugins except these ones:

- script manager (command `/script`)
- scripting languages: perl, python, ruby, lua, tcl, guile, php
- spell

## Install and run with Docker Hub

You can install and run directly the latest version from the [Docker Hub](https://hub.docker.com/r/weechat/weechat):

```bash
docker run -it weechat/weechat
```

Or the Alpine version:

```bash
docker run -it weechat/weechat:latest-alpine
```

For a specific WeeChat version (Debian):

```bash
docker run -it weechat/weechat:4.3.2
```

Run with custom home directories on host to persist data (WeeChat ≥ 3.2, using XDG directories):

```bash
mkdir -p ~/.weechat-container/config ~/.weechat-container/data ~/.weechat-container/cache
chmod 777 ~/.weechat-container/config ~/.weechat-container/data ~/.weechat-container/cache
docker run -it -v $HOME/.weechat-container/config:/home/user/.config/weechat -v $HOME/.weechat-container/data:/home/user/.local/share/weechat -v $HOME/.weechat-container/cache:/home/user/.cache/weechat weechat/weechat
```

Run with a custom single home directory on host to persist data (any WeeChat version):

```bash
mkdir -p ~/.weechat-container
chmod 777 ~/.weechat-container
docker run -it -v $HOME/.weechat-container:/home/user/.weechat weechat/weechat weechat -d /home/user/.weechat
```

## Build

A Makefile is provided and supports these variables:

- `BUILDER`: the tool to build the image: `docker`, `podman` or any equivalent tool (default is `docker`)
- `VERSION`: the WeeChat version to build (default is `latest` which is the latest stable version, use `devel` for development version, which is built every day).

Build a Debian-based image with latest stable version of WeeChat:

```bash
make debian
```

Build all images with latest stable version of WeeChat:

```bash
make all-images
```

Build an Alpine-based image with Podman, slim version, WeeChat 4.3.2:

```bash
make BUILDER=podman VERSION=4.3.2 alpine-slim
```

Build a Debian-based image with WeeChat 4.3.2, directly with docker:

```bash
docker build -f debian/Containerfile --build-arg VERSION=4.3.2 .
```

## Update image

To update your existing WeeChat container to a newer image version:

**Pull the latest image:**

```bash
docker pull weechat/weechat:latest
```

Or for Alpine:

```bash
docker pull weechat/weechat:latest-alpine
```

**Recreate the container** (preserving your persistent data):

If you used persistent volumes (recommended):

```bash
docker stop weechat
docker rm weechat
docker run -it -v $HOME/.weechat-container/config:/home/user/.config/weechat \
  -v $HOME/.weechat-container/data:/home/user/.local/share/weechat \
  -v $HOME/.weechat-container/cache:/home/user/.cache/weechat \
  weechat/weechat:latest
```

If you used a single home directory:

```bash
docker stop weechat
docker rm weechat
docker run -it -v $HOME/.weechat-container:/home/user/.weechat \
  weechat/weechat:latest weechat -d /home/user/.weechat
```

**Remove the old image** (after verifying the new container works):

```bash
docker image prune -f
```

Or to remove only the specific old WeeChat image:

```bash
docker images | grep weechat/weechat
docker rmi <old-image-id>
```

**Note:** Your WeeChat configuration, logs, and scripts are preserved as long as you use volume mounts. Always ensure you have backups before updating. The old image will continue taking disk space until pruned.

## Copyright

<!-- REUSE-IgnoreStart -->
Copyright © 2021-2025 [Sébastien Helleu](https://github.com/flashcode)

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
<!-- REUSE-IgnoreEnd -->
