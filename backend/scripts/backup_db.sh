#!/bin/bash

#==============================================================================
# PostgreSQL Database Backup Script
#==============================================================================
# This script creates a backup of the PostgreSQL database
# with timestamp and stores it in the backups directory.
#
# Usage: ./backup_db.sh
#==============================================================================

set -e  # Exit on error

# Load environment variables
if [ -f "../.env.dev" ]; then
    export $(cat ../.env.dev | grep -v '^#' | xargs)
fi

# Configuration
BACKUP_DIR="../backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/backup_${SQL_DATABASE}_${TIMESTAMP}.sql"
COMPRESSED_FILE="${BACKUP_FILE}.gz"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

echo -e "${YELLOW}Starting database backup...${NC}"
echo "Database: ${SQL_DATABASE}"
echo "Host: ${SQL_HOST}:${SQL_PORT}"
echo "Backup file: ${COMPRESSED_FILE}"

# Create backup using pg_dump
PGPASSWORD="${SQL_PASSWORD}" pg_dump \
    -h "${SQL_HOST}" \
    -p "${SQL_PORT}" \
    -U "${SQL_USER}" \
    -d "${SQL_DATABASE}" \
    -F p \
    --verbose \
    --no-owner \
    --no-acl \
    > "${BACKUP_FILE}"

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database dump created successfully${NC}"
    
    # Compress the backup
    echo -e "${YELLOW}Compressing backup...${NC}"
    gzip "${BACKUP_FILE}"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Backup compressed successfully${NC}"
        
        # Get file size
        FILE_SIZE=$(du -h "${COMPRESSED_FILE}" | cut -f1)
        echo -e "${GREEN}Backup size: ${FILE_SIZE}${NC}"
        echo -e "${GREEN}Backup location: ${COMPRESSED_FILE}${NC}"
        
        # Delete backups older than 30 days
        echo -e "${YELLOW}Cleaning up old backups (older than 30 days)...${NC}"
        find "${BACKUP_DIR}" -name "backup_*.sql.gz" -type f -mtime +30 -delete
        
        # Count remaining backups
        BACKUP_COUNT=$(find "${BACKUP_DIR}" -name "backup_*.sql.gz" -type f | wc -l)
        echo -e "${GREEN}Total backups: ${BACKUP_COUNT}${NC}"
        
        echo -e "${GREEN}✓ Backup completed successfully!${NC}"
        exit 0
    else
        echo -e "${RED}✗ Failed to compress backup${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Database backup failed${NC}"
    exit 1
fi
