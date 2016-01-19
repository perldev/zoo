# -*- coding: utf-8 -*-

import os
import os.path
import platform
import yaml
import logging
from collections import OrderedDict

from core.helpers.yaml_helper import YamlHelper
from core.version import VERSION


# главный фид, он не появляется в настрофках в морде, он тут захардкожен
MAIN_FEED = 'http://ci-helicontech/zoo4/feed.yaml'
try:
    # возможность переопределить главный фид
    # фича для разработчика в модуле local_feed
    import local_feed
    MAIN_FEED = local_feed.MAIN_FEED
except:
    pass


class Settings(object):
    """
    Класс который умеет загружать, хранить и отдавать настройки ядра.
    """

    # статический экземпляр
    _instance = None

    @classmethod
    def get_instance(cls):
        return cls._instance

    # путь по умолчанию к файлу с настройками
    DEFUALT_SETTINGS_FILE = os.path.normpath(os.path.join(os.path.dirname(__file__), '..\..\etc\settings.yaml'))

    @classmethod
    def load_from_file(cls, yaml_path=None):
        """
        Загружает файл настроек и возвращает объект настроек Settings.
        :rtype : Settings
        """
        path = yaml_path or cls.DEFUALT_SETTINGS_FILE
        if os.path.exists(path):
            # файл существует
            logging.debug('settings file: {0}'.format(path))
            # загружаем ямл и десериализуем его
            with open(path, 'r') as f:
                data = yaml.load(f)
        else:
            logging.warning('settings file {0} not found, continue with empty settings'.format(path))
            data = {}
        data['path'] = path
        return Settings(**data)

    def __init__(self, **kwargs):
        """
        Конструктор настроек.
        :param kwargs: словарь с настройками, обычно загруженный из файла или взятый из старого ядра при пересоздания ядраю
        """

        if 'path' in kwargs:
            # сохраним путь к файлу с настройками
            self.path = kwargs['path']
            del kwargs['path']

        # запомним оргинальный словарь с настройками
        self.source = OrderedDict(kwargs)

        uname = platform.uname()

        # корень проекта
        self.root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..\..'))
        # диретория кеша
        self.cache_path = os.path.join(self.root, kwargs.get('cache_path', 'cache'))
        # директория кеша
        self.logs_path = os.path.join(self.root, kwargs.get('logs_path', 'logs'))
        self.tmp_logs_path = os.path.join(self.root, kwargs.get('tmp_logs_path', 'tmp'))
        self.supervisor_logpath =os.path.join(self.root, kwargs.get('tmp_logs_path', 'supervisor.log'))
        # диктория для хранения ямлов (installed-history, current, ...)
        self.storage_path = os.path.join(self.root, kwargs.get('storage_path', 'data'))
        # урлы фидов
        self.urls = [MAIN_FEED]
        self.urls.extend(kwargs.get('urls') or [])
        # ос, может задавать в настройках, но обычно нет
        self.os = kwargs.get('os', uname.system.lower())
        # версия ос, может задавать в настройках, но обычно нет
        self.os_version = kwargs.get('os_version', uname.version)
        # битность, может задавать в настройках, но обычно нет
        self.bitness = kwargs.get('bitness', '64' if uname.machine.find('64') > 0 else '32')
        # веб сервер
        self.webserver = kwargs.get('webserver')
        # язык
        self.lang = kwargs.get('lang')
        # пути к yaml-файлам
        self.installed_feed = os.path.join(self.storage_path, 'install-history.yaml')
        self.engines_feed = os.path.join(self.storage_path, 'engines-{0}.yaml'.format(self.webserver))
        self.current_feed = os.path.join(self.storage_path, 'current.yaml')
        # директория, куда ставятся все продукты
        self.zoo_home = kwargs.get('zoo_home')
        # наша версия
        self.version = VERSION

        # создадим папки, если еще не
        self.assert_exist(self.storage_path)
        self.assert_exist(self.cache_path)
        self.assert_exist(self.logs_path)

        Settings._instance = self

    def __repr__(self):
        return '{0}'.format(self.get_state())

    def get_platform(self):
        """
        Создаёт и возвращает объект Платформы.
        """
        from .models.platform import Platform
        return Platform(os=self.os,
                        bitness=self.bitness,
                        os_version=self.os_version,
                        lang=self.lang,
                        web_server=self.webserver)

    def get_state(self):
        """
        Сериализует настройки для дальнейшего сохранения в файл или передачи в json.
        """
        return {
            'version': self.version,
            'root': self.root,
            'cache_path': self.cache_path,
            'logs_path': self.logs_path,
            'storage_path': self.storage_path,
            'urls': self.urls,
            'os': self.os,
            'os_version': self.os_version,
            'bitness': self.bitness,
            'webserver': self.webserver,
            'lang': self.lang,
            'zoo_home': self.zoo_home
        }

    def to_dict(self):
        """
        Алиас для get_state, только возвращает упорядоченный словарь.
        """
        return OrderedDict(self.source)

    def update(self, values):
        """
        Обновляет настройкию
        :param values: словарь с настройкаи, которые нужно обновить.
        """
        data = OrderedDict(values)

        # fix empty url
        if 'urls' in data:
            data['urls'] = [url for url in data['urls'] if url]

        # fix empty strings to null
        for key, val in data.items():
            if val == '':
                data[key] = None

        source = OrderedDict(self.source, path=self.path)
        source.update(data)
        self.__init__(**source)

    def save(self):
        """
        Сохраняет настройки в файл.
        """
        self.assert_exist(os.path.dirname(self.path))
        YamlHelper.save(self.source, self.path)

    def format(self):
        """
        Форматирует настройки для вывода строкой как yaml.
        """
        return yaml.dump(self.get_state())

    @staticmethod
    def assert_exist(path):
        """
        Создаёт диреткорию с настройками, если её ещё нет.
        """
        os.makedirs(path, exist_ok=True)