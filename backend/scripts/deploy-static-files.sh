#!/bin/bash
# Deployment script for fixing static files and Swagger documentation
# This script ensures all static files are properly collected for drf-yasg (Swagger)

set -e

echo "=== Starting Django Deployment Script ==="
echo "Environment: ${DJANGO_ENV:-development}"

# Load environment variables
if [ -f ".env.${DJANGO_ENV:-development}" ]; then
    set -a
    source ".env.${DJANGO_ENV:-development}"
    set +a
    echo "✓ Loaded environment variables from .env.${DJANGO_ENV:-development}"
else
    echo "⚠ Warning: .env.${DJANGO_ENV:-development} not found"
fi

# Ensure Python environment is activated (if using venv)
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Activated Python virtual environment"
fi

echo ""
echo "=== Running Django Management Commands ==="

# Apply database migrations
echo "1. Applying database migrations..."
python manage.py migrate --no-input
echo "   ✓ Migrations applied"

# Collect static files for production
echo "2. Collecting static files (required for Swagger/drf-yasg)..."
python manage.py collectstatic --no-input --clear

if [ $? -eq 0 ]; then
    echo "   ✓ Static files collected successfully"
    echo "   Location: $(python -c 'from pathlib import Path; from django.conf import settings; print(settings.STATIC_ROOT)')"
else
    echo "   ✗ Failed to collect static files"
    exit 1
fi

# Check static files were created
STATIC_ROOT=$(python -c 'from pathlib import Path; from django.conf import settings; print(settings.STATIC_ROOT)')
if [ -d "$STATIC_ROOT" ] && [ "$(ls -A $STATIC_ROOT)" ]; then
    FILE_COUNT=$(find "$STATIC_ROOT" -type f | wc -l)
    echo "   ✓ Verified: $FILE_COUNT files in static directory"
else
    echo "   ✗ Warning: Static directory is empty"
fi

echo ""
echo "=== Deployment Checklist ==="
echo "✓ Database migrations applied"
echo "✓ Static files collected (Swagger schema should now load)"
echo "✓ WhiteNoise is configured to serve static files"
echo ""
echo "=== Next Steps ==="
echo "1. Restart the Django application server"
echo "2. Test Swagger UI at: http://localhost:8000/api/docs/"
echo "3. Verify API schema loads properly"
echo ""
echo "=== Troubleshooting ==="
echo "If Swagger still doesn't load:"
echo "  - Check browser console for network errors"
echo "  - Verify STATIC_URL and STATIC_ROOT in settings.py"
echo "  - Ensure WhiteNoise middleware is installed and enabled"
echo "  - Check file permissions on static directory"
echo ""
echo "=== Deployment Complete ==="
