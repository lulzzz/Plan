#!/usr/bin/env python
import os
import sys

# project = 'settings_lifung_sourcing'
# project = 'settings_wolford_iap'
# project = 'settings_bauer_dpp'
# project = 'settings_vans_pdas'
# project = 'settings_tattoo'
project = 'settings_ess'
PROJECT_SETTINGS = 'settings.projects.' + project + '.project'

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', PROJECT_SETTINGS)
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)
