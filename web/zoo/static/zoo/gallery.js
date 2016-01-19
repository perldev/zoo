$(document).ready(function () {
  window.Gallery = {

    $filters: $('#filters'),

    $installed_list: $('#product-list'),
    $not_installed_list: $('#product-list'),

    $product_list: $('.product-list'),

    $product_template: $('#product-template'),
    product_template: null,
    $filter_menu: $('#main-menu'),
    $search_input: $('#product-search-input'),

    $tag_list: $('#tag-list'),
    $tag_template: $('#tag-template'),
    tag_template: null,

    $installed_filter: $('#installed-filter'),

    filter: null,
    search: null,
    ignore_select_events: false,

    cache: {},
    engine_cache: {},

    get_filter: function(){
      if (this.filter){
        return {filter: this.filter};
      }

      if (this.search){
        return {q: this.search};
      }

      return {};
    },

    merge_product_lists: function(product_list1, product_list2){
      var result = product_list1.slice(0);
      for (var i=0; i<product_list2.length; i++){
        var product2 = product_list2[i];
        var found = false;
        for(var j=0; j<result.length; j++){
          var product1 = result[j];
          if (product1.name == product2.name){
            result[j] = product2;
            found = true;
            break;
          }
        }
        if (!found){
          result.push(product2);
        }
      }

      return result;
    },


    clear_products: function () {
      this.$product_list.find('>.product-item').remove();
    },

    load: function () {
      Status.show('Loading products');
      this.clear_products();
      ZooApi.get(ZooApi.Urls.product_list, Gallery.get_filter(), function(response) {

        // start tags loading
        if (Gallery.tag_template) {
          Gallery.clear_tags();
          ZooApi.get(ZooApi.Urls.tag_list, Gallery.get_filter(), function (response) {
            Gallery.print_tag_list(response.data);
          });
        }

        // and print products
        Gallery.print_product_list(response.data);
      });
    },

    load_engines: function() {
      var available_engines, installed_engines;

      // load not installed engines
      ZooApi.get(ZooApi.Urls.product_list, {filter: 'engine'}, function(response) {
        available_engines = response.data || [];

        Gallery.print_product_list(available_engines);

        // save engine objects to use engine titles in app configurations
        for(var i=0; i<available_engines.length; i++){
          var engine = available_engines[i];
          Gallery.engine_cache[engine.name] = engine;
        }


        /*
        ZooApi.get(ZooApi.Urls.engine_list, {}, function(response) {
          installed_engines = response.data || [];

          // var engines = installed_engines.concat(available_engines);
          var engines = Gallery.merge_product_lists(available_engines, installed_engines);
          Gallery.print_product_list(engines);

          // save engine objects to use engine titles in app configurations
          for(var i=0; i<engines.length; i++){
            var engine = engines[i];
            Gallery.engine_cache[engine.name] = engine;
          }
        });
        */
      });
    },

    print_product_list: function (items) {
      for (var i = 0; i < items.length; i++) {
        var item = items[i];
        var context = {
          engine_list: Gallery.filter == 'engine'
        };
        $.extend(context, item);
        var html = this.product_template(context);
        var $html = $(html);
        if (item.tags) {
          for (var j = 0; j < item.tags.length; j++) {
            $html.addClass('tag-' + item.tags[j]);
          }
        }

        if (item.installed_version) {
          $html.appendTo(this.$installed_list);
        } else {
          $html.appendTo(this.$not_installed_list);
        }

        this.cache[item.name] = item;
      }

      this.toggle_product_list_headers();

      Gallery.select_products(Cart.get_cart());
      Status.hide();

      this.$installed_filter.find('>a>.badge').text(this.$installed_list.find('.product-item').length);
    },

    toggle_product_list_headers: function(){
      this.$installed_list.show();
      var show_installed_items = this.$installed_list.find('.product-item:visible').length > 0;
      this.$installed_list.toggle(show_installed_items);
      this.$installed_list.prev().toggle(show_installed_items);

      this.$not_installed_list.show();
      var show_not_installed_items = this.$not_installed_list.find('.product-item:visible').length > 0;
      this.$not_installed_list.toggle(show_not_installed_items);
      this.$not_installed_list.prev().toggle(show_not_installed_items);
    },

    clear_tags: function () {
      this.$tag_list.find('>a').remove();
    },

    print_tag_list: function (items) {
      for (var i = 0; i < items.length; i++) {
        var item = items[i];
        // capitalize name first letter
        var html = this.tag_template(item);
        var $html = $(html);
        $html.attr('data-tag', item.name);
        $html.appendTo(this.$tag_list);//.slideDown();
      }

      this.$tag_list.find('>a:first').addClass('active');
    },

    tag_click: function (ev) {
      ev.preventDefault();
      var $tag_item = $(this);
      if ($tag_item.hasClass('active'))
        return;

      Gallery.$not_installed_list.show();

      var tag_name = $tag_item.attr('data-tag');
      //Gallery.$tag_list.find('>a.active').removeClass('active');
      Gallery.$filters.find('.list-group-item.active').removeClass('active');
      $tag_item.addClass('active');
      Gallery.filter_tag(tag_name);
    },


    filter_tag: function(tag_name) {
      this.$product_list.find('.product-item').each(function(i, el){
        var $product = $(el);
        if (tag_name == 'all' || $product.hasClass('tag-'+tag_name)){
          $product.show();
        } else {
          $product.hide();
        }
      });

      this.toggle_product_list_headers();
    },


    product_selected: function(ev){
      if (Gallery.ignore_select_events){
        return;
      }
      var $product_item = $(this).closest('.product-item');
      var product_name = $product_item.attr('data-product');
      var checked = $(this).is(':checked');
      if (checked){
        Cart.add_product(product_name);
      } else {
        Cart.remove_product(product_name);
      }
    },

    select_products: function(products){
      this.ignore_select_events = true;

      this.$product_list.find('.checkbox-install').prop('checked', false);

      if (products && products.length>0){
        for(var i=0; i<products.length; i++){
          var product_name = products[i];
          var $product = $('.product-item[data-product="'+product_name+'"]');
          $product.find('.checkbox-install').prop('checked', true);
        }

        Cart.update_panel(products);
      }

      this.ignore_select_events = false;
    },

    product_install_click: function(ev){
      var $product_item = $(this).closest('.product-item');
      var product_name = $product_item.attr('data-product');
      Cart.clear();
      Cart.add_product(product_name);
      Cart.click_install(ev);
    },

    product_uninstall_click: function(ev){
      var $product_item = $(this).closest('.product-item');
      var product_name = $product_item.attr('data-product');
      Cart.clear();
      Cart.add_product(product_name);
      Cart.uninstall();
    },

    get_parent_product_for_control: function($el){
      var $product_item = $el.closest('.product-item');
      var product_name = $product_item.attr('data-product');
      return this.cache[product_name];
    },

    show_installed_only: function(){
      this.filter_tag('all');
      this.$not_installed_list.find('.product-item').hide();
      this.toggle_product_list_headers();
    },

    get_engine: function(engine_name){
      if (this.engine_cache.hasOwnProperty(engine_name)){
        return this.engine_cache[engine_name];
      }
      return null;
    },

    init: function (settings) {

      this.$installed_list = settings.$installed_list;
      this.$not_installed_list = settings.$not_installed_list;

      this.$installed_list.empty();
      this.$not_installed_list.empty();

      this.product_template = Handlebars.compile(this.$product_template.html());
      if (this.$tag_template.length > 0) {
        this.tag_template = Handlebars.compile(this.$tag_template.html());
      }

      // highlight filter
      var filter = settings.filter || Common.get_query_variable('filter');
      var search = Common.get_query_variable('q');
      if (search) {
        this.search = search;
        this.$search_input.val(this.search).focus();
      } else {
        this.filter = filter || 'product';
        this.$filter_menu.find('>li[data-filter=' + this.filter + ']').addClass('active');
      }

      this.$tag_list.on('click', '>a', this.tag_click);
      this.$product_list.on('change', '.checkbox-install', this.product_selected);
      this.$product_list.on('click', '.product-btn-install', this.product_install_click);
      this.$product_list.on('click', '.product-btn-uninstall', this.product_uninstall_click);

      if (this.filter == 'product') {
        this.$installed_filter.find('>a').click(function () {
          Gallery.$filters.find('.list-group-item.active').removeClass('active');
          $(this).addClass('active');
          Gallery.show_installed_only();
        });
      } else {
        this.$installed_filter.hide();
      }

      if (this.filter == 'engine'){
        this.load_engines()
      } else {
        this.load();
      }
    },

    product_settings: {
      $installed_list: $('#products-installed'),
      $not_installed_list: $('#products-not-installed'),
      // filter: products or apps from query string
      filter: null
    }

  };



});
