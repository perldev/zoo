# -*- coding: utf-8 -*-

import sys

from core.core_loader import CoreLoader
from core.helpers.log_format import format_dict
from core.helpers.common import str_list_to_dict

from .commands.uninstall import UninstallCommand
from .commands.sync import SyncCommand
from .commands.list import ListProductsCommand
from .commands.install import InstallCommand
from .commands.runserver import RunServerCommand
from .commands.run_install_worker import RunInstallWorkerCommand, RunTaskWorkerCommand



"""
Маршрутизатор команд из аргументов коммандной строки
"""


def process_commands(args, settings):
    """
    Start Core and route cmd line commands
    :param args: parsed cmd line argumens (parser.parse_args())
    :param settings: Core will be created with this settings, by default they are loaded from settings.yaml
    :return: None
    """

    # if quiet mode - redefine stdout and stderr
    if args.quiet:
        sys.stdout = open("NUL", 'w')
        sys.stderr = open("NUL", 'w')

    core_loader = CoreLoader.get_instance()

    # start loader, core will be created and initialized in thread
    core_loader.start(settings)

    # commands that require the core, wait core creation
    core = core_loader.wait_core()

    # set interactive mode
    core.interactive = args.interactive
    # process commands that do not require the core
    if args.run_server:
        core_loader.start(settings, make_sync=True)
        cmd = RunServerCommand(settings, args.run_server_addr)
        cmd.setup_logs()
        cmd.start_supervisor()
        cmd.run()

        return



    # print settings
    if args.get_settings:
        settings = core.settings.get_state()
        print(format_dict(settings))
        return

    # set settings from cmd
    if args.set_settings:
        core.set_settings(str_list_to_dict(args.set_settings))
        settings = core.settings.get_state()
        print(format_dict(settings))
        return

    # process install/uninstall task

    if args.worker_task_id:
        RunInstallWorkerCommand(core, args.worker_task_id).run()
        return

    ## subprocess of installing
    if args.task_id:
        RunTaskWorkerCommand(core, args.task_id).run()
        return

    # print products
    if args.list_products:
        ListProductsCommand(core.feed).products()
        return

    # print installed products
    if args.show_installed:
        ListProductsCommand(core.feed).installed()
        return

    # search products and print
    if args.search:
        ListProductsCommand(core.feed).search(args.search)
        return

    # search installed products
    if args.sync:
        SyncCommand(core).do()
        return

    # install products from cmd line
    if args.install:
        InstallCommand(args.products, args.parameters).do()
        return

    # uninstall products from cmd line
    if args.uninstall:
        UninstallCommand(args.products, args.parameters).do()
        return

