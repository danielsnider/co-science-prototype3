#
# Cos-Base Dockerfile
#
# https://github.com/danielsnider
#

FROM cos-base:latest
MAINTAINER Daniel Snider<danielsnider12@gmail.com>

# Install COS Package
COPY packages /cos_packages/

ENTRYPOINT cos
