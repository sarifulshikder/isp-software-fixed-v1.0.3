FROM alpine:3.19

LABEL maintainer="ISP Software Team"

RUN apk add --no-cache \
    freeradius \
    freeradius-postgresql \
    freeradius-utils \
    postgresql-client \
    tzdata \
    && cp /usr/share/zoneinfo/Asia/Dhaka /etc/localtime \
    && echo "Asia/Dhaka" > /etc/timezone

# Overlay only the config files we ship (e.g. clients.conf and any
# customised modules under mods-config). The rest of /etc/raddb keeps the
# distro defaults so FreeRADIUS can still find sites/mods/dictionaries.
COPY config/ /etc/raddb/

EXPOSE 1812/udp 1813/udp 1814/tcp

# Use radiusd's own self-test as the health check; radtest needs a live
# user which we don't provision by default.
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD radiusd -XC > /dev/null 2>&1 || exit 1

CMD ["radiusd", "-f", "-l", "stdout"]
