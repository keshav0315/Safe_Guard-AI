#!/usr/bin/env python
"""
SafeGuard AI — Django Management Script
Yeh file backend root mein hai. Run karo:
  .\\venv\\Scripts\\python.exe manage.py <command>
"""

import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    # ---------------------------------------------------------------------------
    # Path setup — safeguard_backend package ko importable banao
    # manage.py backend/ mein hai, safeguard_backend/ uske andar hai
    # ---------------------------------------------------------------------------
    backend_root = Path(__file__).resolve().parent          # backend/
    safeguard_pkg = backend_root / 'safeguard_backend'       # backend/safeguard_backend/

    # Dono paths sys.path mein add karo:
    # - backend_root: 'safeguard_backend' package directly import hoga
    # - safeguard_pkg: 'config', 'apps', 'common' directly import honge
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))
    if str(safeguard_pkg) not in sys.path:
        sys.path.insert(0, str(safeguard_pkg))

    # Default settings — development use karo jab tak override na ho
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?\n"
            f"Venv activate karo: .\\venv\\Scripts\\activate"
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
