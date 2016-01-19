# -*- coding: utf-8 -*-

import logging
from collections import OrderedDict

from core.dependency_manager import DependencyManager
from core.models.engine import Engine
from core.models.base_product import BaseProduct, ProductNotFoundError
from core.parameters_manager import KnownParameters


class Application(BaseProduct):
    """
    Represents Application (product type).
    See BaseProduct class for comments.
    Differences from BaseProduct:
    - additional attrs: engines, database_type, start_page
    - creating .zoo file after installation
    - manage engines
    """

    def __init__(self, core, attrs = None):
        super().__init__(core, attrs)
        self.iis = self.core.api.os.web_server
        # supported engines with configs
        self.engines = {}
        # list of supported database types
        self.database_type = []
        # start page that we need show after installation
        self.start_page = None
        self.selected_engine = None

    def get_typename(self):
        return 'application'

    def merge(self, **kwargs):
        super().merge(**kwargs)
        # merge additional fields
        self.engines = kwargs.get('engines') or self.engines
        self.database_type = kwargs.get('database_type') or self.database_type
        self.start_page = kwargs.get('start_page') or self.start_page

    def __getstate__(self):
        result = super().__getstate__()
        # additional fields
        result['engines'] = self.engines
        result['database_type'] = self.database_type
        result['start_page'] = self.start_page
        return result

    def install(self, parameters):
        """
        Installs application.
        Creates .zoo file with zoo app config.
        """
        result = super().install(parameters)
        if not result:
            return False

        self.create_zoo_file(parameters[KnownParameters.PHYSICAL_PATH.value], parameters)
        return True

    def create_zoo_file(self, physical_path, parameters):
        """
        Creates and saves .zoo config for installed zoo app.
        :param physical_path:
        :param parameters:
        :return:
        """
        # get engine
        engine = self.get_selected_engine()
        # get engine config
        engine_config = self.get_settings_for_engine(engine)

        # .zoo file data
        config = OrderedDict(engine_config)
        # set app enabled
        config['state'] = 'enabled'
        # save application representation
        config['application'] = self.to_dict(rich=True)
        # save install paramerters
        config['parameters'] = parameters
        # save .zoo file
        self.iis.create_zoo_config(physical_path, config)

    def set_select_engine(self, engine):
        """
        Sets engine for zoo app, this engine will be saved in .zoo file.
        This method is called by installed_manager to set zoo app engine.
        Real engine selection appears in Core.install() on 'engine = dependency_manager.get_engine(products)'
        :type engine: core.models.engine.Engine
        """
        if engine is None:
            raise Exception("can't set engine, engine is null")
        logging.info('Engine {0} selected for {1}'.format(engine, self))
        self.selected_engine = engine

    def get_selected_engine(self):
        """
        Returns selected engine for zoo app.
        """
        if not isinstance(self.selected_engine, Engine):
            raise ProductNotFoundError("Can\'t find selected engine '{0}' for '{1}'".format(self.selected_engine, self.name))
        return self.selected_engine

    def get_settings_for_engine(self, engine_object)-> OrderedDict:
        """
        Returns OrderedDict with settings for engine.
        This settings will be saved in .zoo file.
        """
        name = engine_object.name
        result = OrderedDict()
        if self.engines:
            for app_engine in self.engines:
                if app_engine['engine'].lower() == name.lower():
                    result = app_engine
                    return result

        logging.warning("Can't find engine '{0}'".format(name))
        return result
