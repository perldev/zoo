# -*- coding: utf-8 -*-

from web.helpers.singletonmixin import  Singleton
from web.helpers.json import json_response, json_request

from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from core.helpers.decode import OutputDecoder
from web.taskqueue.loghandler import TaskDbLogHandler
from web.taskqueue.models_peewee import TaskPeewee as Task

import time
import subprocess
import logging
import sys
import json

from core.core import Core
from core.product_collection import ProductCollection
from core.dependency_manager import DependencyManager
from core.parameters_manager import ParametersManager
from core.parameters_parser import ParametersParserJson


##TOD
class MasterProduct(Singleton):
    # there is a hidden state of getting all routes to this class
    # state => wait command

    pid = None

    # get this params from Task Manager
    pid = None
    logger = None

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

        for product in products.to_json_list():

            state = {
                'requested_products': requested_products,
                'products': product,
                'parameters': parameter_manager.get_state()
            }
            state2save = json.dumps(state, sort_keys=True, indent=1)

            task = Task(
                command=Task.COMMAND_INSTALL,
                title=title,
                params=state2save,
                settings=json.dumps(settings, sort_keys=True, indent=1)
            )
            task.save()
        # production
        # For debug worker uncomment this
        # self.task.execute()
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

        # production

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
        return task.id
