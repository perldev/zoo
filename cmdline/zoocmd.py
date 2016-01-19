# -*- coding: utf-8 -*-

import sys

import os
import logging
from core.settings import Settings
from core.start import init_logger
from cmdline import argument_parser
from cmdline.route import process_commands

"""
Main function of cmd line interface
"""


def main():
    """
    Main entry point of cmd line interface
    """

    # parse cmd line arguments
    parser = argument_parser.create_parser()
    args = parser.parse_args()

    # if not args, just print help
    if len(sys.argv) <= 1:
        parser.print_help()
        return

    # get debug level
    log_level_str = args.log_level or os.environ.get('LOG_LEVEL') or 'INFO'
    log_level_str = log_level_str.upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    # init logger
    init_logger(log_level, args.quiet)

    # load settings from settings.yaml
    settings = Settings.load_from_file()
    # if additional feed urls are in cmd line args, then add it to settings
    if args.urls:
        settings.urls.extend(args.urls)

    # route commands
    process_commands(args, settings)


if __name__ == '__main__':
    main()