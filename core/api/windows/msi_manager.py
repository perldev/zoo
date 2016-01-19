from core.core import Core


class MsiManager(object):
    """
    Api to install or uninstall MSI
    """

    @staticmethod
    def install(filename, log_path, optional_parameters: dict=None, ignore_exit_code=False, no_wait=False):
        """
        Install MSI with options
        :param filename:
        :param log_path:
        :param optional_parameters:
        :param ignore_exit_code:
        :param no_wait:
        """
        command = 'msiexec.exe /norestart /q /i "{0}" /log "{1}" ALLUSERS=1'.format(filename, log_path)
        if optional_parameters:
            for k, v in optional_parameters.items():
                if v and v != "":
                    command += ' {0}="{1}"'.format(k, v)

        return Core.get_instance().api.os.shell.cmd(command, ignore_exit_code=ignore_exit_code, no_wait=no_wait)

    @staticmethod
    def uninstall(filename, log_path, ignore_exit_code=False):
        """
        Uninstall MSI with options
        :param filename:
        :param log_path:
        :param ignore_exit_code:
        :return:
        """
        command = 'msiexec.exe /norestart /q /X "{0}" /log "{1}"'.format(filename, log_path)
        return Core.get_instance().api.os.shell.cmd(command, ignore_exit_code=ignore_exit_code)

