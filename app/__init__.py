"""
BSource Database Backup Package
Sistema automatizado de backup de bases de dados com suporte a múltiplos engines e storage providers.
"""

__version__ = "3.0.0"
__author__ = "BSource Team"
__description__ = (
    "Sistema automatizado de backup de bases de dados "
    "(PostgreSQL, MySQL, MariaDB, SQL Server) "
    "com envio para Cloudflare R2 ou AWS S3"
)

from .db_dumper import DatabaseDumper, create_dumper_from_env
from .storage_provider import StorageProvider, create_storage_from_env

__all__ = [
    "DatabaseDumper",
    "create_dumper_from_env",
    "StorageProvider",
    "create_storage_from_env",
]