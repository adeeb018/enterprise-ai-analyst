#!/bin/bash
set -e

echo "Creating MIMIC-IV schema..."

docker cp mimic-code/mimic-iv/buildmimic/postgres/create.sql \
enterprise-postgres:/tmp/create.sql

docker exec -i enterprise-postgres \
psql -U postgres -d enterprise_ai \
-f /tmp/create.sql

echo "Schema created successfully."