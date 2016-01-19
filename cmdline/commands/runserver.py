# -*- coding: utf-8 -*-

import os
import os.path
import sys
import logging
import subprocess

class RunServerCommand(object):
    """
    Helper class to start web ui django server
    """

    def __init__(self, settings, port):
        self.settings = settings
        self.port = port

    @staticmethod
    def setup_logs():
        # set up addition log file when server starts from ui.exe
        log_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'logs'))
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, '_zoo_server.log')
        if os.path.exists(log_path):
            os.remove(log_path)
        logger = logging.getLogger()
        ch = logging.FileHandler(log_path)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d [%(levelname)3.3s] %(module)s.%(funcName)s: %(message)s', '%y%m%d %H:%M:%S'))
        logger.addHandler(ch)

    # starting tornado queue manager in separate subprocess
    def start_supervisor(self):
        log = open(self.settings.supervisor_logpath, 'w')
        # may be we must looking at it, but why if it will become the main process
        print("starting tornado task manager")
        cmd = sys.argv[0]
        exe = sys.executable
        subprocess.Popen(
            (
                exe,
                '-u',
                cmd,
                '--start-install-worker',
                '1'
            ),
            stderr=log,
            stdout=log
        )
        print("hello world")

    def run(self):
        """
        run django server
        """
        # set django env
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
        from django.core import management
        # add web module to python path
        sys.path.append(os.path.join(self.settings.root, 'src', 'web'))
        # sync database: create sqlite db if needed
        management.call_command('syncdb')

        # start http server on specific port
        management.call_command('runserver', self.port, use_reloader=False, use_threading=True, use_static_handler=False)
