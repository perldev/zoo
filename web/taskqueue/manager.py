# -*- coding: utf-8 -*-

import sys
import subprocess
import json
import logging
from threading import Thread
import time

from core.core import Core
from core.parameters_manager import ParametersManager
from core.product_collection import ProductCollection
from core.helpers.decode import OutputDecoder
from web.taskqueue.loghandler import TaskDbLogHandler
from web.taskqueue.models import Task


class TaskManager:
    """
    управление воркером
    создает дочерний процесс
    ждет его завершения
    следит чтобы не создавалось больше одного воркера
    читает его лог, std_out и сохраняет это в базе данных


    """
    _instance = None

    @classmethod
    def get_instance(cls):
        """
        :rtype : TaskManager
        """
        if not cls._instance:
            cls._instance = TaskManager()
            # cls._instance.create_job_object()
        return cls._instance

    def __init__(self):
        self.pid = None
        self.process = None
        self.task = None
        self.wait_worker_process_thread = None
        self.stdout_read_thread = None
        self.stderr_read_thread = None
        self.logger = None
        self.decoder = OutputDecoder()

    def has_active_install(self):
        """
        Есть ли уже активный воркер?

        :return:
        """
        is_running = (self.process and self.process.poll() is None)
        return is_running

    def run_worker(self, task_id):
        """
        Запустить воркер, с заданием task_id
        :param task_id:
        :raise Exception:
        """
        if self.has_active_install():
            raise Exception("Can't run new worker, another one still exists")

        self.create_worker(task_id)

    def cancel(self):
        """
        отменить, убить процесс

        """
        if self.process:
            self.process.terminate()
        self.task = None

    def create_worker(self, task_id):
        """
        создать воркер, передать task_id дочернему процессу
        zoocmd --start-install-worker= task_id

        новый процесс сам все сделает дальше

        :param task_id:
        """
        self.logger = logging.getLogger('zoo-worker-task-' + str(task_id))
        self.logger.propagate = False
        self.logger.handlers = []
        self.logger.addHandler(TaskDbLogHandler(self.task))

        self.process = subprocess.Popen(
            (
                sys.executable,
                sys.argv[0],
                '--start-install-worker={0}'.format(task_id),
                #'--log-level=debug'
            ),
          # stdout =  subprocess.PIPE,
          # stderr = subprocess.PIPE
        )

        # self.pid = self.process.pid
        #
        self.wait_worker_process_thread = Thread(target=self.wait_worker_process)
        self.wait_worker_process_thread.start()
        #
        # self.stdout_read_thread = Thread(target=self.read_stdout)
        # self.stderr_read_thread = Thread(target=self.read_stderr)
        #
        # self.stdout_read_thread.start()
        # self.stderr_read_thread.start()


    def wait_worker_process(self):
        logging.debug('thread for waiting of worker process started')
        while self.process:
            if self.process.poll() is not None:
                logging.debug("process is finished")
                self.process = None
                break
            else:
                logging.debug('sleep')
                time.sleep(1)

        self.logger.info('install worker process is finished')
        self.sync_core()

    def read_stdout(self):
        """
        читать лог воркера, это должно происходить в отдельном потоке чтобы не блокировать работу воркера

        """
        while self.process:
            if self.process.poll() is not None:
                break

            if self.process.stdout.closed:
                logging.debug("stdout is closed")
                break

            line = self.process.stdout.readline()
            if line != b'':
                s = self.decoder.try_decode(line)
                s = s.rstrip()
                self.logger.info(s)
                logging.debug(line.decode('ascii', errors='ignore').rstrip())
            else:
                self.process.stdout.close()

        logging.debug("read worker stdout thread is finished")

    def read_stderr(self):
        """
        читать лог воркера, это должно происходить в отдельном потоке чтобы не блокировать работу воркера
        """
        while self.process:
            if self.process.poll() is not None:
                break

            if self.process.stderr.closed:
                logging.debug("stderr is closed")
                break

            line = self.process.stderr.readline()
            if line != b'':
                s = self.decoder.try_decode(line)
                self.logger.warning(s)
                logging.debug(line.decode('ascii', errors='ignore').rstrip())
            else:
                self.process.stderr.close()

        logging.debug("read worker stderr thread is finished")

    @staticmethod
    def sync_core():
        """
        После каждой установки выполнить sync чтобы current.yaml был в актуальном сосотоянии

        """
        logging.debug('start core updating after install process finished')
        Core.get_instance().set_expired(True)
        Core.get_instance().update()

    def create_install_task(self, requested_products: list, products: ProductCollection, parameter_manager: ParametersManager):
        """
        фабричный метод: создать такс с переданными параметрами, с типом COMMAND_INSTALL
        сохранить в базе данных
        зхапустить воркер

        :param requested_products:  те продукты которые выбрал пользователь
        :param products:  продукты для установки (продукты которые выбрал пользователь + зависимости)
        :param parameter_manager:
        :return: номер таска
        """
        title = 'Installing products: {0}'.format(', '.join([product_name for product_name in requested_products]))
        state = {
            'requested_products': requested_products,
            'products': products.to_json_list(),
            'parameters': parameter_manager.get_state()
        }
        settings = Core.get_instance().settings.get_state()

        logging.debug('state: {0}'.format(state))
        state2save = json.dumps(state, sort_keys=True, indent=1)
        task = Task(
            command=Task.COMMAND_INSTALL,
            title=title,
            params=state2save,
            settings=json.dumps(settings, sort_keys=True, indent=1)
        )
        task.save()
        self.task = task

        # production
        self.run_worker(task.id)

        # For debug worker uncomment this
        #self.task.execute()

        return task.id

    def create_upgrade_task(self, requested_products: list, products: ProductCollection):
        """
        фабричный метод: создать такс с переданными параметрами, с типом COMMAND_UPGRADE
        сохранить в базе данных
        зхапустить воркер

        :param requested_products:
        :param products:
        :param parameter_manager:
        :return:
        """
        title = 'Upgrading products: {0}'.format(', '.join([product_name for product_name in requested_products]))
        state = {
            'requested_products': requested_products,
            'products': products.get_names_list(),
            'parameters': {}
        }
        settings = Core.get_instance().settings.get_state()

        logging.debug('state: {0}'.format(state))

        task = Task(
            command=Task.COMMAND_UPGRADE,
            title=title,
            params=json.dumps(state, sort_keys=True, indent=1),
            settings=json.dumps(settings, sort_keys=True, indent=1)
        )
        task.save()
        self.task = task

        # production
        self.run_worker(task.id)

        # For debug worker uncomment this
        #self.task.execute()

        return task.id

    def create_uninstall_task(self, products: ProductCollection):
        """
        фабричный метод: создать такс с переданными параметрами, с типом COMMAND_UNINSTALL
        сохранить в базе данных
        зхапустить воркер

        :param requested_products:
        :param products:
        :param parameter_manager:
        :return:
        """

        title = 'Uninstalling products: {0}'.format(', '.join([product.title for product in products]))
        state = {
            'products': products.get_names_list(),
        }
        settings = Core.get_instance().settings.get_state()
        task = Task(
            command=Task.COMMAND_UNINSTALL,
            title=title,
            params=json.dumps(state, sort_keys=True, indent=1),
            settings=json.dumps(settings, sort_keys=True, indent=1))
        task.save()
        self.task = task
        self.run_worker(task.id)
        return task.id

    def rerun_task(self, task):
        """
        повтонрно выполнить задание N
        удобно для оталадки,
        удобно если что-то упало, повторить снова
        :param task:
        :return:
        """
        task.status = Task.STATUS_PENDING
        task.logmessage_set.all().delete()
        task.error_message = ''
        task.save()
        self.task = task
        self.run_worker(task.id)
        return task.id
