"""HDFS storage manager for article media files."""

import os
from typing import Optional

from hdfs import InsecureClient

from src.config import HDFS_CONFIG


class HDFSManager:
    """Manages file uploads and downloads to HDFS."""

    def __init__(self):
        namenode = HDFS_CONFIG["namenode"]
        port = HDFS_CONFIG["web_port"]
        self.client = InsecureClient(f"http://{namenode}:{port}", user="root")
        self.base_path = HDFS_CONFIG["base_path"]
        self.replication = HDFS_CONFIG["replication"]

    def upload_file(self, local_path: str, hdfs_path: str) -> bool:
        """Upload file to HDFS."""
        full_hdfs_path = f"{self.base_path}/{hdfs_path}"

        try:
            parent_dir = os.path.dirname(full_hdfs_path)
            if parent_dir and not self.client.status(parent_dir, strict=False):
                self.client.makedirs(parent_dir)

            self.client.upload(
                full_hdfs_path, local_path, replication=self.replication, overwrite=True
            )
            return True
        except Exception as e:
            print(f"⚠ HDFS upload failed for {hdfs_path}: {e}")
            return False

    def read_file(self, hdfs_path: str) -> Optional[bytes]:
        """Read file content from HDFS."""
        full_hdfs_path = f"{self.base_path}/{hdfs_path}"

        try:
            with self.client.read(full_hdfs_path) as reader:
                return reader.read()
        except Exception as e:
            print(f"⚠ HDFS read failed for {hdfs_path}: {e}")
            return None

    def file_exists(self, hdfs_path: str) -> bool:
        """Check if file exists in HDFS."""
        full_hdfs_path = f"{self.base_path}/{hdfs_path}"

        try:
            return self.client.status(full_hdfs_path, strict=False) is not None
        except Exception:
            return False

    def list_files(self, hdfs_path: str = "") -> list[str]:
        """List files in HDFS directory."""
        full_hdfs_path = (
            f"{self.base_path}/{hdfs_path}" if hdfs_path else self.base_path
        )

        try:
            return self.client.list(full_hdfs_path)
        except Exception as e:
            print(f"⚠ HDFS list failed for {hdfs_path}: {e}")
            return []

    def get_storage_info(self) -> dict:
        """Get HDFS cluster storage information."""
        try:
            self.client.status("/")
            return {
                "available": True,
                "base_path": self.base_path,
                "replication": self.replication,
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
            }
