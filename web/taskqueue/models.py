# -*- coding: utf-8 -*-

import math
import logging
import json
from datetime import datetime

from django.db import models
from django.db import connection

from core.core import Core
from cmdline.commands.list import ListProductsCommand
import datetime

# disable django db logger
connection.use_debug_cursor = False
logging.getLogger('django.db.backends').setLevel(logging.CRITICAL)
logging.getLogger('django.db.backends').propagate = False


# table of unique values and  keys we use it like a lock
class Locks(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False, unique=True)
    value = models.CharField(max_length=100, blank=False, null=False)



class Task(models.Model):
    """
    Задание на установку или удаление
    Сохраняет свое состояние в базе данных

    UI - создает его,
    воркер - читает и выполняет
    воркер обновляет статутс
    UI - показывает что задние выболнено, или ошибка

    для задания которое выполнялось, есть логи, они хранятся в LogMessage
    """

    STATUS_PENDING = 'pending'
    STATUS_RUNNING = 'running'
    STATUS_DONE = 'done'
    STATUS_FAILED = 'failed'

    COMMAND_INSTALL = 'install'
    COMMAND_UPGRADE = 'upgrade'
    COMMAND_UNINSTALL = 'uninstall'

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=100, blank=False, null=False)
    command = models.CharField(max_length=30)
    parent_pid = models.IntegerField(null=True, blank=True)
    pid = models.IntegerField(null=True, blank=True)
    session = models.CharField(max_length=255, null=True, blank=True)

    params = models.TextField()
    status = models.CharField(max_length=30, default=STATUS_PENDING)
    settings = models.TextField()
    error_message = models.TextField(null=True, blank=True)

    def execute(self):
        """
        выполнить это задание, в этом процеесе
        выбрать параметре
        выбрать метод
        вывать у ядра нужный метод с параметрами
        ждать пока доделает

        это длинный и блокирующий метод, должен вызываться или из консоли, или из воркера
        никонгда из UI

        :raise ValueError:
        """
        if self.command == self.COMMAND_INSTALL:
            logging.debug("ok everything good i'm going to install")
            self.command_install()

        elif self.command == self.COMMAND_UPGRADE:
            self.command_upgrade()
        elif self.command == self.COMMAND_UNINSTALL:
            self.command_uninstall()
        else:
            raise ValueError('Invalid task command: {0}'.format(self.command))

    def command_install(self):
        state = json.loads(self.params)
        Core.get_instance().install(state['products'], state['parameters'])

    def command_upgrade(self):
        state = json.loads(self.params)
        Core.get_instance().upgrade(state['products'], state.get('parameters'))

    def command_uninstall(self):
        state = json.loads(self.params)
        Core.get_instance().uninstall(state['products'], state.get('parameters'))

    def add_log(self, record):
        """
        добавить лог запись в базу данных

        :param record:
        """
        LogMessage(
            task=self,
            level=record.levelname,
            source='{0}.{1}'.format(record.module, record.funcName),
            message=record.msg
        ).save()

    def get_logs(self, since):
        """
        :param since: str or int unix time to filter log messages
        :return: list of log message objects
        """
        log_messages = self.logmessage_set.all()
        if since:
            if isinstance(since, str):
                since = str_timestamp_to_datetime(since)
            log_messages = log_messages.filter(created__gt=since)

        return [lm for lm in log_messages]

    def to_dict(self):
        """
        для сериализации в json

        :return:
        """
        return {
            'id': self.id,
            'created': self.created.isoformat(),
            'updated': self.updated.isoformat(),
            'title': self.title,
            'command': self.command,
            'params': json.loads(self.params) if self.params else None,
            'params_str': self.params,
            'status': self.status,
            'error_message': self.error_message,
            'is_finished': True if self.status in (self.STATUS_DONE, self.STATUS_FAILED) else False
        }

    class Meta:
        ordering = ('-created',)





class LogMessage(models.Model):
    """
    Представляет собой 1 лог запись (обычно строка) в базе данных
    """

    task = models.ForeignKey(Task)
    created = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=10)
    source = models.CharField(max_length=50)
    message = models.TextField()

    class Meta:
        ordering = ('created',)

    def to_dict(self):
        return {
            'created': self.created.timestamp(),
            'level': self.level,
            'source': self.source,
            'message': self.message
        }


def str_timestamp_to_datetime(s):
    f = float(s)
    f += 0.0000005
    result = datetime.fromtimestamp(f)
    return result
