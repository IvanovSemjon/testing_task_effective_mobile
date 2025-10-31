#!/usr/bin/env python
import os
import sys
from auth_system_project.config.env_loader import ENV


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"auth_system_project.config.{ENV}")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Make sure it's installed and your virtualenv is active."
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
