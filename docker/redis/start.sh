#!/bin/sh
set -eu
umask 077
# Keep the password out of process arguments.
printf 'bind 0.0.0.0\nprotected-mode yes\nport 6379\nsave ""\nappendonly no\nrequirepass %s\n' \
  "$(cat /run/secrets/redis_password)" > /tmp/redis.conf
exec redis-server /tmp/redis.conf
