 Uninstall = {

    product_tabs:[
      "tab-pill-list",
      "tab-pill-product-uninstalling"
    ],
    product_pages:[
      "tab-list",
      "tab-product-uninstalling"
    ],
    product_page4state:{
      "start":[],
      "product_list":[],
      "uninstalling":[0]
    },

    product_tabs4state:{
      "start":[],
      "product_list":[0],
      "uninstalling":[0,1]
    },
    requested_items: [],
    state: null,
    current_state: null,
    product_uninstall_template: null,
    $product_uninstall_template:  $('#product-uninstall-template'),
    $uninstall_list: $('#uninstall-list'),
    initial_request: function(response){
        var req = {
          requested_products: Uninstall.requested_items,
          command: "product_list"
        };
        Status.show('Getting product to uninstall');
        console.log('initial request: ', req);
        ZooApi.post(ZooApi.Urls.uninstall, req, function(response){
          Uninstall.uninstall_response(response);
        });
    },
    product_master_product_list: function (response) {
          console.log(response);
          Uninstall.state = response.data.items;
          Uninstall.fill_product_list();
    },
    fill_product_list: function () {
      this.$uninstall_list.empty();
      for (var i=0; i<this.state.length; i++){
        var product = this.state[i].product;
        console.log(product);
        var html = this.product_uninstall_template(this.state[i]);
        var $html = $(html);
        $html.addClass('hide-soft');
        $html.appendTo(this.$uninstall_list).slideDown(function(){$html.removeClass('hide-soft');});
      }
    },
    hide_pages_before:function(State){
        console.log("current page hide " + this.current_state);
        for(var i=0; i<this.product_page4state[State].length; i++){
            console.log(" hide " + this.product_pages[i]);
            $("#"+this.product_pages[i]).hide();
        }
    },
    finish: function(TaskObj){
           console.log(" show finish ");
           $("#finish").removeClass("hidden");
           $("#cancel_button").hide();
    },


    render_up_buttons: function(){
        var i;
        for(i =0; i<this.product_tabs4state[this.current_state].length; i++){
            $("#"+this.product_tabs[i]).removeClass("active");

        }
        $("#first_tab").removeClass("active");
        if(this.current_state == "product_list"){
                    $("#first_tab").addClass("active");
        }
        if(i>0){
            $("#"+this.product_tabs[i-1]).addClass("active");
        }

    },
    master2uninstall: function(){
      if (Uninstall.state.length) {
        var req = {
            requested_products: Uninstall.requested_items,
            "command": "uninstall"
        };
        console.log('uninstall request:', req);
        ZooApi.post(ZooApi.Urls.uninstall, req, function(response){
          Uninstall.uninstall_response(response);
        });
      }
    },
     // process mistakes
    product_master_uninstalling: function(response){
       Uninstall.hide_pages_before(response.data.state);
       console.log("uninstalling");
       console.log(response);
       if (response.data.task.id){
           Task.task_id = response.data.task.id;
           Task.init(Uninstall);
           $("#tab-product-uninstalling").show();
       }
    },
    move_away:function(){
            window.location.href="/gallery/";
    },
    master2finish:function(ev){
        var req = {
          "command": "finish"
         };
        console.log(req);
        ZooApi.post(ZooApi.Urls.uninstall, req, Uninstall.uninstall_response);
    },
    next: function(ev){
       var Routes = {
        "product_list": Uninstall.master2uninstall,
        "uninstalling": Uninstall.move_away,
      };
      Routes[Uninstall.current_state](ev)
    },
    uninstall_response: function (response) {
      Status.hide();
      console.log('install response: ');
      console.log(response.data);

      console.log(" GOT ");
      console.log(response);
      //Install.$response_log.text(JSON.stringify(response.data, null, ' '));
      var Routes = {
        "start": Uninstall.initial_request,
        "product_list": Uninstall.product_master_product_list,
        "uninstalling": Uninstall.product_master_uninstalling,
      };
      Uninstall.current_state = response.data.state;
      Routes[Uninstall.current_state](response)
      Uninstall.render_up_buttons()


    },
     product_master_start: function(){
       // check request products
        //we need avoid of this
        var p = Common.get_query_variable('products');
        if (p){
          Uninstall.requested_items = p.split(';');
        }

        var req = {
          "command": "start",
          "requested_products": Uninstall.requested_items,
        }

        ZooApi.post(ZooApi.Urls.uninstall, req, function(response){
            Uninstall.uninstall_response(response);
        });

    },
    init: function () {

      // check request products
      var p = Common.get_query_variable('products');
      if (p){
        this.requested_items = p.split(';');
      }
      if (this.requested_items.length == 0) {
        alert('No products to uninstall');
        return;
      }

      // compile templates
      this.product_uninstall_template = Handlebars.compile(this.$product_uninstall_template.html());
      this.product_master_start();

    }



  };


