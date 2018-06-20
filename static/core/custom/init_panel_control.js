/*
Function to control the panel buttons
*/
$(document).ready(function () {

    // Variable definition
    var current_page_container = $('#content .container_reference.is_loaded.active');

    // Save button (POST)
    current_page_container.find('button.save-button').click(function(){

        // Serialize form data
        if ($(this).hasClass('filter-button')) {
            var x_content = $(this).parent().parent().parent();
        } else {
            var x_panel = $(this).closest('.x_panel');
            var x_content = x_panel.find('.x_content').first();

        }

        var post_data = x_content.find('form').first().serialize();

        // Iterate through all url_load values
        x_content.find('.url_load').each(function() {

            var url_load = $(this);
            var url = url_load.attr('url');

            // Store serialized POST data
            url_load.attr('post_data', post_data);

            // Check if url has separate PK
            if(url_load.attr('url_pk')){
                url = url + '/' + url_load.attr('url_pk');
            }

            // Show loading bar
            x_content.find('.loading_container').first().show();
            url_load.hide();

            // Post serialized data to server
            $.post(url, post_data, function(data) {
                // Hide loading bar
                x_content.find('.loading_container').first().hide();

                // Overwrite result and show
                url_load.html(data).show();

            });

        });

    });

    // Refresh button (GET)
    current_page_container.find('.refresh-link').click(function(){
        var x_panel = $(this).closest('.x_panel');
        var x_content = x_panel.find('.x_content').first();
        var url_load = x_content.find('.url_load').first();
        var url = url_load.attr('url');

        // Check if url as separate PK
        if(url_load.attr('url_pk')){
            url = url + '/' + url_load.attr('url_pk');
        }

        // Show loading bar
        x_content.find('.loading_container').first().show();
        url_load.hide();

        // Refresh div and show
        url_load.load(url, function(){
            // Hide loading bar
            x_content.find('.loading_container').first().hide();
            url_load = x_content.find('.url_load').first();
            url_load.show();
        });
    });

    // Level select (GET)
    current_page_container.find('select.form_select_show').change(function(){
        // Prepare selectors
        var x_panel = $(this).closest('.x_panel');
        var x_content = x_panel.find('.x_content').first();
        var url_load = x_content.find('.url_load').first();
        url_load.attr('url_pk', $(this).val());

        // Refresh panel
        x_panel.find('.refresh-link').trigger('click');
    });

});
