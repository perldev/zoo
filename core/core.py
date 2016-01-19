# -*- coding: utf-8 -*-

import logging
import os
import os.path

from core.models.installed_product import InstalledProductInfo
from .log_manager import LogManager
from .error_manager import ErrorManager


class Core:

    """
    Объект этого класса — главный в проекте. Он создаёт и хранит в себе
    все коллекции продуктов (feed, current, install_history),
    умеет выполнять ключевые действия: install, upgrade, uninstall, sync.
    Объект этого класса создаётся один на процесс, хранится в статической переменной _instance.
    Умеет создавать этот объект CoreLoader.
    """

    # статический экземпляр этого класса, всегда один
    # доступ к нему только через Core.get_instance()
    _instance = None

    @classmethod
    def get_instance(cls):
        """
        Возвращает экземпляр ядра, если оно создано.
        :rtype : Core
        """
        if not cls._instance:
            raise RuntimeError('core is not created')
        return cls._instance

    @classmethod
    def is_created(cls):
        """
        Создано ли ядро?
        :rtype : bool
        """
        return cls._instance is not None

    @classmethod
    def create_instance(cls, settings=None, settings_path=None):
        """
        Создаёт и возвращает объект ядра с настройками из объекта settings или из файла по settings_path.
        :rtype : Core
        """
        logging.debug('creating core instance')
        cls._instance = Core(settings, settings_path)
        logging.debug('core created: {0}'.format(cls._instance))
        return cls._instance

    @classmethod
    def drop_instance(cls):
        """
        Удалять объект ядра, использовется, когда нужно пересоздать ядро для новых настроек.
        :return:
        """
        cls._instance = None

    def __init__(self, settings=None, settings_path=None):
        """
        Конструктор ядра.
        :param settings: объект Settings или dict с настройками ядра.
        :param settings_path: путь к файлу с настройками.
        """
        from .api_manager import ApiManager
        from .env_manager import EnvManager
        from .settings import Settings
        from .storage import Storage

        if settings:
            if isinstance(settings, Settings):
                # если настройки передали в виде готового объекта Settings
                # используем его
                self.settings = settings
            else:
                # иначе создаем из словаря
                self.settings = Settings(**settings)
        else:
            # загружаем настройки из файла
            self.settings = Settings.load_from_file(settings_path)

        # печатаем настройки
        logging.info('settings:\n{0}'.format(self.settings.format()))

        # запомним объект платформы, он хранит в себе ос, версию, битность, веб-сервер
        # по нему мы фильтруем объекты из фида
        self.platform = self.settings.get_platform()
        # помощник для добавлять, хранить и удалять переменные окружения
        self.envs = EnvManager()
        # помощник, который умеет получать и создавать директории и пути для логов установки продуктов
        self.log_manager = LogManager.get_instance(self)
        # коллекция полезных АПИ
        self.api = ApiManager(self)

        # можно ли задавать волпросы пользователю из zoocmd
        self.interactive = False
        # коллекции продуктов устарели и их нужно обновить
        self.expired = True

        # коллекция ошибок, который случились во время загрузки ядра и фидов
        self.error_manager = ErrorManager()

        # установить полезные переменные окружения
        self.set_envs()

        # feed of products found with sync
        # коллекция продуктов найденных во время синка, сохраняется в current.yaml
        # доступ к продуктам это коллекции осуществляется через core.current,
        # который есть core.current_storage.feed
        self.current_storage = Storage(self, self.settings.current_feed)

        # коллекция продуктов, которые были установлены через зу,
        # живёт в файле installed-history.yaml
        self.installed_storage = Storage(self, self.settings.installed_feed)

        # коллекция устновленных продкутов-энжинов,
        # живёт в engines-<webserver>.yaml
        self.engine_storage = Storage(self, self.settings.engines_feed)

        # Сырая коллекция продуктов загружженых из фидов
        # это ленивый объект, он создастся (и загрузяться фиды) при первом обращении к core.feed
        self._feed = None

    def __repr__(self):
        return 'Core(platform={0})'.format(self.platform)

    def set_settings(self, values: dict):
        """
        Устновить настройки и сохранить, используется для установки настроек из командной строки.
        """
        self.settings.update(values)
        self.settings.save()

    def load_feeds(self):
        """
        Загружает фиды из урлов, указанных в настройках.
        Урл главного фида захардкожен.
        """
        logging.debug('Loading feeds: {0}'.format(self.settings.urls))
        self.feed.load(*self.settings.urls)
        self.set_expired(False)

    def get_feed(self):
        """
        Создаёт ленививый объект core.feed, когда к нему обращаются и загружает фиды.
        :rtype : core.feed.Feed
        """
        from .feed import Feed
        if not self._feed:
            self._feed = Feed(self, self.platform)
            self.load_feeds()

        return self._feed

    # обёртка для создания ленивого объекта
    feed = property(get_feed)

    def get_current(self):
        return self.current_storage.feed

    # свойство для короткого доступа к core.current_stotage.feed
    current = property(get_current)

    @staticmethod
    def set_envs():
        """
        Устанавливает переменные окружения ProgramFiles(x86) и ProgramFiles(x64)
        """
        os.environ.setdefault('ProgramFiles(x86)', os.path.expandvars(os.environ['ProgramFiles']))
        os.environ.setdefault('ProgramFiles(x64)',
                              os.path.expandvars(os.environ.get('ProgramW6432', os.environ['ProgramFiles'])))

    def expandvars(self, value, product=None):
        """
        разворачивает переменные окружения с учётом продукта и его переменных окружения.
        """
        result = value
        result = self.envs.expandvars(result)
        if product:
            result = product.envs.expandvars(result)
        result = os.path.expandvars(result)

        if result.find("%") != -1:
            if result != value:
                result = self.expandvars(result)

        return result

    def update_environment_vars(self):
        """
        Обновляет переменную процесса PATH из реестра.
        """
        os.environ['PATH'] = self.api.os.registry.get_system_path()

    def set_expired(self, expired: bool):
        """
        Устанавливает устарело ли ядро.
        Вызывается после установки/удаления для обновить коллекции продуктов.
        """
        logging.debug('core set expired' if expired else 'core set updated')
        self.expired = expired

    def update(self, force=False):
        """
        Обновляет все коллекции продуктов и вызывает синк, если ядро устарело.
        """
        self.get_feed()
        if self.expired or force:
            logging.debug('updating expired core')
            # перезагружает фиды
            self.feed.update()
            # перезагружает current.yaml
            self.current_storage.update()
            # перезагружает installed-history.yaml
            self.installed_storage.update()
            # перезагружает engines.yaml
            self.engine_storage.update()
            # Slava: make sync after every install/upgrade/uninstall
            # делает синк
            self.sync()
            self.set_expired(False)

    def has_upgrade(self)-> bool:
        """
        Проверяет, есть ли новая версия себя в фиде.
        Используется для показать в морде, что есть апгрейд.
        """
        zoo_product = self.feed.get_product('Helicon.Zoo')
        if zoo_product is None:
            return None
        installed_version = zoo_product.get_installed_version()
        if installed_version:
            return zoo_product.version if zoo_product.has_upgrade() else None
        else:
            return True

    def get_cache_size(self):
        """
        Возвращает размер директории с кешем.
        """
        cache_path = self.settings.cache_path
        return self.api.os.shell.dir_size(cache_path)

    def clear_cache(self):
        """
        Очищает директорию с кешем.
        """
        logging.info('Clearing cache')
        cache_path = self.settings.cache_path
        self.api.os.shell.delete_path(cache_path)
        self.api.os.shell.make_dir(cache_path)

    def get_logs_size(self):
        """
        Возвращает размер директории с логами.
        """
        logs_path = self.settings.logs_path
        return self.api.os.shell.dir_size(logs_path)

    def clear_logs(self):
        """
        Очищает директорию с логами.
        """
        logging.info('Clearing logs')
        logs_path = self.settings.logs_path
        self.api.os.shell.delete_path(logs_path)
        self.api.os.shell.make_dir(logs_path)

    def set_product_installed(self, product, parameters):
        """
        Записывает в коллекции, что продукт установлен.
        """
        from .models.engine import Engine
        from .models.application import Application
        from .models.product import Product

        if isinstance(product, Application):
            # устновленные приложения никуда не записывать.
            return

        logging.debug('set {0} installed'.format(product))
        # запомним установденную версию
        product.installed_version = product.version

        if isinstance(product, Engine):
            # энжэин сохраним в коллекцию энжинов
            self.engine_storage.set_product_installed(product, parameters)
        elif isinstance(product, Product):
            # продукт сохраним в installed-history
            self.installed_storage.set_product_installed(product, parameters)

        # и в current.yaml сохраним
        self.current_storage.set_product_installed(product, parameters)

    def set_product_uninstalled(self, product):
        """
        Удалим из коллекций деинсталиированный продукт.
        """
        from .models.engine import Engine
        from .models.application import Application
        from .models.product import Product

        if isinstance(product, Application):
            # приложение ниоткуда не удаляем
            return

        logging.debug('set {0} uninstalled'.format(product))

        if isinstance(product, Engine):
            # энжин из энжинов
            self.engine_storage.set_product_uninstalled(product)
        elif isinstance(product, Product):
            # продукт из installed-history.yaml
            self.installed_storage.set_product_uninstalled(product)

        # и из current.yaml
        self.current_storage.set_product_uninstalled(product)

    def install(self, product_names, parameters: dict, with_dependencies=False):
        """
        Устанавливает продукты.
        :param product_names: список имён продуктов для установки, может быть с версиями.
        :param parameters: переметры для установки.
        :param with_dependencies: нужно ли ставить зависимости?
        :return: словарь с результатами.
        """
        from .dependency_manager import DependencyManager
        from .install_manager import InstallManager
        from .parameters_manager import ParametersManager
        from .product_collection import ProductCollection

        print('products requested to install: {0}'.format(product_names))
        # создаём коллекцию продуктов по их именами
        # продукты ищем в фиде и в текущих
        products = ProductCollection(product_names, feeds=(self.feed, self.current), ready_json=True )

        # разруливатель зависимостей
        dependency_manager = DependencyManager()

        with_dependencies = with_dependencies or (parameters.get('with-dependencies', "False").lower() == "true")
        if with_dependencies and False:
            # если нужно ставить с зависимости (из консоли нужно), найдём все неустановленные
            products = dependency_manager.get_products_with_dependencies(products)
            products.reverse()

        # удалим установленные приложения из коллекции
       #products = dependency_manager.remove_installed(products, strict_version=False)

        if products and len(products) > 0:

            logging.info('Going to install with:')
            logging.info('  products: {0}'.format(products.to_dict()))
            logging.info('  parameters: {0}'.format(parameters))

            # создаем менеджер инсталляций
            install_manager = InstallManager(products)
            # менеджер параметров
            parameters_manager = ParametersManager(products, parameters)

            if not parameters_manager.are_all_parameters_filled():
                # если не все параметры заданы
                if self.interactive:
                    # и можно спрашивать у пользователя - то спросим
                    parameters_manager.ask_unfilled_parameters()
                else:
                    # спрашивать нельзя — падаем с ошибкой
                    parameters_manager.raise_parameters_error()

            # запускаем инсталляцию
            install_manager.pm = parameters_manager
            install_manager.install()

        # результат установки
        result = dict()
        result["status"] = "OK"
        result["products"] = products.to_dict()
        result["parameters"] = parameters
        result["settings"] = self.settings.get_state()

        logging.info("All products have been installed\n")

        return result

    def upgrade(self, product_names, parameters: dict):
        """
        Апгрейдит продукты. Апгрейд работает пока плохо, т.к. не всё продукты умеют апгрейдится,
        не для всех есть апгрейд команды, не понятно как разруливать зависимости.
        В целом работает так же как и install()
        :param product_names: список имён продуктов для апгрейда
        :param parameters: параметры для апгрейда
        :return:
        """
        from .install_manager import InstallManager
        from .parameters_manager import ParametersManager
        from .product_collection import ProductCollection

        # из списка имён создаём коллекцию продуктов
        products = ProductCollection(product_names)

        if products and len(products) > 0:
            logging.info('Going to upgrade with:')
            logging.info('  products: {0}'.format(products.to_dict()))
            logging.info('  parameters: {0}'.format(parameters))

            # создаём менеджер инсталляций и параметров
            install_manager = InstallManager(products)
            parameters_manager = ParametersManager(products, parameters)

            # спрашиваем переметры, если можем
            if not parameters_manager.are_all_parameters_filled():
                if self.interactive:
                    parameters_manager.ask_unfilled_parameters()
                else:
                    parameters_manager.raise_parameters_error()

            # запускаем апгрейд
            install_manager.pm = parameters_manager
            install_manager.upgrade()

        # результат
        result = dict()
        result["status"] = "OK"
        result["products"] = products.to_dict()
        result["parameters"] = parameters
        result["settings"] = self.settings.get_state()

        logging.info("All products have been upgraded")

        return result

    def uninstall(self, product_names, parameters: dict=None):
        """
        Деинсталлирует продукты.
        :param product_names: списко имён продуктов для удаления
        :param parameters: параметры
        :return:
        """
        from .dependency_manager import DependencyManager
        from .install_manager import InstallManager
        from .product_collection import ProductCollection

        dm = DependencyManager()
        # создаём коллекцию продуктов из списка имён, ищём продукты в текущих
        products = ProductCollection(product_names, feed=self.current_storage.feed)
        # удаляем не установленные
        products = dm.remove_not_installed(products)

        logging.info('Going to uninstall with:')
        logging.info('  products: {0}'.format(products.to_dict()))
        logging.info('  parameters: {0}'.format(parameters))

        # создаём менеджер и запускаем деинсталляцию
        install_manager = InstallManager(products)
        install_manager.uninstall()

        # результат
        result = dict()
        result["status"] = "OK"
        result["products"] = products.to_dict()
        result["parameters"] = parameters
        result["settings"] = self.settings.get_state()

        logging.info("\nAll products have been uninstalled\n")

        return result

    def sync(self):
        """
        Ищёт установденные продукты и сохраняем их в current.yaml

        """
        logging.info('search installed products')

        from .models.engine import Engine
        from .models.application import Application
        from .install_manager import KnownParameters

        # очищаем текущие
        current_feed = self.current_storage.feed
        current_feed.clear()

        # цикл по всем фидам, что у нас есть: фид, энжины, история инсталляций
        for feed in (self.installed_storage.feed, self.engine_storage.feed, self.feed):
            # коллекция продуктов для каждого фида
            products = feed.get_products()
            # цикл по прдуктам
            for product in products:
                try:
                    if isinstance(product, Application):
                        # с приложениями ничего не делаем
                        continue

                    if isinstance(product, Engine):
                        # энжины ищем в engines.yaml
                        if self.engine_storage.is_product_installed(product.name):
                            # если энжин есть в engines.yaml - сохраняем его в текущих
                            current_feed.add_raw_item(product.to_dict())
                            #if not self.feed.has_product(product.name, product.version):
                            #    self.feed.add_raw_item(product.to_dict())
                    else:
                        # это продукт

                        # вызовем команду продукта для поискать себя
                        installed_product_info = product.find_installed()

                        # проверим, что вернулось нужного типа
                        if installed_product_info and not isinstance(installed_product_info, InstalledProductInfo):
                            raise TypeError("Not InstalledProduct instance: {0} for {1}".format(installed_product_info, product))

                        # если что надо
                        if installed_product_info \
                                and isinstance(installed_product_info, InstalledProductInfo) \
                                and installed_product_info.version:

                            # поищем в фиде продукт с найденой версией
                            strict_product = self.feed.get_product('{0}=={1}'.format(product.name, installed_product_info.version))
                            if not strict_product:
                                # если в фиде на нашлось, поищем в инсталл хистори
                                strict_product = self.installed_storage.feed.get_product('{0}=={1}'.format(product.name, installed_product_info.version))

                            if strict_product:
                                # нашёлся продукт в такой же версией
                                logging.debug('{0}: found with the same version'.format(product))
                                # запомним инсталл директорию
                                strict_product.parameters[KnownParameters.INSTALL_DIR.value] = installed_product_info.install_dir
                                # запомним установленную версию
                                strict_product.installed_version = installed_product_info.version
                                # сохраним в текущих
                                current_feed.add_raw_item(strict_product.to_dict())
                            else:
                                # продукт с такой же версией не нашёлся
                                logging.debug('{0}: found with unknown version {1}'.format(product, installed_product_info.version))

                                # ???
                                product.version = installed_product_info.version

                                # запомним установленную версию
                                product.installed_version = installed_product_info.version
                                # очистим файлы, команды инсталляции и деинсталляции
                                # найденные продукты с неизвестной версией мы не можем удалять и ставить
                                #product.files = []
                                #product.install_command = None
                                #product.uninstall_command = None
                                # запомним установленную версию
                                product.parameters[KnownParameters.INSTALL_DIR.value] = installed_product_info.install_dir
                                # сохраним в текущих
                                current_feed.add_raw_item(product.to_dict())
                        else:
                            # продукт не установлен
                            logging.debug('{0}: not found'.format(product))
                except Exception as ex:
                    # ошибка во время синка, случаться не должна в нормальнойм режиме
                    raise Exception('Sync on {0} failed'.format(product)) from ex

        # сохраним current.yaml
        self.current_storage.save()

        # напечатаем список найденных продуктов
        for product in self.current_storage.feed.get_products():
            logging.info('{0:30} {1:30} {2}'.format(
                product.name,
                product.get_installed_version(),
                product.parameters.get('install_dir') or '-'
            ))
