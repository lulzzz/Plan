/*
ChartJS controller
*/
$(document).ready(function() {

    // Variable definition
    var current_page_container = $('#content .container_reference.is_loaded.active');

    var this_div = current_page_container.find('.jstree_container.load-js-controller').first();
    var url_load = this_div.parent();
    var url_action = url_load.attr('url_action');
    var chart_type = url_load.attr('type');
    this_div.removeClass('load-js-controller');

    this_div.jstree({
      "core" : {
        "animation" : 0,
        "check_callback" : true,
        "themes" : { "stripes" : true },
        'data' : {
          'url' : 'static/core/vendors/jstree/ajax_demo_roots.json',
          'data' : function (node) {
            return { 'id' : node.id };
          }
        }
      },
      "types" : {
        "#" : {
          "max_children" : 1,
          "max_depth" : 4,
          "valid_children" : ["root"]
        },
        "root" : {
          "icon" : "/static/3.3.5/assets/images/tree_icon.png",
          "valid_children" : ["default"]
        },
        "default" : {
          "valid_children" : ["default","file"]
        },
        "file" : {
          "icon" : "glyphicon glyphicon-file",
          "valid_children" : []
        }
      },
      "plugins" : [
        "contextmenu", "dnd", "search",
        "state", "types", "wholerow"
      ]
    });

});
