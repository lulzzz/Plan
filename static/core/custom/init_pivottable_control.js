/*
Function to control the worldmap
*/
$(document).ready(function () {

    // Variable definition
    var current_page_container = $('#content .container_reference.is_loaded.active');

    var this_div = current_page_container.find('.pivottable.load-js-controller').first();
    this_div.removeClass('load-js-controller');
    var url_action = this_div.parent().attr('url_action');

    // Config
    var pivottable_cols = [];
    if (this_div.parent().attr('pivottable_cols')){
        pivottable_cols = this_div.parent().attr('pivottable_cols').split(',');
    }
    var pivottable_rows = [];
    if (this_div.parent().attr('pivottable_rows')){
        pivottable_rows = this_div.parent().attr('pivottable_rows').split(',');
    }

    var pivottable_vals = [];
    if (this_div.parent().attr('pivottable_vals')){
        pivottable_vals = this_div.parent().attr('pivottable_vals').split(',');
    }

    var aggregator_name = 'Sum';
    if (this_div.parent().attr('aggregator_name')){
        aggregator_name = this_div.parent().attr('aggregator_name');
    }

    var renderer_name = 'Table';
    if (this_div.parent().attr('renderer_name')){
        renderer_name = this_div.parent().attr('renderer_name');
    }

    // Show loading bar while table is loading
    this_div.parent().parent().find('.loading_subcontainer').first().show();

    // Catch post data
    var post_data = this_div.parent().attr('post_data');

    // Check if panel has post data
    if (post_data == '') {

        // Perform JSON request to load data into table
        $.getJSON(url_action, function(data) {
            // Display
            display_pivottable(this_div, data, pivottable_cols, pivottable_rows, pivottable_vals);
        });

    }

    else {

        // Post serialized data to server
        $.post(url_action, post_data, function(data) {
            // Display
            display_pivottable(this_div, data, pivottable_cols, pivottable_rows, pivottable_vals);
        });

    }

    // Pivottable display function
    function display_pivottable(this_div, data, pivottable_cols, pivottable_rows, pivottable_vals) {

        // Hide loading bar
        this_div.parent().parent().find('.loading_subcontainer').first().hide();

        // Pivot Table
        this_div.pivotUI(data, {
            cols: pivottable_cols,
            rows: pivottable_rows,
            vals: pivottable_vals,
            aggregatorName: aggregator_name,
            rendererName: renderer_name
        });

    }

});
