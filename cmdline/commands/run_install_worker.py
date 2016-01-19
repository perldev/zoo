# -*- coding: utf-8 -*-

import os
import sys
import json
import logging
import time
from core.start import start
import traceback


class RunInstallWorkerCommand(object):
    """
    Helper class to run install/uninstall task
    """

    def __init__(self, core, task_id=None):
        self.core = core
        self.task_id = task_id

    def run(self):
        """
        Run task
        """
        # set django env to load django settings.py and get database config
        # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
        # from django.core import management
        # append web module to python path

        sys.path.append(os.path.join(self.core.settings.root, 'src', 'web'))
        from web.taskqueue.tornado_worker import TornadoWorker
        from web.taskqueue.models_peewee  import TaskPeewee as Task

        print("starting worker with frontend web on 7798")
        web = TornadoWorker()
        print("start listening server")
        web.start()


class RunTaskWorkerCommand(object):
    """
    Helper class to run install/uninstall task
    """

    def __init__(self, core, task_id):
        self.core = core
        self.task_id = task_id

    def run(self):
        """
        Run task
        """
        # set django env to load django settings.py and get database config
        # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
        # from django.core import management
        # append web module ti python path
        sys.path.append(os.path.join(self.core.settings.root, 'src', 'web'))
        from web.taskqueue.models_peewee import TaskPeewee as Task
        print("start working on  task %s" % self.task_id)
        task = Task.get(Task.id == self.task_id)

        if task.status != Task.STATUS_PENDING:
            raise Exception("Incorrect status: " + task.status)

        # create core with settings for current task
        settings = None
        if task.settings:
            settings = json.loads(task.settings)

        start(settings)

        # configure logger

        logger = logging.getLogger()

        # remove all handlers
        logger.handlers = []
        # all to output, tornado will write to db from output of this process
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(module)s.%(funcName)s: %(message)s')
        logger.addHandler(ch)
        ch.setLevel(logging.INFO)
        logger.addHandler(ch)
        self.do_task(task, Task.LOCK)
        sys.exit(0)

    @staticmethod
    def do_task(task, lock):
            """
            выполнить задание
            :param task:
            """
            try:
                from web.taskqueue.tornado_worker import TornadoWorker
                task.status = task.STATUS_RUNNING
                task.save()
                logging.debug('get task #{0}: {1}'.format(task.id, task.title))
                task.execute()
                task.status = task.STATUS_DONE
                task.save()
                TornadoWorker.clear_lock(lock)
                logging.debug('Done task {0}'.format(task.id))
            except Exception as e:
                tb = traceback.format_exc()
                task.status = task.STATUS_EXCEPTION
                task.error_message = 'An error occurred during execution of task {0}.\r\nMessage: {1}\r\n{2}'.format(
                    task.id, e, tb)
                task.save()
                TornadoWorker.clear_lock(lock)
                logging.error(task.error_message)
                sys.exit(1)