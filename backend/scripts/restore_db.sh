#!/bin/bash

#==============================================================================
# PostgreSQL Database Restore Script
#==============================================================================
# This script restores a PostgreSQL database from a backup file.
#
# Usage: ./restore_db.sh <backup_file>
# Example: ./restore_db.sh ../backups/backup_ptb_ot_20260109_143000.sql.gz
#==============================================================================

set -e  # Exit on error

# Load environment variables
if [ -f "../.env.dev" ]; then
    export $(cat ../.env.dev | grep -v '^#' | xargs)
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backup file is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Backup file not specified${NC}"
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 ../backups/backup_ptb_ot_20260109_143000.sql.gz"
    
    # List available backups
    echo ""
    echo -e "${YELLOW}Available backups:${NC}"
    ls -lht ../backups/backup_*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "${BACKUP_FILE}" ]; then
    echo -e "${RED}Error: Backup file not found: ${BACKUP_FILE}${NC}"
    exit 1
fi

# Confirm restoration
echo -e "${YELLOW}WARNING: This will REPLACE the current database!${NC}"
echo "Database: ${SQL_DATABASE}"
echo "Host: ${SQL_HOST}:${SQL_PORT}"
echo "Backup file: ${BACKUP_FILE}"
echo ""
read -p "Are you sure you want to continue? (yes/no): " -r
echo

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo -e "${YELLOW}Restore cancelled${NC}"
    exit 0
fi

# Create a backup of current database before restoring
echo -e "${YELLOW}Creating safety backup of current database...${NC}"
SAFETY_BACKUP="../backups/pre_restore_backup_$(date +"%Y%m%d_%H%M%S").sql.gz"
PGPASSWORD="${SQL_PASSWORD}" pg_dump \
    -h "${SQL_HOST}" \
    -p "${SQL_PORT}" \
    -U "${SQL_USER}" \
    -d "${SQL_DATABASE}" \
    -F p \
    --no-owner \
    --no-acl \
    | gzip > "${SAFETY_BACKUP}"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Safety backup created: ${SAFETY_BACKUP}${NC}"
else
    echo -e "${RED}✗ Failed to create safety backup${NC}"
    exit 1
fi

# Drop and recreate database
echo -e "${YELLOW}Dropping database...${NC}"
PGPASSWORD="${SQL_PASSWORD}" dropdb \
    -h "${SQL_HOST}" \
    -p "${SQL_PORT}" \
    -U "${SQL_USER}" \
    --if-exists \
    "${SQL_DATABASE}"

echo -e "${YELLOW}Creating database...${NC}"
PGPASSWORD="${SQL_PASSWORD}" createdb \
    -h "${SQL_HOST}" \
    -p "${SQL_PORT}" \
    -U "${SQL_USER}" \
    "${SQL_DATABASE}"

# Restore from backup
echo -e "${YELLOW}Restoring database from backup...${NC}"

if [[ "${BACKUP_FILE}" == *.gz ]]; then
    # Decompress and restore
    gunzip -c "${BACKUP_FILE}" | PGPASSWORD="${SQL_PASSWORD}" psql \
        -h "${SQL_HOST}" \
        -p "${SQL_PORT}" \
        -U "${SQL_USER}" \
        -d "${SQL_DATABASE}" \
        --quiet
else
    # Restore directly
    PGPASSWORD="${SQL_PASSWORD}" psql \
        -h "${SQL_HOST}" \
        -p "${SQL_PORT}" \
        -U "${SQL_USER}" \
        -d "${SQL_DATABASE}" \
        --quiet \
        < "${BACKUP_FILE}"
fi

# Check if restore was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database restored successfully!${NC}"
    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo "1. Run migrations: python manage.py migrate"
    echo "2. Create superuser: python manage.py createsuperuser"
    echo "3. Verify data integrity"
    echo ""
    echo -e "${YELLOW}Safety backup location: ${SAFETY_BACKUP}${NC}"
    exit 0
else
    echo -e "${RED}✗ Database restore failed${NC}"
    echo -e "${YELLOW}Rolling back to safety backup...${NC}"
    
    # Restore from safety backup
    gunzip -c "${SAFETY_BACKUP}" | PGPASSWORD="${SQL_PASSWORD}" psql \
        -h "${SQL_HOST}" \
        -p "${SQL_PORT}" \
        -U "${SQL_USER}" \
        -d "${SQL_DATABASE}" \
        --quiet
    
    echo -e "${GREEN}✓ Rolled back to safety backup${NC}"
    exit 1
fi
