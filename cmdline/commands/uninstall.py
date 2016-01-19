# -*- coding: utf-8 -*-

from core.core import Core
from core.parameters_parser import ParametersParserStr


class UninstallCommandError(Exception):
    pass


class UninstallCommand(object):
    """
    Helper class to uninstall products from cmd line
    """
    def __init__(self, product_names, args_parameters=None):
        if not product_names:
            raise UninstallCommandError('no products specified')

        self.core = Core.get_instance()
        self.product_names = product_names
        self.args_parameters = args_parameters

    def do(self):
        """
        Do uninstall
        """
        # get uninstall parameters from parsed cmd line args
        parameters = ParametersParserStr(self.args_parameters).get()
        # call uninstall
        self.core.uninstall(self.product_names, parameters)