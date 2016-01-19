$(document).ready(function () {
  window.TaskList = {

    $task_list: $('#task-list'),
    $task_template: $('#task-item-template'),
    task_template: null,

    load: function(){
      ZooApi.get(ZooApi.Urls.task_list, {}, function(response){
        TaskList.print_task_list(response.data);
      });
    },

    print_task_list: function(items){
      if (items && items.length) {
        this.$task_list.empty();
        for (var i = 0; i < items.length; i++) {
          var item = items[i];
          var html = this.task_template({task: item});
          var $html = $(html);
          $html.appendTo(this.$task_list);
        }
      } else {
        this.$task_list.find('.task-item').slideDown();
      }
    },

    init: function () {
      this.task_template = Handlebars.compile(this.$task_template.html());
      $('#service-menu').find('a[href="/task/"]').parent().addClass('active');
      this.load();
    }

  };

  window.TaskList.init();
});

