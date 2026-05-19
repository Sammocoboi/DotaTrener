#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def _patch_psycopg2_windows_errors():
    """psycopg2 on Windows may fail decoding Russian libpq errors as UTF-8."""
    if sys.platform != "win32":
        return
    try:
        import psycopg2
    except ImportError:
        return

    if getattr(psycopg2, "_dotatrener_patched", False):
        return

    original_connect = psycopg2.connect

    def connect(*args, **kwargs):
        try:
            return original_connect(*args, **kwargs)
        except UnicodeDecodeError as exc:
            raise psycopg2.OperationalError(
                "Не удалось подключиться к PostgreSQL. Проверьте: "
                "1) служба PostgreSQL запущена; "
                "2) в .env задан реальный DB_PASSWORD (не your-password); "
                "3) пользователь и БД созданы (scripts/setup_postgres.sql)."
            ) from exc

    psycopg2.connect = connect
    psycopg2._dotatrener_patched = True


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DotaTrener.settings')
    _patch_psycopg2_windows_errors()
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
