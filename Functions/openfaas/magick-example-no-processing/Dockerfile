FROM ghcr.io/openfaas/classic-watchdog:0.1.5 as watchdog

FROM alpine:3.12

RUN mkdir -p /home/app

COPY --from=watchdog /fwatchdog /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog

# Add non root user
RUN addgroup -S app && adduser app -S -G app
RUN chown app /home/app

WORKDIR /home/app

#USER app

# Populate example here - i.e. "cat", "sha512sum" or "node index.js"
#USER root

RUN apk update

RUN apk upgrade

RUN apk add curl tar file xz alpine-sdk imagemagick imagemagick-dev jpeg-dev libpng-dev

RUN rm -rf /var/cache/apk/*

USER app

COPY example.cpp .

RUN export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig

RUN c++ `Magick++-config --cxxflags --cppflags` -O2 -o example example.cpp `Magick++-config --ldflags --libs`

ENV fprocess="./example"
# Set to true to see request in function logs
ENV write_debug="false"

EXPOSE 8080

HEALTHCHECK --interval=3s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]
