# -*- coding: utf-8 -*-

import os
import logging
import shutil
import re
import sys
import subprocess
import win32api


class WindowsShell(object):
    """
    Windows shell api: executing command, handling files and folder, extracting archives.
    """

    ROOT = ''

    def __init__(self, root):
        WindowsShell.ROOT = root

    @staticmethod
    def cmd(command, log_path=None, ignore_exit_code=False, envs=None, no_wait=False):
        """
        Run command via subprocess and return exit code
        """
        logging.info('> {0}'.format(command))

        process = subprocess.Popen(command, env=envs)

        # exit if do not need to wait process
        if no_wait:
            return 0

        process.wait()
        exit_code = process.returncode

        if exit_code != 0 and not ignore_exit_code:
            # raise error if exit code is not 0
            raise RuntimeError('Execute of command "{0}" failed with status {1}'.format(command, exit_code))

        return exit_code

    @staticmethod
    def get_cmd_output(command):
        """
        Executes command and return output
        """
        logging.debug(command)
        return subprocess.check_output(command)

    @staticmethod
    def un7zip(source_filename, target_dir, source_internal_dir=None, delete: bool=False, log_path=None):
        """
        Unzip file to target_dir.
        :param source_filename: source arhcive file (.zip or .7z)
        :param target_dir: dir to extract
        :param source_internal_dir: directory in archive to extract
        :param delete: delete or not archive after extract
        :param log_path: log file name
        """
        WindowsShell.cmd('{0} x "{1}" {2} "-o{3}" -y'.format(
            os.path.join(WindowsShell.ROOT, r'bin\7za.exe'),
            source_filename, source_internal_dir or '', target_dir), log_path=log_path)

        if source_internal_dir:
            WindowsShell.move_dir(os.path.join(target_dir, source_internal_dir), target_dir, log_path=log_path)

        if delete:
            WindowsShell.delete_path(source_filename)

    @staticmethod
    def move_dir(src, dest, log_path=None):
        """
        Move 'src' directory to 'dest'.
        """
        WindowsShell.cmd('XCOPY "{0}" "{1}" /S /E /Y'.format(src, dest), log_path=log_path)
        WindowsShell.delete_path(src)

    @staticmethod
    def ensure_exists(source_filename):
        """
        Raises error if source_filename is not exist.
        """
        return  os.path.isfile(source_filename)

    @staticmethod
    def delete_path(path):
        """
        Deletes file ot folder specified in path. Ignores any errors.
        :param path: file or folder
        """
        logging.debug("Delete path '%s'", path)
        try:
            shutil.rmtree(path)
            return
        except Exception:
            pass
        try:
            os.remove(path)
        except Exception:
            pass

    @staticmethod
    def get_file_version(filename, parts=None):
        """
        Returns version of win-executable file.
        :param filename:
        :param parts: Number of version parts to return
        """
        logging.debug(filename)
        try:
            info = win32api.GetFileVersionInfo(filename, "\\")
            ms = info['FileVersionMS']
            ls = info['FileVersionLS']
            if parts == 1:
                return "{0}".format(win32api.HIWORD(ms))
            if parts == 2:
                return "{0}.{1}".format(win32api.HIWORD(ms), win32api.LOWORD(ms))
            if parts == 3:
                return "{0}.{1}.{2}".format(win32api.HIWORD(ms), win32api.LOWORD(ms), win32api.HIWORD(ls))

            return "{0}.{1}.{2}.{3}".format(win32api.HIWORD(ms), win32api.LOWORD(ms), win32api.HIWORD(ls), win32api.LOWORD(ls))
        except Exception:
            return None

    @staticmethod
    def chdir(path):
        """
        Changes current directory.
        """
        logging.debug(path)
        os.chdir(path)

    @staticmethod
    def replace_in_file(path, pattern, replace):
        """
        Replaces text in file.
        :param path: physical path to file
        :param pattern: text or regexp to search
        :param replace: text to replace
        """
        #logging.info("patch file '{0}': '{1}' -> '{2}'".format(filename, pattern, replace))

        WindowsShell.ensure_exists(path)

        with open(path, 'r') as f:
            s = f.read()
        (new_string, number_of_subs_made) = re.subn(pattern, replace, s, count=0, flags=re.M | re.I | re.U)
        s = new_string
        with open(path, 'w') as f:
            f.write(s)

        logging.debug('file {0} patched'.format(path))

    @staticmethod
    def add_to_path(path):
        """
        Adds 'path' to PATH env variable of current process.
        """
        logging.debug(path)
        WindowsShell.remove_from_path(path)
        os.environ["PATH"] = path + os.pathsep + os.environ["PATH"]

    @staticmethod
    def remove_from_path(path):
        """
        Removes path from PATH env variable of current process
        :param path:
        """
        logging.debug(path)
        system_path = os.environ["PATH"]
        # split PATH
        paths = system_path.split(os.pathsep)
        for part in paths:
            if part.lower() == path.lower():
                paths.remove(part)
        system_path = os.pathsep.join(paths)
        os.environ["PATH"] = system_path

    @staticmethod
    def copy_file(source, destination):
        """
        Copies 'source' file to 'destination'
        """
        shutil.copy(source, destination)

    @staticmethod
    def append_file(source, destination):
        """
        Appends content of 'source' file to 'destination' file.
        """
        if not os.path.exists(source):
            raise FileNotFoundError(source)
        if not os.path.exists(destination):
            raise FileNotFoundError(destination)
        with open(destination, 'a+b') as df:
            with open(source, 'rb') as sf:
                df.write(sf.read())

    @staticmethod
    def make_dir(path):
        """
        Makes directories tree specified in 'path'.
        """
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def is_alive(pid):
        """
            check existed process
        """
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    @staticmethod
    def dir_list_file(path):
        """
        Return the list of files in giving directory and subdirectories
        """
        total_size = 0
        list_flnames = []
        for dir_path, dir_names, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dir_path, f)
                list_flnames.append(fp)
        return list_flnames

    @staticmethod
    def dir_size(path):
        """
        Return directory size in bytes.
        """
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

    @staticmethod
    def get_short_path_name(long_name):
        """
        Return short name of specified file name.
        """
        return win32api.GetShortPathName(long_name)
