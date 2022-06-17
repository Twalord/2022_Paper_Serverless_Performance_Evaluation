ARG NUCLIO_LABEL=1.6.26
ARG NUCLIO_ARCH=amd64
ARG NUCLIO_BASE_IMAGE=alpine:3.13
ARG NUCLIO_ONBUILD_IMAGE=quay.io/nuclio/handler-builder-golang-onbuild:${NUCLIO_LABEL}-${NUCLIO_ARCH}-alpine

# Supplies processor uhttpc, used for healthcheck
FROM quay.io/nuclio/uhttpc:0.0.1-amd64 as uhttpc

# Builds source, supplies processor binary and handler plugin
FROM ${NUCLIO_ONBUILD_IMAGE} as builder

# Keep the Builder as base image to not install dependencies twice
FROM ${NUCLIO_BASE_IMAGE}

# Copy required objects from the suppliers
COPY --from=builder /home/nuclio/bin/processor /usr/local/bin/processor
COPY --from=builder /home/nuclio/bin/handler.so /opt/nuclio/handler.so
COPY --from=uhttpc /home/nuclio/bin/uhttpc /usr/local/bin/uhttpc

# Readiness probe
HEALTHCHECK --interval=1s --timeout=3s CMD /usr/local/bin/uhttpc --url http://127.0.0.1:8082/ready || exit 1

# Run processor with configuration and platform configuration
CMD [ "processor" ]
