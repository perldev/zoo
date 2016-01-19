/*
    {
 "data": {
  "log_messages": [
   {
    "source": "web.read_stderr",
    "created": 1419607149.190669,
    "message": "Core loader: Creating core...\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.242672,
    "message": "settings:\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.244673,
    "message": "bitness: '64'\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.246673,
    "message": "cache_path: C:\\Users\\ruslan\\NewLifeProjects\\Zoo\\cache\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.252673,
    "message": "lang: null\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.254673,
    "message": "logs_path: C:\\Users\\ruslan\\NewLifeProjects\\Zoo\\logs\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.257673,
    "message": "os: windows\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.259673,
    "message": "os_version: 6.1.7601\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.262674,
    "message": "root: C:\\Users\\ruslan\\NewLifeProjects\\Zoo\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.264674,
    "message": "storage_path: C:\\Users\\ruslan\\NewLifeProjects\\Zoo\\data\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.267674,
    "message": "urls: ['http://ci-helicontech/zoo4/feed.yaml']\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.269674,
    "message": "version: 1.0.0.0\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.272674,
    "message": "webserver: iis\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.274674,
    "message": "zoo_home: c:\\zuu\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.277674,
    "message": "\r\n",
    "level": "WARNING"
   }
  ],
  "task": {
   "created": "2014-12-26T17:19:07.371565",
   "status": "pending",
   "params_str": "{\n \"parameters\": {\n  \"erlang59\": {\n   \"install_dir\": \"%SystemDrive%\\\\erl5.9\"\n  }\n },\n \"products\": [\n  {\n   \"author\": \"Ericsson Computer Science Laboratory\",\n   \"description\": \"Erlang is a programming language used to build massively scalable soft real-time systems\\nwith requirements on high availability. Some of its uses are in telecoms, banking, e-commerce,\\ncomputer telephony and instant messaging. Erlang's runtime system has built-in support for concurrency,\\ndistribution and fault tolerance.\\n\",\n   \"eula\": \"http://www.erlang.org/EPLICENSE\",\n   \"files\": [\n    {\n     \"file\": \"http://www.erlang.org/download/otp_win32_R15B.exe\",\n     \"filename\": \"otp_win32_R15B.exe\"\n    }\n   ],\n   \"find_installed_command\": \"if 'install_dir' in parameters and os.path_exists(parameters['install_dir']):\\n  result = InstalledProductInfo()\\n  result.version = windows.get_file_version(parameters['install_dir'] + '\\\\\\\\bin\\\\\\\\erlang.exe', parts=3)\\n  result.install_dir = parameters['install_dir']\",\n   \"icon\": \"http://ci-helicontech/zoo4/Erlang/erlang-100x100.png\",\n   \"install_command\": \"os.cmd('{0} /S /D=\\\"{1}\\\"'.format(files[0].path, parameters['install_dir']))\",\n   \"installed_version\": null,\n   \"link\": \"http://www.erlang.org/\",\n   \"os\": \"windows\",\n   \"parameters\": {\n    \"install_dir\": \"%SystemDrive%\\\\erl5.9\"\n   },\n   \"product\": \"Erlang59\",\n   \"tags\": [\n    \"server\"\n   ],\n   \"title\": \"Erlang\",\n   \"uninstall_command\": \"os.delete_path(parameters['install_dir'])\",\n   \"upgrade_command\": \"os.cmd('{0} /S /D=\\\"{1}\\\"'.format(files[0].path, parameters['install_dir']))\",\n   \"version\": \"5.9 R15B\"\n  }\n ],\n \"requested_products\": [\n  \"Erlang59\"\n ]\n}",
   "updated": "2014-12-26T17:19:07.371565",
   "title": "Installing products: Erlang59",
   "command": "install",
   "params": {
    "requested_products": [
     "Erlang59"
    ],
    "parameters": {
     "erlang59": {
      "install_dir": "%SystemDrive%\\erl5.9"
     }
    },
    "products": [
     {
      "product": "Erlang59",
      "install_command": "os.cmd('{0} /S /D=\"{1}\"'.format(files[0].path, parameters['install_dir']))",
      "author": "Ericsson Computer Science Laboratory",
      "parameters": {
       "install_dir": "%SystemDrive%\\erl5.9"
      },
      "files": [
       {
        "filename": "otp_win32_R15B.exe",
        "file": "http://www.erlang.org/download/otp_win32_R15B.exe"
       }
      ],
      "eula": "http://www.erlang.org/EPLICENSE",
      "title": "Erlang",
      "upgrade_command": "os.cmd('{0} /S /D=\"{1}\"'.format(files[0].path, parameters['install_dir']))",
      "os": "windows",
      "installed_version": null,
      "find_installed_command": "if 'install_dir' in parameters and os.path_exists(parameters['install_dir']):\n  result = InstalledProductInfo()\n  result.version = windows.get_file_version(parameters['install_dir'] + '\\\\bin\\\\erlang.exe', parts=3)\n  result.install_dir = parameters['install_dir']",
      "description": "Erlang is a programming language used to build massively scalable soft real-time systems\nwith requirements on high availability. Some of its uses are in telecoms, banking, e-commerce,\ncomputer telephony and instant messaging. Erlang's runtime system has built-in support for concurrency,\ndistribution and fault tolerance.\n",
      "uninstall_command": "os.delete_path(parameters['install_dir'])",
      "tags": [
       "server"
      ],
      "link": "http://www.erlang.org/",
      "icon": "http://ci-helicontech/zoo4/Erlang/erlang-100x100.png",
      "version": "5.9 R15B"
     }
    ]
   },
   "is_finished": false,
   "error_message": "",
   "id": 110
  }
 }
}
  */


Task = {




    $task_placeholder: $('#task-placeholder'),
    $task_log: $('#task-log'),

    $task_template: $('#task-template'),
    task_template: null,

    $task_log_template: $('#task-log-template'),

    task_log_template: null,
    log_socket: null,
    task_id: null,
    task_finished: false,
    last_updated: null,
    last_log: 0,
    urls_printed: false,
    ExtObject: null,

    $go_to_node_link: $('#go-to-node'),
    load: function(){
      ZooApi.get(ZooApi.Urls.task + this.task_id + '/', {}, function(response){
        var task = response.data;
        Task.print_task(task);

        if (!Task.task_finished && "WebSocket" in window) {
                var ws ;
                var this_obj = window.Task;
                //TODO try reconnect
                setTimeout(function() {

                        // TODO move to attributes host
                        ws = new WebSocket("ws://localhost:7798/socket/log");
                        this_obj.log_socket = ws;
                        this_obj.log_socket.onopen = function () {
                            console.log("open connection...");
                            this_obj.log_socket.send("{\"msg\":\"hello\"}");
                        };
                        this_obj.log_socket.onmessage = function (Txt) {

                            var Obj = JSON.parse(Txt.data);
                            console.log(Obj);
                            if(Obj.status) {
                                 this_obj.print_log(Obj["data"]);
                                 if( Obj["state"] === "wait_finish" ){
                                        console.log("open DLG");
                                        this_obj.task_finished = true;
//                                        Task.log_socket.send("{\"msg\":\"finish\",\"task_id\":" + this_obj.task_id + "}");
                                        Task.ExtObject.finish(Task);
                                        this_obj.log_socket.close()

                                 }else {
                                        this_obj.log_socket.send("{\"msg\":\"ping\",\"task_id\":" + this_obj.task_id + "}");
                                  }
                            }else{
                                if(!this_obj.task_finished )
                                    this_obj.log_socket.send("{\"msg\":\"ping\",\"task_id\":" + this_obj.task_id + "}");
                            }


                        };
                        this_obj.log_socket.onclose = function () {
                            console.log("Connection is closed...");
                        };

                },2000);
            } else {
                Task.update_log();
                Task.ExtObject.finish(Task);
            }


      });
    },

    print_task: function(task){
      if (Task.last_updated == task.updated){
        // nothing
      } else {
        Task.last_updated = task.updated;
        console.log('task:', task);
        Task.$task_placeholder.empty();
        var html = Task.task_template({task: task});
        Task.$task_placeholder.html(html);
        if (task.is_finished){
          Task.task_finished = true;
        }
        if (!Task.urls_printed){
          Task.get_result_urls(task);
        }
      }
    },

    update_log: function(){
      console.log('update task log since', this.last_log);
      //Status.show('loading logs');
      ZooApi.get(ZooApi.Urls.task + this.task_id + '/log/', {since: this.last_log}, function(response){
        Task.print_log(response.data);
        if (!response.data.task.is_finished || !Task.task_finished){
             Task.wait_and_reload_log();
        }

      });
    },

    print_log: function(data){
      if (data.log_messages){
          //Status.show('printing logs');

        //var html = '';
        var text = [];
        for(var i=0; i<data.log_messages.length; i++){
          var log = data.log_messages[i];
          //html += this.task_log_template(log);

          var message = log['message'];
          message = message.replace(/\s*$/, '') + '\n';
          text.push(message);
          this.last_log = log.created;
        }

        //$(html).appendTo(this.$task_log);
        this.$task_log.append(document.createTextNode(text.join('')));
        if (text.length > 0) {
          this.$task_log[0].scrollTop = this.$task_log[0].scrollHeight;
        }
      }

      //Status.hide();

      if (!data.task.is_finished || !this.task_finished) {
        this.print_task(data.task);

      } else {
        console.log('task finished');
      }

      this.update_log_size();
    },

    wait_and_reload_log: function(){
      setTimeout(function(){
          Task.update_log();
        }, 100
      );
    },

    cancel: function(){
      console.log('canceling task');
      ZooApi.post(ZooApi.Urls.task + this.task_id + '/cancel/', {}, function(response){
        console.log(response.data);
      });
    },

    rerun: function(){
      console.log('re-run task');
      Status.show('re-running task');
      ZooApi.post(ZooApi.Urls.task + this.task_id + '/rerun/', {}, function(response){
        console.log(response.data);
        window.location.reload(true);
      });
    },

    toggle_debug_log: function(enable){
      this.$task_log.find('.log-level-DEBUG').toggle(enable);
      this.$task_log.find('.log-dbg').toggle(enable);
    },

    get_result_urls: function(task){
      $('#result-urls').hide();
      if (!task.is_finished){
        return;
      }

      // search product
      var app_params = null;

      if (task.params) {
        var products_params = task.params.parameters;
        if (products_params) {
          var product_names = Object.keys(products_params);
          for (var i = 0; i < product_names.length; i++) {
            var product_params = products_params[product_names[i]];
            if (product_params.hasOwnProperty('site-name')) {
              app_params = product_params;
              break;
            }
          }
        }
      }

      if (!app_params){
        return;
      }

      var site_name = app_params['site-name'];
      var app_path = app_params['app-name'] || '';

      var node_path = site_name + app_path;
      this.$go_to_node_link.removeClass('hidden').attr('href', this.$go_to_node_link.attr('href') + '#' + node_path);

      // TODO: get start page!
      var start_page = app_params['start-page'] || '';
      if (app_path.startsWith('/')){
        app_path = app_path.substr(1);
      }
      if (app_path && !app_path.endsWith('/')){
        app_path = app_path + '/'
      }
      if (start_page.startsWith('/')){
        start_page = start_page.substr(1);
      }

      // get site object
      ZooApi.get(ZooApi.Urls.server_root + site_name + '/', {}, function(response){
        var node = response.data.node;
        var result_urls = [];
        if (node['urls']){
          for(var i=0; i<node.urls.length; i++){
            var url = node.urls[i];
            /*
            if (url.endsWith('/')){
              url = url.substr(0, url.length-1);
            }
            */
            result_urls.push(url + app_path + start_page);
          }
          Task.print_result_urls(result_urls);
        }
      });
    },

    print_result_urls: function(urls){
      var html = Handlebars.compile("\{\{#each urls}}<li><a href=\"{{this}}\" target=\"_blank\">{{this}}</a></li>\{\{/each\}\}")({urls: urls});
      $('#result-urls>ul').html(html).parent().show();
    },

    update_log_size: function(){
      var wh = $(window).height();
      var tph = this.$task_placeholder.height();
      var th = wh - $('#header').outerHeight() - tph - 100;
      //console.log('task log height: ', th);
    },

    init: function (Ext) {
      $('#service-menu').find('a[href="/task/"]').parent().addClass('active');
      Task.ExtObject = Ext;
      this.$task_placeholder.on('click', '#btn-toggle-task-meta', function(ev){
        Task.$task_placeholder.find('#task-meta').toggle();
      });
      this.$task_placeholder.on('click', '#btn-task-cancel', function(ev){
        Task.cancel();
      });
      this.$task_placeholder.on('click', '#btn-task-rerun', function(ev){
        Task.rerun();
      });
      /*
      this.$task_placeholder.on('change', '#checkbox-show-debug', function(ev){
        Task.toggle_debug_log($(this).is(':checked'));
      });
      */

      this.task_template = Handlebars.compile(this.$task_template.html());
      this.task_log_template = Handlebars.compile(this.$task_log_template.html());

      this.load();

      this.update_log_size();
      $(window).resize(function(){
        Task.update_log_size();
      });

      var ua = window.navigator.userAgent;
      if (ua.indexOf('MSIE ') > 0 || ua.indexOf('Trident') > 0) {
        $('#copy-log').click(function () {
          var log = Task.$task_log[0];
          var cl = document.getElementById('clipboard-area');
          cl.innerText = log.innerText;
          cl.focus();
          var r = cl.createTextRange();
          r.execCommand('selectall');
          r.execCommand('Copy');
        });
      } else {
        $('#copy-log').hide();
      }

    }

  };

