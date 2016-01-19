# -*- coding: utf-8 -*-

import logging


class WindowsFeature():
    """
    Api to install or uninstall windows features (IIS, .Net, ...)
    """

    DISM_EXE = '%SystemRoot%\\Sysnative\\dism.exe'

    def __init__(self, core):
        self.core = core
        self.dism_exe = self.core.expandvars(self.DISM_EXE)

    def install(self, name):
        """
        Install Windows feature
        :param name: feature name
        """
        logging.info("Install windows feature: '{0}'".format(name))
        return self.core.api.os.shell.cmd('{0} /Online /NoRestart /Enable-Feature /FeatureName:{1}'.format(self.dism_exe, name))

    def uninstall(self, name):
        """
        Uninstall Windows feature
        :param name: feature name
        """
        logging.info("Uninstall windows feature: '{0}'".format(name))
        return self.core.api.os.shell.cmd("{0} /Online /NoRestart /Disable-Feature /FeatureName:{1}".format(self.dism_exe, name), ignore_exit_code=True)


