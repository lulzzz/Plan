/*
Switchery
*/

$(document).ready(function() {

    // Variable definition
    var content = $('#content');

    var this_div = content.find('.group_container_control.load-js-controller').first();
    this_div.removeClass('load-js-controller');

    // pretty_checkbox
    this_div.find('.pretty_checkbox').change(function(){

        // Check if page should be reloaded
        var page_reload = $(this).hasClass('page_reload');

        // Check if checkbox was checked or unchecked
        if($(this).attr('checked')) {
            $(this).removeAttr('checked');
        } else {
            $(this).attr('checked', 'checked');
        }

        // Get correct URL
        var url = $(this).attr('url');
        if(this.checked) {
            url = url.slice(0, -1) + '1'
        } else {
            url = url.slice(0, -1) + '0'
        }

        // Get AJAX call
        $.get(url, function(data) {
            if (page_reload) {
                location.reload();
            }
        });
    });


    // filter_change
    this_div.find('.filter_change').click(function(e){
        e.preventDefault();

        // Check if page should be reloaded
        var page_reload = $(this).hasClass('page_reload');

        // Get correct URL
        var url = $(this).attr('url');

        // Get form data
        var post_data = $(this).closest('form').serialize();

        // Post serialized data to server
        $.post(url, post_data, function(data) {
            if (page_reload) {
                location.reload();
            }
        });

    });

});
