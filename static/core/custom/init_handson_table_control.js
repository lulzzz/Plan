/*
Function to control the handsontable call
*/
$(document).ready(function () {

    // Variable definition
    var current_page_container = $('#content .container_reference.is_loaded.active');

    var this_div = current_page_container.find('.handsontable.load-js-controller').first();
    var url_action = this_div.parent().parent().attr('url_action');
    var url_action_helper = this_div.parent().parent().attr('url_action_helper');
    this_div.removeClass('load-js-controller');
    this_div.parent().find('.alert, .loading_icon_small').hide();
    var save_button;

    // Get table header
    $.getJSON(url_action_helper, function(colheader) {

        // Perform JSON request to load data into table
        $.getJSON(url_action, function(data) {

            function errorRowRenderer(instance, td, row, col, prop, value, cellProperties) {
                Handsontable.renderers.TextRenderer.apply(this, arguments);
                td.style.color = '#a94442';
                td.style.background = '#f2dede';
            }

            function successRowRenderer(instance, td, row, col, prop, value, cellProperties) {
                Handsontable.renderers.TextRenderer.apply(this, arguments);
                td.style.color = '#3c763d;';
                td.style.background = '#dff0d8';
            }

            function normalRowRenderer(instance, td, row, col, prop, value, cellProperties) {
                Handsontable.renderers.TextRenderer.apply(this, arguments);
                td.style.color = '#73879C;';
                td.style.background = '#FFFFFF';
            }

            // if (!$.isEmptyObject(data[0])){
            //     var columns = $.map(data[0], function(element,index) {return {data: index}});
            // } else {
            //     var columns = [];
            //     for (var i = 0; i < colheader.length; i++) {
            //         columns.push({data:colheader[i]});
            //     }
            // }

            // Store whether table was initialized empty (useful for refresh)
            var table_init_empty = $.isEmptyObject(data[0]);

            // Load handsontable
            var $container = this_div.handsontable({
                data: data,
                colHeaders: colheader,
                // columns: columns,
                minCols: colheader.length,
                maxCols: colheader.length,
                rowHeaders: true,
                minSpareRows: 1,
                columnSorting: true,
                sortIndicator: true,
                width: '100%',
                stretchH: "all",
                height: 420,
                filters: true,
                dropdownMenu: ['filter_by_condition', 'filter_by_value', 'filter_action_bar']
            });

            // Handle save button event
            save_button = this_div.parent().find('.save-button');
            save_button.click(function(){

                // Disable button
                save_button.prop('disabled', true);

                // Show loading icon
                this_div.parent().find('.loading_icon_small').show();
                this_div.parent().find('.alert').hide();
                this_div.parent().find('.alert_message').text('');

                // Prepare data to post
                var post_data = {
                    'csrfmiddlewaretoken': this_div.parent().find('[name=csrfmiddlewaretoken]').val(),
                    'data': JSON.stringify($container.handsontable('getSourceData'))
                };

                // Post
                $.post(url_action, post_data)
                .done(function(data) {

                    // Update success alert message
                    this_div.parent().find('.alert').removeClass('alert-danger').addClass('alert-success').show();
                    this_div.parent().find('.alert_message').text(data);

                    $.getJSON(url_action, function(data_refresh) {
                        if (!table_init_empty){
                            $container.handsontable('loadData', data_refresh);
                        } else {
                            this_div.parent().parent().parent().parent().find('.refresh-link').trigger('click');
                        }
                    });

                    // Update row color NORMAL
                    $container.handsontable({
                        cells: function (row, col, prop) {
                            var cellProperties = {};
                            cellProperties.renderer = normalRowRenderer; // uses function directly
                            return cellProperties;
                        }
                    });

                })
                .fail(function(xhr) {
                    var error_msg = xhr.responseJSON;
                    var error_msg_line = error_msg.row + 1;

                    // Update danger alert message
                    this_div.parent().find('.alert').removeClass('alert-success').addClass('alert-danger').show();
                    this_div.parent().find('.alert_message').append('<h4><i class="fa fa-warning"></i> Warning</h4>');
                    this_div.parent().find('.alert_message').append('<p><strong>Incorrect field:</strong> ' + error_msg.error_field_label + ' at <u>row ' + error_msg_line + '</u>.</p>');
                    this_div.parent().find('.alert_message').append('<p><strong>Reason:</strong> ' + error_msg.error_field_value + '</p>');

                    // Update danger row color RED
                    $container.handsontable({
                        cells: function (row, col, prop) {
                            var cellProperties = {};

                            if (row === error_msg.row) {
                                cellProperties.renderer = errorRowRenderer; // uses function directly
                            }

                            return cellProperties;
                        }
                    });

                })
                .always(function() {

                    // Show message
                    this_div.parent().find('.alert').show();

                    // Hide loading icon
                    this_div.parent().find('.loading_icon_small').hide();

                    // Enable button
                    save_button.prop('disabled', false);

                });

            });

        });

    });

});
