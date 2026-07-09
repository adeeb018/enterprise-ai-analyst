#!/bin/bash
set -e

echo "Creating indexes..."

docker cp mimic-code/mimic-iv/buildmimic/postgres/index.sql \
enterprise-postgres:/tmp/index.sql

docker exec -i enterprise-postgres \
psql -U postgres -d enterprise_ai \
-f /tmp/index.sql

echo "Indexes created successfully."