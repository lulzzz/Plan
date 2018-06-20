/*
Function to control the icheck
*/
$(document).ready(function () {

    // Variable definition
    var current_page_container = $('#content .container_reference.is_loaded.active');

    var this_div = current_page_container.find('.iCheck_action.load-js-controller').first();
    this_div.removeClass('load-js-controller');
    var url_action = this_div.parent().attr('url_action');
    var bulk_action_type = this_div.attr('type');
    var dependency_list = this_div.parent().attr('dependency_list');
    var url_pk;

    // Activating iCheck style
    this_div.find('input.flat').iCheck({
        labelHover: false,
        cursor: true,
        checkboxClass: 'icheckbox_flat-green',
        radioClass: 'iradio_flat-green'
    });

    // Catch checked event
    this_div.find('input.flat').on('ifChecked', function(event) {
        if(bulk_action_type == 'radiobox'){
            // Uncheck all other fields
            this_div.find('input.flat:not(#' + event.target.id + ')').iCheck('uncheck');

            // Update selection
            $.get(event.target.value, function(data) {

                // Eventually refresh connected panels and update url_pk
                if (dependency_list) {
                    url_pk = event.target.name;
                    refresh_dependent_panels(current_page_container, dependency_list, url_pk);
                }

            }).fail(function(xhr) {
                console.log('Error');
            });
        }
    });

});
