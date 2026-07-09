#!/bin/bash
set -e

echo "Adding constraints..."

docker cp mimic-code/mimic-iv/buildmimic/postgres/constraint.sql \
enterprise-postgres:/tmp/constraint.sql

docker exec -i enterprise-postgres \
psql -U postgres -d enterprise_ai \
-f /tmp/constraint.sql

echo "Constraints added successfully."