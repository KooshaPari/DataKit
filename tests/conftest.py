"""
Pytest configuration and fixtures for DataKit tests.
"""

import sys
from pathlib import Path

# Get paths relative to this conftest.py file
_datakit_root = Path(__file__).parent.parent  # DataKit/
_python_dir = _datakit_root / "python"

# Add Python package source paths to sys.path for testing
# Package: directory name -> (src_subdir, import_name)
_package_configs = {
    "pheno-events": ("pheno-events/src", "pheno_events"),
    "pheno-database": ("pheno-database/src", "pheno_database"),
    "pheno-caching": ("pheno-caching/src", "pheno_caching"),
    "pheno-storage": ("pheno-storage/src", "pheno_storage"),
    "db_kit": ("db_kit", "db_kit"),
}

for _pkg_name, (_src_subdir, _import_name) in _package_configs.items():
    full_path = _python_dir / _src_subdir
    if full_path.exists():
        # Add src directory to path
        sys.path.insert(0, str(full_path))
        # For packages without src/, also add parent
        if _src_subdir == "db_kit":
            # db_kit uses flat structure, so we need both the package and python dir
            sys.path.insert(0, str(_python_dir))  # for "from adapters.base import ..."
            sys.path.insert(0, str(full_path))  # for "from db_kit import ..."


# Configure pytest-asyncio
pytest_plugins = ["pytest_asyncio"]
