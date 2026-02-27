"""
Celery Tasks
Async task processing for long-running operations
"""

import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_excel_files_async(self, overtime_id):
    """
    Generate Excel files for overtime request and upload to SMB.

    Uses ExcelGenerator's built-in SMB upload which writes files to the correct
    period folder path (e.g. Management/PTB/AST_Portal_Overtime/2026-01-26_2026-02-25/).
    When EXCEL_TEMP_ONLY=True, files are created in a temp directory, uploaded to SMB,
    then cleaned up automatically.

    Args:
        overtime_id: ID of OvertimeRequest

    Returns:
        dict: Task result with file paths or error
    """
    try:
        from api.models import OvertimeRequest
        from api.utils.excel_generator import ExcelGenerator

        # Update progress
        self.update_state(state="PROGRESS", meta={"progress": 10, "status": "Fetching data"})

        overtime = OvertimeRequest.objects.select_related("employee", "project", "department").get(id=overtime_id)

        logger.info("Generating Excel files for overtime request %s (date: %s)", overtime_id, overtime.request_date)

        # Export data grouped by department (multi-sheet support)
        export_data_grouped = OvertimeRequest.export_daily_data_by_department(overtime.request_date)
        monthly_data_grouped = OvertimeRequest.export_monthly_data_by_department(overtime.request_date)

        self.update_state(state="PROGRESS", meta={"progress": 30, "status": "Generating Excel and uploading"})

        # Generate files and upload to SMB in one step.
        # ExcelGenerator.generate_all_excel_files with upload=True will:
        #   1. Create Excel workbooks (multi-sheet, one per department)
        #   2. Save locally (temp dir if temp_only=True, else data/excel/{period}/)
        #   3. Upload to correct SMB period folder via pysmb
        #   4. Clean up temp files if temp_only=True
        file_paths = {}
        if export_data_grouped or monthly_data_grouped:
            file_paths = ExcelGenerator.generate_all_excel_files(
                export_data_grouped,
                monthly_data_grouped,
                overtime.request_date,
                upload=True,
                temp_only=ExcelGenerator.EXCEL_TEMP_ONLY,
            )
            dept_count = len(export_data_grouped or {})
            logger.info("Excel files generated and uploaded for date %s (multi-sheet with %s departments)", overtime.request_date, dept_count)
        else:
            logger.warning("No data to export for overtime request %s (date: %s)", overtime_id, overtime.request_date)

        self.update_state(state="PROGRESS", meta={"progress": 95, "status": "Finalizing"})

        logger.info("Task completed for overtime request %s", overtime_id)

        return {
            "status": "success",
            "message": f"Excel files generated for {overtime.request_date}",
            "overtime_id": overtime_id,
            "file_paths": {k: str(v) for k, v in file_paths.items()},
        }
    except Exception as exc:
        logger.error("Error generating Excel files for OT %s: %s", overtime_id, exc, exc_info=True)
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1)) from exc


@shared_task(bind=True, max_retries=3)
def regenerate_excel_after_delete(self, request_date_str):
    """
    Regenerate Excel files after an OvertimeRequest is deleted.
    Handles both regeneration of remaining data and cleanup of empty files.

    Args:
        request_date_str: ISO date string (YYYY-MM-DD) of the deleted request
    """
    try:
        from datetime import datetime

        from api.models import OvertimeRequest
        from api.utils.excel_generator import ExcelGenerator

        date = datetime.strptime(request_date_str, "%Y-%m-%d").date()
        daily_requests = OvertimeRequest.objects.filter(request_date=date).exclude(status="rejected")

        if daily_requests.exists():
            # Remaining requests exist for this date — regenerate all files with SMB upload
            export_data_grouped = OvertimeRequest.export_daily_data_by_department(date)
            monthly_data_grouped = OvertimeRequest.export_monthly_data_by_department(date)
            ExcelGenerator.generate_all_excel_files(
                export_data_grouped,
                monthly_data_grouped,
                date,
                upload=True,
                temp_only=getattr(ExcelGenerator, "EXCEL_TEMP_ONLY", False),
            )
            logger.info("Excel files regenerated and uploaded after deletion for date %s", date)
        else:
            # No remaining requests for this date — delete daily files from SMB, handle monthly
            monthly_data = OvertimeRequest.export_monthly_data(date)
            conn = ExcelGenerator.get_smb_connection()
            if conn:
                try:
                    period_path = ExcelGenerator.get_smb_period_folder(date)
                    if period_path:
                        date_str = date.strftime("%Y%m%d")
                        try:
                            conn.deleteFiles(ExcelGenerator.SMB_CONFIG["share_name"], f"{period_path}/{date_str}OT.xlsx")
                            conn.deleteFiles(ExcelGenerator.SMB_CONFIG["share_name"], f"{period_path}/{date_str}OTSummary.xlsx")
                            logger.info("Deleted daily SMB files for %s", date)
                        except Exception as e:
                            logger.warning("Error deleting daily files for %s: %s", date, e)

                        if monthly_data:
                            conn.close()
                            conn = None  # Prevent double-close in finally
                            ExcelGenerator.generate_monthly_excel_files(monthly_data, date)
                            logger.info("Monthly files regenerated after deletion for %s", date)
                        else:
                            from api.utils.time_helpers import get_period_boundaries

                            current_period_start, next_period_end = get_period_boundaries(date)
                            monthly_fn = f"~{current_period_start.strftime('%Y_%m_%d')}-{next_period_end.strftime('%Y_%m_%d')}OT.xlsx"
                            monthly_sum_fn = f"~{current_period_start.strftime('%Y_%m_%d')}-{next_period_end.strftime('%Y_%m_%d')}OTSummary.xlsx"
                            try:
                                conn.deleteFiles(ExcelGenerator.SMB_CONFIG["share_name"], f"{period_path}/{monthly_fn}")
                                conn.deleteFiles(ExcelGenerator.SMB_CONFIG["share_name"], f"{period_path}/{monthly_sum_fn}")
                                logger.info("Deleted monthly SMB files for period containing %s", date)
                            except Exception as e:
                                logger.warning("Error deleting monthly files: %s", e)
                finally:
                    if conn:
                        try:
                            conn.close()
                        except Exception:
                            pass

        return {"status": "success", "date": request_date_str}
    except Exception as exc:
        logger.error("Error regenerating Excel after delete: %s", exc, exc_info=True)
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1)) from exc


@shared_task
def cleanup_expired_sessions():
    """
    Clean up expired user sessions
    Scheduled to run periodically
    """
    try:
        from api.models import UserSession

        # Delete expired sessions (both active and inactive)
        deleted_count, _ = UserSession.objects.filter(token_expires_at__lt=timezone.now()).delete()

        logger.info("Cleaned up %s expired sessions", deleted_count)

        return {"status": "success", "deleted_count": deleted_count}
    except Exception as e:
        logger.error("Error cleaning up sessions: %s", e, exc_info=True)
        return {"status": "error", "message": str(e)}
