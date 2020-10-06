FROM gcr.io/i-lastfm-tools/ubuntu-trusty-buildenv AS build-stage

WORKDIR /app-src

COPY debian/control /app-src/debian/control
RUN apt-get update \
 && mk-build-deps -i debian/control -t 'apt-get --no-install-recommends -y --force-yes'

COPY . /app-src
RUN python -m mirbuild.walk -p python-mirbuild package

FROM scratch AS export-stage
COPY --from=build-stage /lastfm* /
