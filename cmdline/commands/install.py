# -*- coding: utf-8 -*-

from core.core import Core
from core.parameters_parser import ParametersParserStr


class InstallCommandError(Exception):
    pass


class InstallCommand(object):
    """
    install command wrapper class
    """

    def __init__(self, product_names: list, args_parameters: dict=None):
        """
        initialize install wrapper
        :param product_names: list or products names
        :param args_parameters: dict of install parameters
        """
        if not product_names:
            raise InstallCommandError('no products specified')

        self.core = Core.get_instance()
        self.product_names = product_names
        self.args_parameters = args_parameters

    def do(self):
        """
        Install products by Core
        """
        parameters = ParametersParserStr(self.args_parameters).get()
        self.core.install(self.product_names, parameters, with_dependencies=True)



