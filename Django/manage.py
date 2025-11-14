#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    # ▼▼▼ 경로 추가 로직 ▼▼▼
    current_path = Path(__file__).resolve().parent  # Django 폴더
    parent_path = current_path.parent             # SKN18-4th-1Team 폴더
    
    # 1. 프로젝트 최상위 루트 추가 (Feature_rag를 찾기 위함)
    sys.path.append(str(parent_path))
    
    # 2. Feature_rag 폴더 내부 추가 (langgraph_structure를 찾기 위함) << 이 부분 추가됨!
    sys.path.append(str(parent_path / 'Feature_rag'))
    # ▲▲▲ [수정 끝] ▲▲▲

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

