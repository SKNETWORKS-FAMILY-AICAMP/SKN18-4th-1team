#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    # ▼▼▼ [추가된 부분] 상위 폴더(Feature_rag)를 인식하게 해주는 마법의 코드 ▼▼▼
    current_path = Path(__file__).resolve().parent  # 현재 manage.py 위치 (Django 폴더)
    parent_path = current_path.parent             # 그 상위 폴더 (SKN18-4th-1Team)
    sys.path.append(str(parent_path))             # 파이썬 경로에 추가!
    # ▲▲▲ [추가 끝] ▲▲▲

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

