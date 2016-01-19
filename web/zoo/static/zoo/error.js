$(document).ready(function () {
  window.ErrorMessage = {

    $modal: $('#modal-error'),
    $modal_title: $('#modal-error .modal-title'),
    $modal_body: $('#modal-error .modal-body'),

    show: function(jqxhr, status, error){
      var message;
      if (jqxhr && jqxhr.responseJSON && jqxhr.responseJSON.error){
        var err = jqxhr.responseJSON.error;
        message = 'Request: ' + jqxhr.method + ' ' + jqxhr.url +
          '\nError class: '+err['class']+
          '\nError Args: '+err.args+'\n\n'+
          err.traceback;
      } else {
        message = 'An error occured.\nStatus: ' + status + '\nError: ' + error;
      }

      message = message.replace(/\n/g, '<br/>');

      this.$modal_body.html(message);
      this.$modal.modal('show');
    },

    show_html: function(html){
      this.$modal_body.html(html);
      this.$modal.modal('show');
    },

    init: function () {
      this.$modal.modal({
        show: false
      });
    }

  };

  window.ErrorMessage.init();
});

