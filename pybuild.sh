#!/bin/bash
set -ex
apt-get update \
 && mk-build-deps -i debian/control -t 'apt-get --no-install-recommends -y --force-yes'
python -m mirbuild.walk -p python-mirbuild package
