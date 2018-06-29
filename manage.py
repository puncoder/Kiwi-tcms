#!/usr/bin/env python
# pylint: disable=missing-docstring

import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tcms.settings.devel")

    from django.core.management import execute_from_command_line
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'runserver':
        with open('xml-rpc.txt', 'w') as file:
            if len(sys.argv) > 2:
                file.write(sys.argv[2])
            else:
                file.write('127.0.0.1:8000')

    execute_from_command_line(sys.argv)
