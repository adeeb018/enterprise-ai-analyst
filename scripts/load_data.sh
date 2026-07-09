#!/bin/bash
set -e

echo "Loading MIMIC-IV data..."

docker cp data/mimic/mimic-iv-clinical-database-demo-2.2 \
enterprise-postgres:/mimic

docker cp mimic-code/mimic-iv/buildmimic/postgres/load_gz.sql \
enterprise-postgres:/tmp/load_gz.sql

docker exec -i enterprise-postgres \
psql -U postgres \
-d enterprise_ai \
-v mimic_data_dir=/mimic \
-f /tmp/load_gz.sql

echo "Data loaded successfully."