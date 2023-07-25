#!/bin/sh
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER "eas-user";
	CREATE DATABASE emergency_alerts;
	GRANT ALL PRIVILEGES ON DATABASE emergency_alerts TO "eas-user";
EOSQL
