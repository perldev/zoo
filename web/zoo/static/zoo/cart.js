$(document).ready(function () {
  window.Cart = {

    $panel: $('#cart-panel'),
    $install_button: $('#cart-install'),
    $clear_button: $('#cart-clear'),

    add_product: function (product_name) {
      var cart = this.get_cart();
      if ($.inArray(product_name, cart) == -1){
        cart.push(product_name);
        this.set_cart(cart);
        this.update_panel(cart);
      }
    },

    remove_product: function (product_name) {
      var cart = this.get_cart();
      var index = cart.indexOf(product_name);
      if (index >= 0){
        cart.splice(index, 1);
        this.set_cart(cart);
        this.update_panel(cart);
      }
    },

    update_panel: function (items) {
      if (items && items.length > 0) {
        this.$install_button.find('>span').text('Install '+items.length+' products');
        this.$panel.show();
      } else {
        this.$panel.hide();
      }
    },

    clear: function(){
      Cart.set_cart(null);
      Cart.update_panel([]);
      Gallery.select_products([]);
    },

    get_cart: function(){
      var s = $.cookie('zoo_cart');
      if (s){
        return s.split(';');
      } else {
        return [];
      }
    },

    set_cart: function(list){
      if (list && list.length>0) {
        $.cookie('zoo_cart', list.join(';'));
      } else {
        $.removeCookie('zoo_cart');
      }
    },

    click_install: function(ev){
      var cart = Cart.get_cart();
      if (cart && cart.length>0){
        Cart.clear();
        window.location.href = '/install/?products='+cart.join(';');
      }
    },

    uninstall: function(ev){
      var cart = Cart.get_cart();
      if (cart && cart.length>0){
        Cart.clear();
        window.location.href = '/uninstall/?products='+cart.join(';');
      }
    },

    init: function () {
      this.$clear_button.click(this.clear);
      this.$install_button.click(this.click_install);
    }
  };

  window.Cart.init();
});

