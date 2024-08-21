#!/bin/bash
# wait-for-postgres.sh

set -e

host="$DB_HOST"
port="$DB_PORT"

until nc -z "$host" "$port"; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"

flask db init || true
flask db migrate -m "Initial migration" || true
flask db upgrade || true
exec "$@"
