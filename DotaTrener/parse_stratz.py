"""
DEPRECATED: используйте management-команды load_heroes и sync_stratz_meta.

  python manage.py load_heroes
  python manage.py sync_stratz_meta
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
    call_command("load_heroes")
    call_command("sync_stratz_meta")
