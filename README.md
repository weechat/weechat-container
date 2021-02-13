# Containerized WeeChat

Build of WeeChat in container, using [Docker](https://www.docker.com/) (default) or [Podman](https://podman.io/).

## Requirements

The following packages are required to build containers:

- Docker or Podman

Optional dependencies:

- Python ≥ 3.6 if you use the provided Makefile or build.py script

## Build

Containers are based on Debian or Alpine (smaller size, with same features):

- Debian Buster:
  - `debian` (~ 300 MB)
  - `debian-slim`: slim version (~ 110 MB)
- Alpine 3.13:
  - `alpine` (~ 150 MB)
  - `alpine-slim`: slim version (~ 30 MB)

The slim version includes all plugins except these ones:

- script manager (command `/script`)
- scripting languages: perl, python, ruby, lua, tcl, guile, php
- spell

Example:

```
$ make debian
```

Supported make variables:

- `BUILDER`: the tool to build the image: `docker`, `podman` or any equivalent tool (default is `docker`)
- `VERSION`: the WeeChat version to build (default is `latest` which is the latest stable version, use `devel` for development version, which is built every day).

For example, to build the slim container running Alpine and WeeChat 2.9, with Podman:

```
$ make BUILDER=podman VERSION=2.9 alpine-slim
```

## Copyright

Copyright © 2021 [Sébastien Helleu](https://github.com/flashcode)

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