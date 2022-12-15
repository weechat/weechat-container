# Containerized WeeChat

[![Build Status](https://github.com/weechat/weechat-container/workflows/CI/badge.svg)](https://github.com/weechat/weechat-container/actions?query=workflow%3A%22CI%22)

Build of WeeChat images using [Docker](https://www.docker.com/) (default) or [Podman](https://podman.io/).

## Requirements

The following packages are required to build images:

- Docker or Podman

Optional dependencies:

- Python ≥ 3.6 if you use the provided Makefile or build.py script

## Image types

Images are based on Debian or Alpine (smaller size, with same features):

- Debian Bullseye:
  - `debian` (~ 300 MB)
  - `debian-slim`: slim version (~ 110 MB)
- Alpine 3.15:
  - `alpine` (~ 150 MB)
  - `alpine-slim`: slim version (~ 30 MB)

The slim version includes all plugins except these ones:

- script manager (command `/script`)
- scripting languages: perl, python, ruby, lua, tcl, guile, php
- spell

## Supported platforms

It's possible to build for different linux platforms other than amd64,
the only prerequisite is to have `qemu-user-static` package installed

- `linux/386`
- `linux/amd64`
- `linux/arm/v6`
- `linux/arm/v7`
- `linux/arm64`
- `linux/ppc64le`
- `linux/s390x`


## Install from Docker Hub

You can install directly the latest version from the Docker Hub:

```
$ docker run -ti weechat/weechat
```

Or the Alpine version:

```
$ docker run -ti weechat/weechat:latest-alpine
```

For a specific WeeChat version (Debian):

```
$ docker run -ti weechat/weechat:3.6
```

Images on the official Docker Hub: [https://hub.docker.com/r/weechat/weechat](https://hub.docker.com/r/weechat/weechat)

## Build

A Makefile is provided and supports these variables:

- `BUILDER`: the tool to build the image: `docker`, `podman` or any equivalent tool (default is `docker`)
- `VERSION`: the WeeChat version to build (default is `latest` which is the latest stable version, use `devel` for development version, which is built every day).

Build a Debian-based image with latest stable version of WeeChat:

```
$ make debian
```

Build all images with latest stable version of WeeChat:

```
$ make all-images
```

Build all images with latest stable version of WeeChat for AMD64 and ARM64 platforms
and push them to the `docker.io/weechat` registry project:

```
$ make PLATFORMS="linux/amd64 linux/arm64" REGISTRY="docker.io" REGISTRY_PROJECT="weechat" PUSH=true all-images
```

Build an Alpine-based image with Podman, slim version, WeeChat 3.6:

```
$ make BUILDER=podman VERSION=3.6 alpine-slim
```

Build a Debian-based image with WeeChat 3.6, directly with docker:

```
$ docker build -f debian/Containerfile --build-arg VERSION=3.6 .
```

## Run

Run latest WeeChat version in Debian container:

```
docker run -ti weechat
```

Run with custom home directories on host to persist data (WeeChat ≥ 3.2, using XDG directories):

```
mkdir -p ~/.weechat-container/config ~/.weechat-container/data ~/.weechat-container/cache
docker run -ti -v $HOME/.weechat-container/config:/home/user/.config/weechat -v $HOME/.weechat-container/data:/home/user/.local/share/weechat -v $HOME/.weechat-container/cache:/home/user/.cache/weechat weechat
```

Run with a custom single home directory on host to persist data (any WeeChat version):

```
mkdir -p ~/.weechat-container
docker run -ti -v $HOME/.weechat-container:/home/user/.weechat weechat -d /home/user/.weechat
```

## Copyright

Copyright © 2021-2022 [Sébastien Helleu](https://github.com/flashcode)

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
