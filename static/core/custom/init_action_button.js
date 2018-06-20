/*
Function to control the action buttons
*/
$(document).ready(function () {

    // Variable definition
    var current_page_container = $('#content .container_reference.is_loaded.active');

    var this_div = current_page_container.find('.action_button_container.load-js-controller').first();
    this_div.removeClass('load-js-controller');

    this_div.find('.action_button').click(function(){
        var url = $(this).attr('url');
    });

});
