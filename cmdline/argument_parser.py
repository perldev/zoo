# -*- coding: utf-8 -*-

import argparse

"""Description of arguments of command line interface"""


def create_parser():
    """Create command line arguments parser"""
    parser = argparse.ArgumentParser(description='Helicon Zoo feed installer')

    # print settings from settings.yaml
    parser.add_argument('--get-settings', action='store_true', help='get current settings')

    # write settings to settings.yaml
    parser.add_argument('--set-settings', dest="set_settings", nargs="+", help='set settings')

    # set urls of additional feeds
    parser.add_argument('--feed-urls', dest='urls', nargs='*', default='', help='feed urls to load')

    # print installed products
    parser.add_argument('--list-installed', action='store_true', dest='show_installed',
                        help='show all installed programs')
    # print all products
    parser.add_argument('--list', action='store_true', dest='list_products',
                        help='list latest versions of all available products')

    # search products
    parser.add_argument('--search', dest='search', help='search products for name and descriptions')

    # search installed products and write they to current.yaml
    parser.add_argument('--sync', action='store_true', dest='sync', help='synchronize installed version of products from system')

    # set products to install pr uninstall
    parser.add_argument('--products', dest='products', nargs="*", help='product names to install/uninstall')

    # make intstall
    parser.add_argument('--install', dest='install', action='store_true', help='install of specified products')

    # set install parameters for products to install
    parser.add_argument('--parameters', dest='parameters', nargs="*", help='application install parameters')

    # make uninstall
    parser.add_argument('--uninstall', action='store_true', dest='uninstall', help='uninstall a program')

    # quit mode
    parser.add_argument('-q', '--quiet', action='store_true', dest='quiet', default=False,
                        help='don\'t print anything to stdout')
    # allow communicate with user during install process
    parser.add_argument('-i', '--interactive', action='store_true', dest='interactive', default=False,
                        help='allow to ask install parameters if needed')
    # ignore any errors
    parser.add_argument('-f', '--force', action='store_true', dest='force', default=False, help='ignore exit code')

    # set log level
    parser.add_argument('--log-level', dest='log_level', default=None,
                        help='set log level (debug, warning, info, error, critical)')

    # start ui web server
    parser.add_argument('--run-server', dest='run_server', action='store_true', help='run web ui at http://localhost:7799/')

    # set ui server port
    parser.add_argument('--run-server-addr', dest='run_server_addr', default='127.0.0.1:7799', help='bind web ui server to "addr:port" or port')

    # start install/unstall task
    parser.add_argument('--start-install-worker', dest='worker_task_id', type=int, help='start supervisour worker')

    parser.add_argument('--task-work', dest='task_id', type=int, help='start installer worker with task by id')

    return parser


