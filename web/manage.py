#!/usr/bin/env python

import sys

import os
from core.core_loader import CoreLoader


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")

    core_loader = CoreLoader.get_instance()
    core_loader.start()
    core_loader.wait_core()

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
