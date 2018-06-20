/*
*   History and menu control
*/
var tab_storage = [];
var default_tab = 'search';
$(document).ready(function() {

    // Variable definition
    var current_page = $('.nav li.current-page a').first();
    var current_page_name = current_page.attr('name');
    var current_page_menu_item = current_page.attr('name');
    var current_page_url = current_page.attr('href');
    var current_page_container = $('#content div[name=' + current_page_name + ']');

    // Note: the hash is the value after '#' (e.g. for /#search_tab_one_vendor/39 hash is search_tab_one_vendor/39)

    // First load
    // http://127.0.0.1:8000/#product_summary_tab
    if (window.location.hash != '') {

        var hash_url = window.location.hash;
        var hash_div = $('a.menu_control_link[href="' + hash_url + '"]').first()
        var hash_name = hash_div.attr('name');

        if (hash_div.attr('menu_item')) {
            var hash_menu_item = hash_div.attr('menu_item');
        } else {
            var hash_menu_item = hash_name;
        }

        // Store hash in history
        tab_storage.push(hash_url);

        // Load/display tab
        load_container(hash_menu_item, hash_name, hash_url, false);
        // updateTabInfo(window.location.hash);
    }

    // http://127.0.0.1:8000
    else {
        tab_storage.push(current_page_url);
        load_container(current_page_menu_item, current_page_name, current_page_url, false);
    }

    // Store the currently selected tab in the hash value
    // $(".nav li a").on("shown.bs.tab", function(e) {
    $('a.menu_control_link').click(function() {

        var hash_url = $(this).attr('href');
        var hash_name = $('a.menu_control_link[href="' + hash_url + '"]').first().attr('name');

        // Check if user is clicking on active tab
        if(hash_name != $('.nav li.current-page a').first().attr('name')) {
            tab_storage.push(hash_url);
            window.location.hash = hash_url;
        }

    });

    // Control every hash change (including browser back button History)
    window.onhashchange = function() {

        // Click events
        // http://127.0.0.1:8000/#product_summary_tab
        if (window.location.hash != '') {

            var hash_url = window.location.hash;
            var hash_div = $('a.menu_control_link[href="' + hash_url + '"]').first()
            var hash_name = hash_div.attr('name');

            if (hash_div.attr('menu_item')) {
                var hash_menu_item = hash_div.attr('menu_item');
            } else {
                var hash_menu_item = hash_name;
            }

            // Store hash in history
            if ($.inArray(hash_url, tab_storage) < 0) {
                tab_storage.push(hash_url);
            }
            load_container(hash_menu_item, hash_name, hash_url, false);

        // http://127.0.0.1:8000
        } else {
            if ($.inArray(current_page_url, tab_storage) < 0) {
                // Store hash in history
                tab_storage.push(current_page_url);
            }
            load_container(current_page_menu_item, current_page_name, current_page_url, false);
        }

    };

});


/*
Function for loading content container
*/
function load_container(current_page_menu_item, current_page_name, current_page_url_django, reload) {

    // If current_page_menu_item and current_page_name are not provided
    if (current_page_name == null) {
        // Set default search menu item
        current_page_menu_item = default_tab;
        current_page_name = current_page_url_django.substring(1);
        // Remove '/'
        current_page_name = current_page_name.split('/').join('');
        // Remove '%20' (whitespace in URL)
        current_page_name = current_page_name.split('%20').join('');
        // Remove '&' (whitespace in URL)
        current_page_name = current_page_name.split('&').join('');
    }

    // Variable definition
    var content_container = $('#content');
    var current_page_container = $('#content #' + current_page_name);
    var current_page_menu_item_container = $('#content #' + current_page_menu_item);

    // Check if the URL is valid
    if (current_page_url_django.indexOf('#') > -1) {
        var current_page_url = current_page_url_django.replace('#', '/');
        var x_content, url_load, url;

        // Remove focus from all menu item groups
        $('.nav li, .content_container, .group_container').removeClass('current-page active');
        $('.content_container, .group_container').hide();

        // Add focus to new menu item (MENU)
        if ($('a[menu_item="' + current_page_menu_item + '"]').length > 0){
            $('a[menu_item="' + current_page_menu_item + '"]').parent().addClass('current-page active');
        } else if ($('a[name="' + current_page_menu_item + '"]').length > 0){
            $('a[name="' + current_page_menu_item + '"]').parent().addClass('current-page active');
        } else {
            $('a[name="' + default_tab + '"]').parent().addClass('current-page active');
        }

        // Check if menu container content was already loaded
        if (
            reload == false &&
            current_page_container.hasClass('is_loaded') &&
            current_page_container.length > 0
        ) {

            // Show item parent (group if any) and item itself
            current_page_container.parent().show();
            current_page_container.addClass('active').show();

        } else {

            // Show loading bar
            $('#loading_container_base').show();

            // URL has corresponding menu item
            if (current_page_container.length > 0) {
                // Make container active for JS references
                current_page_container.addClass('is_loaded active');

                // Load content
                current_page_container.load(current_page_url, function() {

                    // Hide loading bar
                    $('#loading_container_base').hide();

                    // Show item parent (group if any) and item itself
                    current_page_container.parent().show();
                    current_page_container.show();

                    // Iterate through all empty panels
                    $(this).find('.x_content.panel_body').each(function() {
                        x_content = $(this);
                        url_load = x_content.find('.url_load').first();
                        url = url_load.attr('url');
                        content_container.show();

                        // Check if url as separate PK
                        if(url_load.attr('url_pk')){
                            url = url + '/' + url_load.attr('url_pk');
                        }

                        // Load panel content through AJAX calls
                        if (url != null & url != '') {
                            url_load.load(url, function() {

                                // Hide loading icon in panel that finished loading
                                $(this).parent().find('.loading_container').hide();
                            });
                        }
                    });

                });

            }

            // URL has only
            // Append new content_container to content div and load corresponding content inside through AJAX call
            else {
                current_page_menu_item_container.append($('<div class="content_container container_reference is_loaded active" id="' + current_page_name + '">')
                    .load(current_page_url, function() {

                        // Hide loading bar
                        $('#loading_container_base').hide();

                        // Show item parent (group if any) and item itself
                        $(this).parent().show();
                        $(this).show();
                        content_container.show();

                        // Iterate through all empty panels
                        $(this).find('.x_content.panel_body').each(function() {
                            x_content = $(this);
                            url_load = x_content.find('.url_load').first();
                            url = url_load.attr('url');

                            // Check if url as separate PK
                            if(url_load.attr('url_pk')){
                                url = url + '/' + url_load.attr('url_pk');
                            }

                            // Load panel content through AJAX calls
                            if (url != null & url != '') {
                                url_load.load(url, function() {

                                    // Hide loading icon in panel that finished loading
                                    $(this).parent().find('.loading_container').hide();
                                });
                            }
                        }); // each
                    }) // load
                ); // append
            } // else

        }
    }
    // Otherwise load base page
    else {
        document.location.href = "/";
    }
}
