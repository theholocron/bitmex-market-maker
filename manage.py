#!/usr/bin/env python
import os
import json
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bitmex_market_maker.settings")

    if os.getenv('SERVER_ENV', 'local') == 'local':
        env_vars = json.loads(open('local_variables.json', 'rb').read())
        for key, var in env_vars.items():
            os.environ[key] = var

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
