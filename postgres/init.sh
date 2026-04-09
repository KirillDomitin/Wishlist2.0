#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER user_svc WITH PASSWORD '$DB_USER_SVC_PASSWORD';
    CREATE USER wishlist_svc WITH PASSWORD '$DB_WISHLIST_SVC_PASSWORD';
    CREATE USER reserv_svc WITH PASSWORD '$DB_RESERV_SVC_PASSWORD';

    CREATE DATABASE user_db OWNER user_svc;
    CREATE DATABASE wishlist_db OWNER wishlist_svc;
    CREATE DATABASE reserv_db OWNER reserv_svc;
EOSQL
