/*
Function to control the icheck
*/
$(document).ready(function () {

    // Variable definition
    var current_page_container = $('#content .container_reference.is_loaded.active');

    var this_div = current_page_container.find('.image_paginator.load-js-controller').first();
    this_div.removeClass('load-js-controller');
    var url = this_div.parent().attr('url');
    var dependency_list = this_div.parent().attr('dependency_list');

    // Catch page changes
    this_div.find('a').click(function(){

        // Remove selections
        this_div.find('.was_selected').removeClass('was_selected');

        // Add current selection
        $(this).parent().parent().parent().parent().addClass('was_selected');

        // Update dependent_panel
        if (dependency_list) {
            refresh_dependent_panels(current_page_container, dependency_list, $(this).attr('pk'));
        }

    });

});
