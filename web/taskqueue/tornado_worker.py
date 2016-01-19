# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.ioloop import PeriodicCallback
from tornado import gen
import urllib
import os
import time
from web.zooapi.views.master_product import MasterProduct
from queue import Queue
from threading import Thread
from web.taskqueue.models_peewee import TaskPeewee as Task
from web.taskqueue.models_peewee import LocksPeewee as Locks

import logging
from web.taskqueue.loghandler import TaskDbLogHandler
import subprocess
import sys
from core.helpers.decode import OutputDecoder
import json
from threading import Thread
from core.install_log_reader import InstallLogReader
from core.core import Core


##TEST page for web sockets

Page = "<!DOCTYPE html>\
<html>\
    <head>\
        <meta charset=\"utf-8\">\
	<script type=\"text/javascript\">\
        function WebSocketTest() {\n\
            var messageContainer = document.getElementById(\"messages\");\n\
            if (\"WebSocket\" in window) {\n\
                messageContainer.innerHTML = \"WebSocket is supported by your Browser!\";\n\
                var ws = new WebSocket(\"ws://localhost:7798/socket/log?Id=123456789\");\n\
                ws.onopen = function() {\n\
                    ws.send(\"Message to send\");\n\
                };\n\
                ws.onmessage = function (evt) {\n\
                    var received_msg = evt.data;\n\
                    Prev = messageContainer.innerHTML ;\n\
                    messageContainer.innerHTML = Prev + received_msg;\n\
                    ws.send(\"one more\");\n\
                };\n\
                ws.onclose = function() {\n\
                    messageContainer.innerHTML = \"Connection is closed...\";\n\
                };\n\
            } else {\n\
                messageContainer.innerHTML = \"WebSocket NOT supported by your Browser!\";\n\
            }\n\
        }\n\
        </script>\
    </head>\
    <body>\
        <a href=\"javascript:WebSocketTest()\">Run WebSocket</a>\
        <div id=\"messages\" style=\"height:100%;background:black;color:white;\"></div>\
    </body>\
</html>"
## global variable for connection
connection = None

class TornadoWorker(object):

    def __init__(self, *args):

        self.web_frontend_url = "http://127.0.0.1:7799/api/1/core/sync/"
        self.process = None
        self.logger = None
        self.timer_read_log = None
        self.timer_check_logdir = None
        self.check_new_tasks = None
        self.decoder = OutputDecoder()
        # TODO remove port from code
        self.port = 7798
        self.logger = logging.getLogger()
        self.log_reader = None
        # remove all handlers
        self.logger.handlers = []
        # add only db handler
        self.core = Core.get_instance()

        self.configs = {
            'max_messages_per': 100,
            "queue": Queue(),
            'buffer': 1,
            'sessions': {},
            "state": "reading",
            'status_done': False,
            'task': None
        }

        self.application = tornado.web.Application([
            (r"/socket/log", WebSocketHandler, {"configs": self.configs}),
            (r"/test", MainHandler, {"configs": self.configs})
        ])

    # check weather the child process is working now
    def wait_worker_process(self):
        logging.debug('thread for waiting of worker process started')
        if self.process:
            if self.process.poll() is not None:
                logging.debug("process is finished")
                self.process = None
                # stop interaval timers
                self.timer_read_log.stop()
                self.timer_check_logdir.stop()
                self.logger.info('install worker process is finished check last lines from logs')

                self.sync_core_frontend()
                TornadoWorker.periodic_read_logs(self)

    def sync_core_frontend(self):
        print(self.web_frontend_url)
        urllib.request.urlopen(self.web_frontend_url)

    # start eventloop, webserver and periodic reading
    def start(self):
        self.application.listen(self.port)
        main_loop = tornado.ioloop.IOLoop.instance()
        self.check_new_tasks = PeriodicCallback(lambda: TornadoWorker.periodic_check_new_tasks(self), 2000)
        self.check_new_tasks.start()
        main_loop.start()



    # delete locks after work
    @staticmethod
    def clear_lock(key):
        try:
            obj = Locks.get(Locks.title == key)
            obj.delete_instance()
            return True
        except Locks.DoesNotExist:
            return False

    # try to start locking of a task
    @staticmethod
    def lock_obj(key, val):
        try:
            lk = Locks()
            lk.title = key
            lk.value = val
            lk.save()
            return val
        except BaseException:
            obj = Locks.get(Locks.title == key)
            return obj.value

    # just check lock on given key
    @staticmethod
    def get_lock(key):
        try:
            obj = Locks.get(Locks.title == key)
            return obj.value
        except Locks.DoesNotExist:
            return False

    # make task fail
    @staticmethod
    def task2fail(task_id):
        try:
            obj = Task.get(Task.id == task_id)
            obj.status = Task.STATUS_FAILED
            obj.save()
        except Task.DoesNotExist:
            return True

    # check if task is alive
    @staticmethod
    def is_alive_task(task_id, core):
        try:
            obj = Task.get(Task.id == task_id)
            # may be wrong
            if obj.status == Task.STATUS_EXCEPTION:
                return False
            if obj.status == Task.STATUS_FAILED:
                return False
            if obj.status == Task.STATUS_DONE:
                return False

            print("find possible alive task %i pid is %i" % (task_id, obj.pid) )
            pid = obj.pid
            return core.api.os.shell.is_alive(pid)
        except Task.DoesNotExist:
            return False

    # check weather the running task is zombie
    #  may be there are some sense to do like decorator
    def check_zombie(self, task_id):
        try:
            self.process_check_new_tasks()
        except BaseException:
            print(sys.exc_info())

    # checking for new tasks in database
    # may be there are some sense to do like decorator
    def periodic_check_new_tasks(self):
        # try:
            self.process_check_new_tasks()
        # except BaseException:
        #     print(sys.exc_info())

    # check the lock and failed tasks
    def check_free4run(self):
        ret = TornadoWorker.get_lock(Task.LOCK)
        if not ret:
            return True
        else:
            task_id = int(ret)
            if TornadoWorker.is_alive_task(task_id, self.core):
                print("task is really working we will wait")
                return False
            else:
                print("task to fail %i" % task_id)
                TornadoWorker.task2fail(task_id)
                TornadoWorker.clear_lock(Task.LOCK)
                # TODO add clearing all task with the same session
                return True

    # process tasks to work
    def process_check_new_tasks(self):
        # User.select().where(User.active == True).order_by(User.username)
        print("i'm checking a new tasks")
        query = Task.select().where(Task.status == Task.STATUS_PENDING).order_by(Task.id)

        if not self.check_free4run():
            print("lock is busy")
            return False
        # race condition ?????
        for task in query:
            print("i have found a new task %s" % str(task))
            if TornadoWorker.lock_obj(Task.LOCK, str(task.id)):
                # if it failed ?
                self.start_task(task)
                return True
            else:
                return False



        # start working on task
    def task(self, task):

        self.log_reader = InstallLogReader(path=self.core.settings.tmp_logs_path, task_id=str(task.id))
        common_log = self.log_reader.common_working_log()
        self.logger.addHandler(TaskDbLogHandler(task))

        f_out = open(common_log, 'w')
        self.process = subprocess.Popen(
            (
                sys.executable,
                '-u',
                sys.argv[0],
                '--task-work={0}'.format(task.id),
            ),
            stderr=f_out,
            stdout=f_out
        )
        print("start child task with pid %i" % self.process.pid)
        task.parent_pid = os.getpid()
        task.pid = self.process.pid
        task.save()
        self.configs["task"] = task

        self.timer_check_logdir = PeriodicCallback(lambda: TornadoWorker.periodic_check_logdir(self), 700)
        self.timer_read_log = PeriodicCallback(lambda: TornadoWorker.periodic_read_logs(self), 300)

        self.timer_read_log.start()
        self.timer_check_logdir.start()



    # start working on task
    def start_task(self, task):

        self.log_reader = InstallLogReader(path=self.core.settings.tmp_logs_path, task_id=str(task.id))
        common_log = self.log_reader.common_working_log()
        self.logger.addHandler(TaskDbLogHandler(task))

        f_out = open(common_log, 'w')
        self.process = subprocess.Popen(
            (
                sys.executable,
                '-u',
                sys.argv[0],
                '--task-work={0}'.format(task.id),
            ),
            stderr=f_out,
            stdout=f_out
        )
        print("start child task with pid %i" % self.process.pid)
        task.parent_pid = os.getpid()
        task.pid = self.process.pid
        task.save()
        self.configs["task"] = task

        self.timer_check_logdir = PeriodicCallback(lambda: TornadoWorker.periodic_check_logdir(self), 700)
        self.timer_read_log = PeriodicCallback(lambda: TornadoWorker.periodic_read_logs(self), 300)

        self.timer_read_log.start()
        self.timer_check_logdir.start()

    # pseudo static method of reading new lines from directory
    @staticmethod
    def periodic_read_logs(self):
        lines = self.log_reader.read_new()
        line = "".join(lines)
        # logging.debug(line.decode('ascii', errors='ignore').rstrip())
        if line != "":
            self.configs["queue"].put(line, False)

    # pseudo static method of checking is the directory has changed
    def periodic_check_logdir(self):
        if self.log_reader.is_changed():
            self.log_reader.update_list_checking_files()

        self.wait_worker_process()

    @staticmethod
    def get_object_or_404(id):
        try:
            obj = Task.get(Task.id == id)
            return obj
        except Task.DoesNotExist:
            return []

    # stopping tornado
    def stop(self):
        # schedule stopping
        self.configs["queue"].put("#last_record#")

# handler of processing connections
class WebSocketHandler(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True

    def initialize(self, configs):
        self.configs = configs

    def open(self, *args):

        self.stream.set_nodelay(True)
        global connection
        connection = self

    def on_message(self, message):
        """
        when we receive some message we want some message handler..
        for this example i will just print message to console
        """
        # print("got %s" % message)
        if self.configs["state"] == "reading":
            obj = json.loads(message)
            self.writing_logs(obj)
            return

    # write logs to socket
    def writing_logs(self, obj):
        # TODO change to session
        # if requested task logs is not equal to current task than this task is pending
        if "task_id" not in obj:
            self.write_message(json.dumps({"status": False,
                                           "data": {}}, indent=1))
            return

        if obj["task_id"] != self.configs["task"].id:
            t = TornadoWorker.get_object_or_404(obj["task_id"])
            self.write_message(json.dumps({"status": False,
                                           "state": "pending",
                                           "data": {"task": t.to_dict()}}, indent=1))
            return

        # не мучаем базу данных если таска уже завершилась а логи все еще идут
        # if not self.configs["status_done"]:
        t = TornadoWorker.get_object_or_404(self.configs["task"].id)
        if t.status in (Task.STATUS_DONE, Task.STATUS_FAILED,
                        Task.STATUS_EXCEPTION) :
            state = "wait_finish"
        else:
            state = "reading"

        now_time = time.time()
        size = self.configs["queue"].qsize()

        if self.configs["queue"].empty():
                self.write_message(json.dumps({"status": False,
                                               "state": state, "data":
                                              {"task": t.to_dict()}}, indent=1))
        else:
                reader_index = 0
                messages = []

                while reader_index < size:

                    reader_index += 1
                    item = self.configs["queue"].get(False)
                    messages.append({"created": now_time, "message": item})
                    self.configs["queue"].task_done()

                result = {"status": True, "state": state, "data": {"task": t.to_dict(),
                          "log_messages": messages}}
                self.write_message(json.dumps(result, indent=1))

    # just write something, when we are closed
    def on_close(self):
        print("closed")

# i have leave it only in debugging way
class MainHandler(tornado.web.RequestHandler):

    def initialize(self, configs):
        self.configs = configs

    @tornado.web.asynchronous
    def get(self):
        self.write(Page)
        self.finish()

