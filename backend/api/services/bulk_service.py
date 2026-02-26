"""
Bulk import/export service for CSV operations.
"""

import csv
import io
import logging
from typing import Any

from django.db import transaction
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)


class BulkImportExportService:
    """Service for handling bulk CSV import/export operations."""

    @staticmethod
    def export_to_csv(queryset, fields: list[str], filename: str = "export.csv") -> io.StringIO:
        """
        Export queryset to CSV format.

        Args:
            queryset: Django queryset to export
            fields: List of field names to include in export
            filename: Name for the exported file

        Returns:
            StringIO object containing CSV data
        """
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()

        for obj in queryset:
            row = {}
            for field in fields:
                # Handle nested field access (e.g., 'employee.name')
                if "." in field:
                    parts = field.split(".")
                    value = obj
                    for part in parts:
                        value = getattr(value, part, "")
                        if value is None:
                            value = ""
                    row[field] = value
                else:
                    value = getattr(obj, field, "")
                    row[field] = "" if value is None else value
            writer.writerow(row)

        output.seek(0)
        return output

    @staticmethod
    def import_from_csv(file_obj, serializer_class, max_rows: int = 1000, update_existing: bool = False, lookup_field: str = "id") -> dict[str, Any]:
        """
        Import data from CSV file.

        Args:
            file_obj: Uploaded CSV file
            serializer_class: Serializer class to use for validation
            max_rows: Maximum number of rows to import
            update_existing: Whether to update existing records or create only
            lookup_field: Field to use for finding existing records

        Returns:
            Dict with import results (created, updated, errors)
        """
        results = {"created": 0, "updated": 0, "errors": [], "total_rows": 0}

        try:
            # Decode file content
            content = file_obj.read().decode("utf-8")
            csv_file = io.StringIO(content)
            reader = csv.DictReader(csv_file)

            rows = list(reader)
            results["total_rows"] = len(rows)

            if len(rows) > max_rows:
                raise ValidationError(f"Too many rows. Maximum allowed: {max_rows}, provided: {len(rows)}")

            # Process rows in transaction
            with transaction.atomic():
                for row_num, row in enumerate(rows, start=2):  # Start at 2 (1 is header)
                    try:
                        # Clean empty strings to None
                        cleaned_row = {k: (None if v == "" else v) for k, v in row.items()}

                        # Check if record exists
                        instance = None
                        if update_existing and lookup_field in cleaned_row:
                            lookup_value = cleaned_row.get(lookup_field)
                            if lookup_value:
                                try:
                                    Model = serializer_class.Meta.model
                                    instance = Model.objects.get(**{lookup_field: lookup_value})
                                except Model.DoesNotExist:
                                    pass

                        # Create or update
                        serializer = serializer_class(instance=instance, data=cleaned_row, partial=update_existing)

                        if serializer.is_valid():
                            serializer.save()
                            if instance:
                                results["updated"] += 1
                            else:
                                results["created"] += 1
                        else:
                            results["errors"].append({"row": row_num, "data": row, "errors": serializer.errors})

                    except Exception as e:
                        logger.error(f"Error importing row {row_num}: {str(e)}")
                        results["errors"].append({"row": row_num, "data": row, "errors": str(e)})

                # Rollback if there are too many errors
                error_rate = len(results["errors"]) / results["total_rows"] if results["total_rows"] > 0 else 0
                if error_rate > 0.1:  # More than 10% errors
                    raise ValidationError(f"Import failed: {len(results['errors'])} errors out of {results['total_rows']} rows")

        except Exception as e:
            logger.error(f"CSV import failed: {str(e)}")
            raise

        return results

    @staticmethod
    def validate_csv_headers(file_obj, required_fields: list[str]) -> dict[str, Any]:
        """
        Validate CSV file headers.

        Args:
            file_obj: Uploaded CSV file
            required_fields: List of required field names

        Returns:
            Dict with validation results
        """
        try:
            content = file_obj.read().decode("utf-8")
            file_obj.seek(0)  # Reset file pointer

            csv_file = io.StringIO(content)
            reader = csv.DictReader(csv_file)

            headers = reader.fieldnames or []
            missing_fields = set(required_fields) - set(headers)
            extra_fields = set(headers) - set(required_fields)

            return {"valid": len(missing_fields) == 0, "headers": headers, "missing_fields": list(missing_fields), "extra_fields": list(extra_fields)}

        except Exception as e:
            logger.error(f"CSV validation failed: {str(e)}")
            return {"valid": False, "error": str(e)}
