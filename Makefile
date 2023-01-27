#
# Copyright (C) 2021-2023 Sébastien Helleu <flashcode@flashtux.org>
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

BUILDER ?= docker
PLATFORMS ?= linux/amd64
VERSION ?= latest
IMAGE ?= weechat
REGISTRY ?= docker.io
REGISTRY_PROJECT ?= weechat
REGISTRY_PROJECT_URL = $(REGISTRY)/$(REGISTRY_PROJECT)
REGISTRY_IMAGE = $(REGISTRY_PROJECT_URL)/$(IMAGE)

ALPINE_BASE_IMAGE = alpine:3.15
DEBIAN_BASE_IMAGE = debian:bullseye-slim

ifeq ($(strip $(PUSH)),true)
PUSH_ARG = "--push"
endif

.PHONY: all debian debian-slim alpine alpine-slim

all: debian

all-images: debian debian-slim alpine alpine-slim

debian: weechat-multiarch
	./build.py -b "$(BUILDER)" -p $(PLATFORMS) -r "$(REGISTRY_PROJECT_URL)" $(PUSH_ARG)  -d "debian" "$(VERSION)"

debian-slim: weechat-multiarch
	./build.py -b "$(BUILDER)" -p $(PLATFORMS) -r "$(REGISTRY_PROJECT_URL)" $(PUSH_ARG) -d "debian" --slim "$(VERSION)"

alpine: weechat-multiarch
	./build.py -b "$(BUILDER)" -p $(PLATFORMS) -r "$(REGISTRY_PROJECT_URL)" $(PUSH_ARG) -d "alpine" "$(VERSION)"

alpine-slim: weechat-multiarch
	./build.py -b "$(BUILDER)" -p $(PLATFORMS) -r "$(REGISTRY_PROJECT_URL)" $(PUSH_ARG) -d "alpine" --slim "$(VERSION)"

weechat-multiarch:
	if [ "$(BUILDER)" == "docker" ]; then \
		docker buildx ls | grep weechat-multiarch || docker buildx create --name weechat-multiarch ; \
		docker buildx use weechat-multiarch; \
	fi

test-images:
	for PLATFORM in $(PLATFORMS); do \
		for TAG in $(VERSION)-{debian,alpine}{,-slim}; do \
			REGISTRY_IMAGE_TAG=$(REGISTRY_IMAGE):$$TAG; \
			echo "Testing $$REGISTRY_IMAGE_TAG for $$PLATFORM platform" ; \
			$(BUILDER) pull --platform $$PLATFORM $$REGISTRY_IMAGE_TAG &>/dev/null; \
			echo -n "weechat --version: "; \
			$(BUILDER) run --rm --platform $$PLATFORM $$REGISTRY_IMAGE_TAG --version; \
			echo -n "weechat-headless --version: "; \
			$(BUILDER) run --rm --platform $$PLATFORM --entrypoint /usr/bin/weechat-headless $$REGISTRY_IMAGE_TAG --version ; \
			$(BUILDER) rmi $$REGISTRY_IMAGE_TAG &>/dev/null; \
	  done; \
	done

clean-images:
	if [ "$(BUILDER)" == "podman" ]; then \
		buildah rm --all; \
		$(BUILDER) images --format="{{.Repository}}:{{.Tag}}" localhost/$(IMAGE) | xargs --no-run-if-empty $(BUILDER) rmi -f; \
		$(BUILDER) images --format="{{.Repository}}:{{.Tag}}" $(REGISTRY_PROJECT)/$(IMAGE) | xargs --no-run-if-empty $(BUILDER) rmi -f; \
		$(BUILDER) images --format="{{.Repository}}:{{.Tag}}" $(ALPINE_BASE_IMAGE) | xargs --no-run-if-empty $(BUILDER) rmi -f; \
		$(BUILDER) images --format="{{.Repository}}:{{.Tag}}" $(DEBIAN_BASE_IMAGE) | xargs --no-run-if-empty $(BUILDER) rmi -f; \
		$(BUILDER) image prune -f; \
	fi
	if [ "$(BUILDER)" == "docker" ]; then \
		$(BUILDER) buildx rm weechat-multiarch; \
		$(BUILDER) rmi moby/buildkit:buildx-stable-1
	fi
	
lint: flake8 pylint mypy bandit

flake8:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --statistics

pylint:
	pylint build.py

mypy:
	mypy --strict build.py

bandit:
	bandit build.py
