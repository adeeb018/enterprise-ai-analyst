#!/bin/bash
set -e

echo "===== Setting up MIMIC-IV Database ====="

./scripts/create_schema.sh
./scripts/load_data.sh
./scripts/add_constraints.sh
./scripts/create_indexes.sh

echo "===== Database setup completed ====="