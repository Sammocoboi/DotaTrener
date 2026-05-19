"""
DEPRECATED: используйте management-команду sync_stratz_meta.

  python manage.py load_heroes
  python manage.py sync_stratz_meta
  python manage.py sync_stratz_meta --limit 3
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DotaTrener.settings")

import django

django.setup()

from django.core.management import call_command


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Deprecated wrapper for sync_stratz_meta")
    parser.add_argument("--limit", type=int, help="Limit heroes (debug)")
    parser.add_argument("--patch", type=str, help="Patch version")
    args = parser.parse_args()

    kwargs = {}
    if args.limit:
        kwargs["limit"] = args.limit
    if args.patch:
        kwargs["patch"] = args.patch

    call_command("sync_stratz_meta", **kwargs)
