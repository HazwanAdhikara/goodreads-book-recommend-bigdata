#!/bin/bash
echo "Waiting for PostgreSQL to be ready..."
# Simple wait for PostgreSQL port to be available
until nc -z postgres 5432; do
    echo "Waiting for PostgreSQL..."
    sleep 5
done

echo "PostgreSQL is ready. Starting Hive Metastore..."

# Try to initialize schema (it will skip if already exists)
echo "Initializing schema..."
$HIVE_HOME/bin/schematool -dbType postgres -initSchema || echo "Schema may already exist, continuing..."

exec "$@"
