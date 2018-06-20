/*
c3 controller
*/
$(document).ready(function() {

    // Variable definition
    var current_page_container = $('#content .container_reference.is_loaded.active');

    var this_div = current_page_container.find('.combochartjs.load-js-controller').first();
    var url_load = this_div.parent();
    var url_action = url_load.attr('url_action');
    var chart_type = url_load.attr('type');
    this_div.removeClass('load-js-controller');

    // Catch post data
    var post_data = url_load.attr('post_data');

    // Check if url has separate date range
    var daterange_start = url_load.attr('daterange_start');
    var daterange_end = url_load.attr('daterange_end');

    if (daterange_start != null && daterange_end != null) {
        url_action = url_action + daterange_start + '/' + daterange_end + '/';
    }

    if (this_div.length) {

        var ratio = true;
        if(url_load.attr('panel_height')){
            ratio = false;
        }

        // Show loading bar while table is loading
        url_load.parent().find('.loading_subcontainer').first().show();

        // Check if panel has post data
        if (post_data == '') {

            // Perform JSON request to load data into table
            $.getJSON(url_action, function(data) {
                // Display chart
                display_chart(this_div, chart_type, data, ratio);
            });

        }

        else {

            // Post serialized data to server
            $.post(url_action, post_data, function(data) {
                display_chart(this_div, chart_type, data, ratio);
            });

        }
    }

    // Chart display function
    function display_chart(this_div, chart_type, data, ratio) {

        // Hide loading bar
        url_load.parent().find('.loading_subcontainer').first().hide();

        var t = c3.generate(data);

    }

});
