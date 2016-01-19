# -*- coding: utf-8 -*-
import os


class OsApi(object):
    """
    Implements OS api for using in install_command for product.
    Instance with name 'os' is available in install_commands.
    OsApi is wrapper for core.api.windows.shell.WindowsShell.
    OsApi knows installing product and expands env variables in arguments.
    Example:
    os.cmd(...)
    os.chdir(...)
    """

    def __init__(self, core, product):
        self.core = core
        self.product = product

    def cmd(self, command, ignore_exit_code=False):
        """
        Executes command.
        """
        command = self.core.expandvars(command, product=self.product)
        log_path = self.core.log_manager.get_log_path(self.product, 'cmd')
        self.core.api.os.shell.cmd(command, log_path, ignore_exit_code)

    def delete_path(self, path):
        """
        Deletes path.
        """
        path = self.core.expandvars(path, self.product)
        self.core.api.os.shell.delete_path(path)

    def copy_file(self, source, dest):
        """
        Copies 'source' file to 'dest'.
        :param source:
        :param dest:
        :return:
        """
        source = self.core.expandvars(source, self.product)
        dest = self.core.expandvars(dest, self.product)
        self.core.api.os.shell.copy_file(source, dest)

    def append_file(self, source, dest):
        """
        Append content of 'source' file to 'dest'.
        """
        source = self.core.expandvars(source, self.product)
        dest = self.core.expandvars(dest, self.product)
        self.core.api.os.shell.append_file(source, dest)

    def un7zip(self, path, destination, source_internal_dir=None):
        """
        Extracts archive to 'destination' directory.
        :param path:
        :param destination:
        :param source_internal_dir: dir in archive to extract.
        """
        if not path:
            raise Exception("path does not specified")
        if not destination:
            raise Exception("destination does not specified")

        path = self.core.expandvars(path, self.product)
        destination = self.core.expandvars(destination, self.product)
        log_path = self.core.log_manager.get_log_path(self.product, 'cmd')
        self.core.api.os.shell.un7zip(path, destination, source_internal_dir, delete=False, log_path=log_path)

    def get_system_env(self, name):
        return self.core.api.os.registry.get_system_env(name)

    def set_system_env(self, name, value):
        self.core.api.os.registry.set_system_env(name, value)

    def remove_system_env(self, name):
        self.core.api.os.registry.remove_system_env(name)

    def chdir(self, path):
        """
        Changes current directory.
        """
        path = self.core.expandvars(path, self.product)
        self.core.api.os.shell.chdir(path)

    def make_dir(self, path):
        """
        Makes directories specified in 'path' if not exists.
        """
        path = self.core.expandvars(path, self.product)
        self.core.api.os.shell.make_dir(path)

    def path_exists(self, path)-> bool:
        """
        Check path exists.
        """
        path = self.core.expandvars(path, self.product)
        return os.path.exists(path)

    def path_join(self, *paths):
        """
        Joins list of paths into single string.
        """
        return os.path.join(*[self.core.expandvars(path, self.product) for path in paths])

    def read_file(self, path):
        """
        Returns file content.
        """
        path = self.core.expandvars(path, self.product)
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return f.read()
        except:
            pass
        return None

    def replace_in_file(self, path, pattern, replace):
        """
        Replaces text in file specified in 'path' with 'pattern' to 'replace'.
        :param path:
        :param pattern: text or regexp object to search
        :param replace:
        :return:
        """
        path = self.core.expandvars(path, self.product)
        return self.core.api.os.shell.replace_in_file(path, pattern, replace)