ARG BEANSTALKD_VERSION=1.12

FROM gcc:10 as build

ARG BEANSTALKD_VERSION

ADD https://github.com/beanstalkd/beanstalkd/archive/v$BEANSTALKD_VERSION.tar.gz /beanstalkd.tgz

WORKDIR /beanstalkd

RUN tar xvfz /beanstalkd.tgz 

WORKDIR /beanstalkd/beanstalkd-$BEANSTALKD_VERSION

RUN make

RUN cp beanstalkd /beanstalkd-bin \
    && chmod 555 /beanstalkd-bin

RUN mkdir /data

FROM gcr.io/distroless/base:nonroot

COPY --from=build --chown=nonroot:nonroot /beanstalkd-bin /beanstalkd

VOLUME /data

# Copy empty directory to /data and /config volumes
# to fix permissions until this is fixed:
# https://github.com/moby/moby/issues/2259
COPY --chown=nonroot:nonroot --from=build /data /data

ENTRYPOINT [ "/beanstalkd" ]

EXPOSE 11300