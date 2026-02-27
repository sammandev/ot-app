import logging
import os
import time
from threading import Lock

from django.conf import settings

logger = logging.getLogger(__name__)


class FileSharingViolation(Exception):
    """Raised when a file cannot be accessed due to sharing violation (file is open)"""

    pass


class SMBConnectionPool:
    """Thread-safe SMB connection pool for reusing connections"""

    def __init__(self, server, username, password, share_name, domain="WORKGROUP", port=445, timeout=30, min_size=2, max_size=5):
        self.server = server
        self.username = username
        self.password = password
        self.share_name = share_name
        self.domain = domain
        self.port = port
        self.timeout = timeout
        self.min_size = min_size
        self.max_size = max_size

        self.connections = []
        self.lock = Lock()
        self.enabled = settings.SMB_CONFIG.get("enabled", False)

        if self.enabled:
            self._initialize_pool()

    def _initialize_pool(self):
        """Initialize minimum connections in the pool"""
        try:
            for _ in range(self.min_size):
                conn = self._create_connection()
                if conn:
                    self.connections.append(conn)
            logger.info("SMB pool initialized with %s connections to %s", len(self.connections), self.server)
        except Exception as e:
            logger.error("Failed to initialize SMB pool: %s", e)
            self.enabled = False

    def _create_connection(self):
        """Create new SMB connection"""
        if not self.enabled:
            return None

        try:
            from smb.SMBConnection import SMBConnection

            conn = SMBConnection(username=self.username, password=self.password, my_name="OvertimeApp", remote_name=self.server, domain=self.domain, use_ntlm_v2=True, is_direct_tcp=True)
            conn.connect((self.server, self.port), timeout=self.timeout)
            logger.debug("Created new SMB connection to %s:%s", self.server, self.port)
            return conn
        except Exception as e:
            logger.error("Failed to create SMB connection to %s: %s", self.server, e)
            return None

    def get_connection(self):
        """Get available connection from pool"""
        if not self.enabled:
            return None

        with self.lock:
            # Try existing connections first
            for conn in self.connections[:]:
                if self._is_alive(conn):
                    logger.debug("Using existing SMB connection from pool")
                    return conn
                else:
                    logger.debug("Removing dead connection from pool")
                    self.connections.remove(conn)

            # Create new connection if pool not full
            if len(self.connections) < self.max_size:
                conn = self._create_connection()
                if conn:
                    self.connections.append(conn)
                    logger.debug("Created new connection. Pool size: %s", len(self.connections))
                    return conn

            # Return first alive connection if all are busy
            if self.connections:
                logger.debug("Reusing connection from busy pool")
                return self.connections[0]

        logger.warning("No SMB connections available")
        return None

    def _is_alive(self, conn):
        """Check if connection is still alive"""
        try:
            conn.listPath(self.share_name, "/", timeout=5)
            return True
        except Exception as e:
            logger.debug("Connection check failed: %s", e)
            return False

    def cleanup(self):
        """Close all connections in pool"""
        with self.lock:
            for conn in self.connections:
                try:
                    conn.close()
                except Exception as e:
                    logger.debug("Error closing SMB connection: %s", e)
            self.connections.clear()
            logger.info("SMB connection pool cleaned up")


class SMBService:
    """SMB file operations with retry logic"""

    def __init__(self, pool=None):
        self.pool = pool
        self.logger = logging.getLogger(__name__)
        self.max_retries = 3

    def upload_file(self, local_path, remote_path):
        """Upload file to SMB share with retry logic"""
        return self._retry_operation(lambda: self._upload_file_impl(local_path, remote_path), operation_name=f"upload {os.path.basename(local_path)} to {remote_path}")

    def _upload_file_impl(self, local_path, remote_path):
        """Actual file upload implementation"""
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"Local file not found: {local_path}")

        if self.pool is None or not self.pool.enabled:
            self.logger.info("SMB disabled. File would be uploaded to: %s", remote_path)
            return remote_path

        conn = self.pool.get_connection()
        if not conn:
            raise ConnectionError("No SMB connection available")

        try:
            file_size = os.path.getsize(local_path)
            with open(local_path, "rb") as f:
                conn.storeFile(self.pool.share_name, remote_path, f, timeout=60)

            self.logger.info("Successfully uploaded %s to SMB (%s bytes)", os.path.basename(local_path), file_size)
            return remote_path

        except Exception as e:
            error_str = str(e)
            # Check for file sharing violation (0xC0000043 = STATUS_SHARING_VIOLATION)
            if "0xC0000043" in error_str or "Unable to open file" in error_str:
                self.logger.warning("File sharing violation for %s. The file may be open by another user. Error: %s", remote_path, e)
                raise FileSharingViolation(f"Cannot upload to {remote_path}: The file is currently open by another user. Please ask them to close the file and try again.") from e
            self.logger.error("Failed to upload %s to %s: %s", local_path, remote_path, e)
            raise

    def file_exists(self, remote_path):
        """Check if file exists on SMB share"""
        return self._retry_operation(lambda: self._file_exists_impl(remote_path), operation_name=f"check existence of {remote_path}")

    def _file_exists_impl(self, remote_path):
        """Check file existence implementation"""
        if self.pool is None or not self.pool.enabled:
            return False

        conn = self.pool.get_connection()
        if not conn:
            return False

        try:
            remote_dir = "/".join(remote_path.split("/")[:-1]) or "/"
            filename = remote_path.split("/")[-1]

            file_list = conn.listPath(self.pool.share_name, remote_dir, timeout=10)

            exists = any(f.filename == filename for f in file_list)
            self.logger.debug("File %s exists: %s", remote_path, exists)
            return exists
        except Exception as e:
            self.logger.error("Error checking file existence: %s", e)
            return False

    def delete_file(self, remote_path):
        """Delete file from SMB share"""
        return self._retry_operation(lambda: self._delete_file_impl(remote_path), operation_name=f"delete {remote_path}")

    def _delete_file_impl(self, remote_path):
        """Delete file implementation"""
        if self.pool is None or not self.pool.enabled:
            self.logger.info("SMB disabled. File would be deleted: %s", remote_path)
            return True

        conn = self.pool.get_connection()
        if not conn:
            raise ConnectionError("No SMB connection available")

        try:
            conn.deleteFile(self.pool.share_name, remote_path, timeout=10)
            self.logger.info("Deleted %s from SMB share", remote_path)
            return True
        except Exception as e:
            self.logger.error("Failed to delete %s: %s", remote_path, e)
            raise

    def _retry_operation(self, operation, operation_name, max_retries=None):
        """Execute operation with exponential backoff retry logic"""
        if max_retries is None:
            max_retries = self.max_retries

        last_error = None
        for attempt in range(max_retries):
            try:
                self.logger.debug("Executing: %s (attempt %s/%s)", operation_name, attempt + 1, max_retries)
                return operation()
            except FileSharingViolation as e:
                # For sharing violations, use shorter retry intervals
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 30 * (attempt + 1)  # 30s, 60s, 90s
                    self.logger.warning("File sharing violation for '%s' (attempt %s/%s). File is open by another user. Retrying in %ss...", operation_name, attempt + 1, max_retries, wait_time)
                    time.sleep(wait_time)
                else:
                    self.logger.error("File sharing violation for '%s' persists after %s attempts. Please ensure no one has the file open.", operation_name, max_retries)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 60 * (attempt + 1)
                    self.logger.warning("Operation '%s' failed (attempt %s/%s). Retrying in %ss. Error: %s", operation_name, attempt + 1, max_retries, wait_time, e)
                    time.sleep(wait_time)
                else:
                    self.logger.error("Operation '%s' failed after %s attempts. Final error: %s", operation_name, max_retries, e)

        raise last_error


# ============================================================================
# Singleton instance
# ============================================================================
_smb_pool = None
_smb_service = None


def get_smb_service():
    """Get or create SMB service singleton"""
    global _smb_pool, _smb_service

    if _smb_service is not None:
        return _smb_service

    config = settings.SMB_CONFIG
    if not config.get("enabled", False):
        logger.debug("SMB is disabled in configuration")
        return None

    try:
        _smb_pool = SMBConnectionPool(
            server=config["server"],
            username=config["username"],
            password=config["password"],
            share_name=config["share"],
            domain=config.get("domain", "WORKGROUP"),
            port=config.get("port", 445),
            timeout=config.get("timeout", 30),
            min_size=settings.SMB_POOL_SIZE.get("min", 2),
            max_size=settings.SMB_POOL_SIZE.get("max", 5),
        )
        _smb_service = SMBService(_smb_pool)
        return _smb_service
    except Exception as e:
        logger.error("Failed to initialize SMB service: %s", e)
        return None


def cleanup_smb_service():
    """Clean up SMB connections"""
    global _smb_pool, _smb_service
    if _smb_pool:
        _smb_pool.cleanup()
    _smb_service = None
    _smb_pool = None
