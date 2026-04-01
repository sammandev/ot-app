#!/bin/bash
# Comprehensive Bug Fix Script - January 12, 2026
# This script identifies and fixes the issues found in backend-logs4

echo "====================================="
echo "FTP OT App - Bug Fix & Diagnosis"
echo "====================================="
echo ""

# Navigate to backend
cd backend

echo "STEP 1: Check Migration Status"
echo "=============================="
python manage.py showmigrations api
echo ""

echo "STEP 2: Check for Corrupted OvertimeRequest Data"
echo "================================================"
python manage.py dbshell << EOF
SELECT COUNT(*) as corrupt_records FROM api_overtimerequest 
WHERE employee_id NOT IN (SELECT id FROM api_employee) 
OR employee_id IS NULL 
OR employee_id = '';
EOF
echo ""

echo "STEP 3: Display Corrupted Records (if any)"
echo "========================================="
python manage.py dbshell << EOF
SELECT id, employee_id, employee_name, project_id, request_date 
FROM api_overtimerequest 
WHERE employee_id NOT IN (SELECT id FROM api_employee) 
LIMIT 10;
EOF
echo ""

echo "STEP 4: Apply Pending Migrations"
echo "==============================="
python manage.py migrate
echo ""

echo "STEP 5: Verify CalendarEvent Configuration"
echo "=========================================="
python manage.py dbshell << EOF
SELECT COUNT(*) as total_calendar_events FROM api_calendarevent;
SELECT COUNT(*) as calendar_events_with_issues 
FROM api_calendarevent 
WHERE created_by_id NOT IN (SELECT id FROM api_externaluser) 
OR leave_type_id NOT IN (SELECT id FROM api_leavetype);
EOF
echo ""

echo "STEP 6: Test OT Request Query"
echo "============================"
python manage.py shell << EOF
from api.models import OvertimeRequest, Employee
from django.db.models import Q

# Check total OT requests
total = OvertimeRequest.objects.count()
print(f"Total OT Requests: {total}")

# Check for issues
try:
    # This will trigger the error if corrupt data exists
    requests = OvertimeRequest.objects.filter(
        Q(employee__isnull=False) & Q(employee_id__isnull=False)
    ).select_related('employee')[:10]
    
    for req in requests:
        print(f"ID: {req.id}, Employee: {req.employee.name if req.employee else 'NONE'}")
except Exception as e:
    print(f"Error accessing OT requests: {e}")
EOF
echo ""

echo "====================================="
echo "Bug Analysis Complete"
echo "====================================="
echo ""
echo "RECOMMENDATIONS:"
echo "1. If corrupted records found in STEP 2, run cleanup-corrupted-data.sql"
echo "2. If migrations failed in STEP 4, check migration files"
echo "3. If calendar event issues in STEP 5, update CalendarEvent records"
echo "4. Run backend tests to verify no regressions"
echo ""
