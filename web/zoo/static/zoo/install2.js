  Install = {
    raw_state:{},
    requested_items: [],
    requested_products_names: [],
    requested_products: [],
    requested_product_parameters:{},
    installed_products_names: [],
    installed_products: [],
    starting: true,
    //state -> handler to do
    $modal_dlg: $('#modal-install-confirm'),
    current_state: "",

    selected_engine: null,
    requested_application: null,
    requested_application_db_types: false,
    requested_application_has_unknown_parameters: false,

    state: null,
    is_install_response_processed: false,
    products_has_parameters: false,
    product_tabs:[
      "tab-pill-list",
      "tab-pill-product-parameters",
      "tab-pill-product-licenses",
      "tab-pill-product-installing"
    ],
    product_pages:[
      "tab-list",
      "tab-product-parameters",
      "tab-product-licenses",
      "tab-product-installing"
    ],
    product_page4state:{
      "start":[],
      "requirements":[],
      "wait_params":[0],
      "wait_licences":[0,1],
      "installing":[0,1,2]
    },
    product_tabs4state:{
      "start":[],
      "requirements":[0],
      "wait_params":[0,1],
      "wait_licences":[0,1,2],
      "installing":[0,1,2,3]
    },
    product_install_template:  Handlebars.compile($('#product-install-template2').html()),
    product_licenses_template:  Handlebars.compile($('#product-licenses-template').html()),
    parameters_template:  Handlebars.compile($('#parameters-template').html()),
    product_install_errors_template: Handlebars.compile($('#product-install-errors').html()),
    $response_log: $('#response-log'),

    //$install_list_application: $('#install-list-application'),
    $install_list_products: $('#install-list-products'),
    //$install_list: $('#install-list'),
    $product_params_list: $('#product-parameters-list'),
    $application_params_list: $('#application-parameters-list'),

    $install_request_code: $('#install-request-code'),
    $install_request_errors: $('#install-request-errors'),
    $install_request_errors_placeholder: $('#install-request-errors .placeholder'),



    product_master_licenses: function(){
        Install.hide_pages_before(Install.current_state);
        var result_html="";
        for(var i=0;i<Install.requested_products.length ; i++){
               var item = Install.requested_products[0];
               item['client_id'] = item['client_id'] || Math.uuid(10);
               result_html += Install.product_licenses_template(item);
        }
        $("#product-licenses-list").html(result_html);
        $("#tab-product-licenses").show();
        Install.current_state = "wait_licences";
      //product-licenses-list*/

//        <div class="install-item install clearfix " data-product="Erlang59" data-client-id="ek1vjmjTnm">
//            <div class="install-item-content clearfix">
//              <div class="install-item-header clearfix" data-client-id="ek1vjmjTnm">
//
//                  <img class="install-item-icon" src="/product/Erlang59/icon/">
//
//                <div class="install-item-title clearfix">
//                  <h3 class="title">Erlang</h3>
//                  <span class="product-version">5.9 R15B</span>
//
//                   <span class="product-meta text-muted">
//
//                    ·
//                    <a href="" target="_blank">website</a>
//                    ·
//                    <a href="" target="_blank">license</a>
//                  </span>
//                </div>
//              </div>
//
//
//            </div>
//
//
//            <div class="install-dependencies clearfix"></div>
//        </div>


    },

    product_master2install: function(ev){
          return ev;
    },
    product_master_installing:function(response){
       Install.hide_pages_before("installing");
       console.log("installing");
       console.log(response);
       if (response.data.task.id){
          // install task success started
           //Install.go_to_task(response.data.task);
           Task.task_id = response.data.task.id;
           Task.init(Install);
           $("#tab-product-installing").show();
           Status.hide();
       } else {
           // show error dialog
           Install.update();
       }


    },
    product_master2install_command: function(){

      Status.show('Requesting installation...');
      var req =  Install.prepare_install_request();
      Install.current_state = "installing";
      req.command = "install";
      ZooApi.post(ZooApi.Urls.install, req, Install.product_master_installing);

    },
    product_master2params_command: function(ev){
        var products=[];
        for(var i=0; i<Install.requested_products.length; i++){
          var product_name = Install.requested_products[i].product.name;
          var product_parameters = Install.get_product_parameters(product_name);
          products.push(
            {
              product: product_name,
              parameters: product_parameters
            }
          );
        }
        console.log("params page");
    },
    product_master2params_page: function(){
        Install.current_state = "wait_params";
        console.log(Install.products_has_parameters)
        if(Install.products_has_parameters){
            $("#tab-product-parameters").show();
        }else{
            //Emulate steping
            Install.current_state = "wait_licences";
            Install.product_master_licenses();
        }
    },
    //simple command for changing state of master
    //using for connecting different pages
     product_master2finish: function(ev){
         var req = {
          "command": "finish"
         };
        console.log(req);
        ZooApi.post(ZooApi.Urls.install, req, Install.product_master_installing);
    },
    hide_pages_before:function(State){

        console.log("current page hide " + this.current_state);
        for(var i=0; i<this.product_page4state[State].length; i++){
            console.log(" hide " + this.product_pages[i]);
            $("#"+this.product_pages[i]).hide();
        }
    },
//    java script commands to master
    next: function(ev){

       var Routes = {
        "requirements": window.Install.product_master2params_page,
        "wait_params": window.Install.product_master_licenses,
        "wait_licences": window.Install.product_master2install_command,
        "wait_finish": window.Install.product_master2finish
      };
      Routes[Install.current_state](ev);
      Install.hide_pages_before(Install.current_state);
      Install.render_up_buttons();

    },
    finish: function(TaskObj){
           $("#finish").removeClass("hidden");
           $("#cancel_button").hide();
    },
    finish_task: function(){
         window.location.href = "/gallery"

//         var req = {
//          "command": "finish"
//         };
//        console.log(req);
//        ZooApi.post(ZooApi.Urls.install, req, Install.master_command);

    },
    move_away:function(){
            window.location.href="/gallery/";
    },
//    DEPRECATED
    master_command: function () {
      Status.hide();
      var Routes = {
        "start": window.Install.initial_request,
        "requirements": window.Install.product_master_requirements,
        "wait_params": window.Install.product_master2params_page,
        "wait_licences": window.Install.product_master_licenses,
        "installing": window.Install.product_master_installing,
        "wait_finish":window.Install.product_master_wait2finish,
        "free": window.Install.move_away
      };
      console.log("current state " + Install.current_state);

      Routes[Install.current_state]();
      Install.render_up_buttons();
    },
    render_up_buttons: function(){
        var i=0;

        for(i=0; i<this.product_tabs4state[this.current_state].length; i++){
             $("#"+this.product_tabs[i]).removeClass("active");
        }
         $("#first_tab").removeClass("active");
        if(this.current_state == "requirements"){
                    $("#first_tab").addClass("active");
        }

        if(i>0){
            $("#"+this.product_tabs[i-1]).addClass("active");
        }

    },
    update: function(){
      this.is_install_response_processed = false;
      this.process_install_response();
      this.render_wizard_tabs();
      this.show_errors();
    },
    go_to_task: function(task){
      Status.show('Installation task created');
      console.log('install task created with id', task.id);
      window.location.href = task.url;
    },

    dependency_option_selected: function($li){
      DependencyTree.dependency_option_selected($li);
      this.update();
    },

    render_product_tree: function(){
      this.$install_list_products.empty();
      DependencyTree.render_items_and_add(this.items, this.$install_list_products);
    },

    fill_product_list: function () {
      var printed_product_names = [];
      this.render_product_tree();


      /*
      if (this.requested_application){
        this.render_item_and_add(this.requested_application, this.$install_list_application);
        printed_product_names.push(this.requested_application.product.name);
      }

      for (var i=0; i<this.items.length; i++){
        var item = this.items[i];
        if ($.inArray(item.product.name, printed_product_names) >= 0){
          continue;
        }

        var $list = this.$install_list;
        if ($.inArray(item.product.name, this.requested_items) >= 0){
          $list = this.$install_list_products;
        }

        this.render_item_and_add(item, $list);
        printed_product_names.push(item.product.name);
      }

      if (this.$install_list_application.children().length > 0){
        this.$install_list_application.prev().show();
      }
      if (this.$install_list_products.children().length > 0){
        this.$install_list_products.prev().show();
      }
      if (this.$install_list.children().length > 0){
        this.$install_list.prev().show();
      }
      */

      WizardTabs.$list.find('.actions-bar').slideDown().removeClass('hide-soft');
    },

    fill_product_params: function () {
      this.$product_params_list.empty();
      if (this.products_has_parameters){
        for(var i=0; i<this.requested_products.length; i++){
          var product = this.requested_products[i].product;
          var parameters = this.requested_products[i].parameters;
          if (parameters && parameters.length > 0){
            var html = this.parameters_template(this.requested_products[i]);
            var $html = $(html);
            $html.appendTo(this.$product_params_list);
          }
        }
        this.validate_parameters(WizardTabs.$product_params);
      }
    },

    fill_website_selector: function () {
    },

    fill_application_params: function () {
      this.$application_params_list.empty();
      if (this.requested_application){
        var html = this.parameters_template(this.requested_application);
        var $html = $(html);
        $html.appendTo(this.$application_params_list);

        this.validate_parameters(WizardTabs.$application_params);
      }
    },

    fill_database_selector: function(){
      if (this.requested_application_db_types){
        Database.set_engines(this.requested_application_db_types);
        Database.print_engine_options();
      }
    },

    render_wizard_tabs: function(){
      this.fill_product_list();
      this.fill_product_params();
      this.fill_website_selector();
      this.fill_database_selector();
      this.fill_application_params();
    },

    process_install_response: function(){
      if (!this.is_install_response_processed){

        WizardTabs.hide_pills();

        // search requested_products and products_has_parameters
        this.get_install_product_list();

        // application?
        this.requested_application = null;
        for (var i=0; i<this.items.length; i++) {
          var product = this.items[i]['product'];
          if (product && product.hasOwnProperty('application')){
            this.requested_application = this.items[i];
            break;
          }
        }

        // toggle application specific tabs
        if (this.requested_application) {

          // always show web site page
          WizardTabs.show_pill(WizardTabs.$pill_web_site);

          // get database
          var db_types = null;
          if (this.requested_application.product.hasOwnProperty('database_type')){
            db_types = this.requested_application.product.database_type;
            if (db_types && db_types.length > 0) {
              this.requested_application_db_types = db_types;
            }
          }

          if (this.requested_application_db_types){
            WizardTabs.show_pill(WizardTabs.$pill_database);
          }

          this.requested_application_has_unknown_parameters = Object.keys(this.requested_application.product.parameters).length > 0;
          if (this.requested_application_has_unknown_parameters) {
            WizardTabs.show_pill(WizardTabs.$pill_application_params);
          }
        }

        this.is_install_response_processed = true;
      }
    },

    get_install_product_list: function(){
      Install.products_has_parameters = false;
      Install.requested_products_names = [];
      Install.requested_products = [];
      Install.installed_products_names = [];
      Install.installed_products = [];
      console.log('items:', Install.items);

      Install._loop_items(Install.items);
      console.log('requested product names:', this.requested_products_names);
      console.log('installed product names:', this.installed_products_names);

    },

    _loop_items: function(items, filter_id){
      for(var i=0; i<items.length; i++){

        var item = items[i];
        item['client_id'] = item['client_id'] || Math.uuid(10);

        if (filter_id && item['client_id']!=filter_id){
          continue;
        }
        console.log("adding product");
        console.log(item);

        if (item['product']){
          var product = item['product'];
          if (product['application']){
            // skip application, accept product and engines only
          } else {
            var product_name = product['name'];
            // раньше была проверка, по которой мы не проверяли продукты-дубли в списке
            // теперь будли оставляем, дальше в апи дубли уберуться
            //if ($.inArray(product_name, this.requested_products_names) == -1) {
              if (!product['installed_version']) {
                // product is not installed


                this.requested_products_names.push(product_name);
                this.requested_products.push(item);
                var parameters = item['parameters'];
                //if (product.hasOwnProperty('parameters') && Object.keys(product.parameters).length > 0) {
                if (parameters && parameters.length > 0) {
                  this.products_has_parameters = true;
                }
              } else {
                // product is installed, save it for install request
                if ($.inArray(product_name, this.installed_products_names) == -1) {
                  this.installed_products_names.push(product_name);
                  this.installed_products.push(item);
                }
              }
            //}

            // try to save selected engine
            if (product['engine']){
              // save selected engine
              this.selected_engine = product;
            }
          }
        }


        if (item['and']){
          this._loop_items(item['and']);
        }

        if (item['or']){
          var or_options = item['or'];
          for (var j=0; j<or_options.length; j++){
            var or_item = or_options[j];
            or_item['client_id'] = or_item['client_id'] || Math.uuid(10);
          }
          var selected_id = DependencyTree.get_selected_option_client_id(item['client_id'], or_options);
          this._loop_items(or_options, selected_id);
        }
      }
    },

    show_errors: function(){
      var has_errors = false;
      this.$install_request_errors_placeholder.empty();

      for (var i=0; i<this.items.length; i++) {
        var item = this.items[i];
        if (item.error){
          has_errors = true;
          var html = this.product_install_errors_template(item);
          var $html = $(html);
          $html.appendTo(this.$install_request_errors_placeholder);
        }
      }

      if (has_errors) {
        this.$install_request_errors.slideDown();
      } else {
        this.$install_request_errors.slideUp();
      }
    },

    prepare_install_request: function(){
      var products = [];
      if (this.requested_application){
        var app_name = this.requested_application.product.name;
          products.push(
            {
              product: app_name,
              parameters: this.get_application_parameters()
            }
          );
      }
      for(var i=0; i<this.requested_products.length; i++){
        var product_name = this.requested_products[i].product.name;
        var product_parameters = this.get_product_parameters(product_name);
        products.push(
          {
            product: product_name,
            parameters: product_parameters
          }
        );
      }
      /*
      // решили не передавать инсталлированные продукты
      for(var i=0; i<this.installed_products.length; i++){
        var product = this.installed_products[i].product;
        products.push(
          {
            product: product.name + '==' + product.installed_version,
            parameters: null,
            is_installed: true
          }
        );
      }
      */

      var req = {
        install_products: products,
        requested_products: this.requested_items
      };

      console.log(req);
      return req;
    },
    get_product_parameters: function(product_name){
      var params = {};
      var $product_parameters_block = $('.parameter-item[data-product="'+product_name+'"]');
      if ($product_parameters_block.length) {
        $product_parameters_block.find('.form-group').each(function(i, el){
          var $input = $(this).find('[data-parameter]');
          var name = $input.attr('data-parameter');
          params[name] = $input.val();
        });
      }
      return params;
    },
    get_selected_engine: function(){
      if (this.selected_engine){
        return this.selected_engine['name'];
      }

      return null;
    },

    get_application_parameters: function(){
      var params = {};

      if (this.requested_application){
        var website_params = Websites.get_website_parameters();
        $.extend(params, website_params);
      }

      if (this.requested_application_db_types){
        var db_params = Database.get_db_params();
        $.extend(params, db_params);
      }

      if (this.requested_application_has_unknown_parameters){
        var unknown_params = this.get_product_parameters(this.requested_application.product.name);
        $.extend(params, unknown_params);
      }

      var selected_engine = this.get_selected_engine();
      if (selected_engine){
        params['selected-engine'] = selected_engine;
      }

      return params;
    },

    show_install_request: function(){
      var req = this.prepare_install_request();
      this.$install_request_code.text(JSON.stringify(req, null, 2));
    },

    validate_parameters: function($parameters_placeholder){
      var has_empty = false;
      $parameters_placeholder.find('input.parameter-value').each(function(i, el){
        if (!$(el).val()){
          has_empty = true;
        }
      });

      $parameters_placeholder.find('.wizard-next').toggleClass('disabled', has_empty);
    },

    init: function () {


      // init dependency tree
      DependencyTree.product_install_template = this.product_install_template;

      this.product_master_start();

      this.$install_list_products.on('click', '.install-select-menu>li', function(){
        Install.dependency_option_selected($(this));
      });
      // bind validators
      //checking params on table
      WizardTabs.$product_params.on('change keyup', 'input.parameter-value', function(ev){
        Install.validate_parameters(WizardTabs.$product_params);
      });
      WizardTabs.$application_params.on('change keyup', 'input.parameter-value', function(ev){
        Install.validate_parameters(WizardTabs.$application_params);
      });

      // bind clicks
//      $('.wizard-next').click(Install.next);

//      $('#btn-start-install').click(function(ev){
//        Install.request_install();
//      });

    },
    initial_request: function(response){
          Status.hide();
          Install.current_state = response.data.state;
          Install.items = response.data.items;
          Install.update();
           if(!Install.products_has_parameters){
            $("#tab-pill-product-parameters").hide();

          }
          Install.render_up_buttons();
    },
    // at first time we use server  like an echo server
    // but if user refresh page we are getting products requested in previous work
    product_master_start: function(){
       // check request products
       // we need avoid of this
        var p = Common.get_query_variable('products');
        if (p){
          Install.requested_items = p.split(';');
        }
        var req = {
          "command":"start",
          "requested_products": Install.requested_items,
        }
        ZooApi.post(ZooApi.Urls.install, req, Install.initial_request);

    },


  };




  WizardTabs = {

    $pills: $('#install-pills'),

    $pill_list: $('#tab-pill-list'),
    $pill_product_params: $('#tab-pill-product-parameters'),
    $pill_web_site: $('#tab-pill-web-site'),
    $pill_database: $('#tab-pill-database'),
    $pill_application_params: $('#tab-pill-application-parameters'),
    $pill_install: $('#tab-pill-install'),

    $list: $('#tab-list'),
    $product_params: $('#tab-product-parameters'),
    $web_site: $('#tab-web-site'),
    $database: $('#tab-database'),
    $application_params: $('#tab-application-parameters'),
    $install: $('#tab-install'),

    enable: function($pill){
      $pill.removeClass('disabled');
    },

    show_pill: function($pill){

      $pill.removeClass('hidden');
    },

    hide_pills: function(){
      this.$pills.find('>li').not(':first').not(':last').addClass('hidden');
    },

    get_tab: function($pill){
      return $($pill.find('>a').attr('href'));
    },

    next: function(ev){
      var $active_pill = WizardTabs.$pills.find('>.active');
      var $next_pill = $active_pill.nextAll().filter(':visible:first');

      if ($next_pill.length){
        WizardTabs.enable($next_pill);
        $next_pill.find('>a').tab('show');
        var $tab = WizardTabs.get_tab($next_pill);
        $tab.find('input[type=text]:first').focus();
      }
    },


  };