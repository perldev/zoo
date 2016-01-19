$(document).ready(function () {
  window.Grid = {

    template: Handlebars.compile($('#grid-template').html()),


    render_edit_values: function(params){
      return this.template({params: params, edit_keys: false, can_add: false});
    },

    render_edit_keys_values: function(params){
      return this.template({params: params, edit_keys: true, can_add: true});
    },

    get_params: function($placeholder){
      var params = {};
      $placeholder.find('.form-group').each(function(i, el){
        var $el = $(el);
        var key;
        if ($el.find('input.key').length == 1){
          key = $el.find('input.key').val();
        } else {
          key = $el.attr('data-name');
        }
        if (key) {
          var val = $el.find('input.value').val();
          var number = parseInt(val, 10);
          if (!isNaN(number)){
            val = number;
          }
          params[key] = val;
        }
      });
      return params;
    },

    init: function(){
      $('body').on('click', 'form.grid .remove', function(e){
        $(this).closest('.form-group').slideUp(function(e){
          $(this).remove();
        })
      });
      $('body').on('click', 'form.grid .add', function(e){
        var $form = $(this).closest('form.grid');
        var $new_group = $form.find('.form-group').last().clone().removeClass('hide-soft');
        $new_group.find('input').val('');
        $new_group.insertAfter($form.find('.form-group').last());
        $new_group.find('input').first().focus();
      });
    }

  };

  window.Grid.init();
});

