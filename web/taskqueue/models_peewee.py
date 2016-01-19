# -*- coding: utf-8 -*-

import math
import logging
import json
from datetime import datetime

from core.core import Core
import datetime

# disable django db logger
logging.getLogger('django.db.backends').setLevel(logging.CRITICAL)
logging.getLogger('django.db.backends').propagate = False
import web.settings as Settings
import peewee

def connect_peewee():
    db = peewee.SqliteDatabase(Settings.DATABASES["default"]["NAME"], threadlocals=True)
    return db


# table of unique values and  keys we use it like a lock
class LocksPeewee(peewee.Model):
    title = peewee.CharField(max_length=100, null=False, unique=True)
    value = peewee.CharField(max_length=100, null=False)
    class Meta:
        db_table = 'taskqueue_locks'
        database = connect_peewee()


class TaskPeewee(peewee.Model):

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
    STATUS_EXCEPTION = 'exception'
    LOCK = "running"

    COMMAND_INSTALL = 'install'
    COMMAND_UPGRADE = 'upgrade'
    COMMAND_UNINSTALL = 'uninstall'

    created = peewee.DateTimeField(default=datetime.datetime.now)
    updated = peewee.DateTimeField(default=datetime.datetime.now)
    title = peewee.CharField(max_length=100)
    command = peewee.CharField(max_length=30)
    params = peewee.TextField()
    status = peewee.CharField(max_length=30, default=STATUS_PENDING)
    settings = peewee.TextField()
    parent_pid = peewee.IntegerField()
    pid = peewee.IntegerField()
    session = peewee.CharField(max_length=255)
    error_message = peewee.TextField()

    class Meta:
        db_table = 'taskqueue_task'
        database = connect_peewee()

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

    # HACK [ state['products'] ] in order do not rewrite ProductCollection Class
    # TODO it's not pretty solution
    def command_install(self):
        state = json.loads(self.params)
        Core.get_instance().install([state['products']], state['parameters'])

    def command_upgrade(self):
        state = json.loads(self.params)
        Core.get_instance().upgrade([state['products']], state.get('parameters'))

    def command_uninstall(self):
        state = json.loads(self.params)
        Core.get_instance().uninstall(state['products'], state.get('parameters'))

    def add_log(self, record):
        """
        добавить лог запись в базу данных

        :param record:
        """
        PeeweeLogMessage.create(
            task=self,
            level=record.levelname,
            source='{0}.{1}'.format(record.module, record.funcName),
            message=record.msg
        )

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


class PeeweeLogMessage(peewee.Model):
    """
    Представляет собой 1 лог запись (обычно строка) в базе данных
    """

    task = peewee.ForeignKeyField(TaskPeewee)
    created = peewee.DateTimeField(default=datetime.datetime.now)
    level = peewee.CharField(max_length=10)
    source = peewee.CharField(max_length=50)
    message = peewee.TextField()

    class Meta:
        db_table = 'taskqueue_logmessage'
        database = connect_peewee()

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
