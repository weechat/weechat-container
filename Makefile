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

BUILDER ?= "docker"
VERSION ?= "latest"

.PHONY: all debian debian-slim alpine alpine-slim

all: debian debian-slim alpine alpine-slim

debian:
	./build.py -b "$(BUILDER)" -d "debian" "$(VERSION)"

debian-slim:
	./build.py -b "$(BUILDER)" -d "debian" --slim "$(VERSION)"

alpine:
	./build.py -b "$(BUILDER)" -d "alpine" "$(VERSION)"

alpine-slim:
	./build.py -b "$(BUILDER)" -d "alpine" --slim "$(VERSION)"
