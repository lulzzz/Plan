/*
Stored procedure run
*/
$(document).ready(function() {

    // Variable definition
    var current_page_container = $('#content .container_reference.is_loaded.active');

    var this_div = current_page_container.find('.table_procedure.load-js-controller').first();
    this_div.removeClass('load-js-controller');
    this_div.parent().find('.alert').hide();

    var enable_run = true;

    this_div.find('button.procedure_run_button').click(function(){

        // if run is enabled (prevent double click)
        if (enable_run) {

            // REPLACE WITH BOOTSTRAP
            // $("#dialog-confirm").find('span.text').text('Are you sure you want to run this procedure?');
            // $("#dialog-confirm").dialog({
            //     resizable: false,
            //     height: "auto",
            //     width: 400,
            //     modal: true,
            //     buttons: {
            //         "Confirm": function() {
            //             $( this ).dialog( "close" );
            //         },
            //         Cancel: function() {
            //             $(this).dialog( "close" );
            //         }
            //     }
            // });

            // Make new run impossible
            enable_run = false;

            // Focus on current button
            var current_button = $(this);
            var current_button_refresh_interval = current_button.attr('duration') * 1000 / 100;

            // Disable all buttons
            this_div.find('button.procedure_run_button').addClass('disabled');

            // Hide alert div
            this_div.parent().find('.alert').hide();
            this_div.parent().find('.alert_message').text('');

            // Set progress bar to 0
            var current_progressbar = current_button.parent().parent().find('.progress-bar').first();
            updateProgressbar(current_progressbar, 'init', 'info', '');

            // Refresh progress bar on regular intervals
            var progressbar_interval = setInterval(function(){ updateProgressbar(current_progressbar, 'loading', 'info', 'loading...') }, current_button_refresh_interval);

            // Run the stored procedure and wait for response boolean
            $.get($(this).attr('url'), function(data) {

                // Identify current color for button depending on response boolean
                current_button.removeClass('btn-default');
                if(data.message){
                    current_button.addClass('btn-success');
                } else{
                    current_button.addClass('btn-danger');
                }

                // Stop the progress bar loading and show success
                clearInterval(progressbar_interval);
                updateProgressbar(current_progressbar, 'completed', 'success', 'completed');

                // Refresh div and show
                this_div.parent().parent().parent().find('.refresh-link').trigger('click');

            })
            .fail(function(xhr) {
                var message;
                if ( xhr.hasOwnProperty('responseJSON') ) {
                    var error_msg = xhr.responseJSON;
                    message = error_msg.message;
                } else {
                    message = 'The stored procedure returned errors. Please contact the admin.'
                }

                // Update danger alert message
                this_div.parent().find('.alert').removeClass('alert-success').addClass('alert-danger').show();
                this_div.parent().find('.alert_message').append('<h4><i class="fa fa-warning"></i> Error</h4>');
                this_div.parent().find('.alert_message').append('<p><strong>Reason:</strong> ' + message + '</p>');

                // Show message
                this_div.parent().find('.alert').show();

                // Display button in danger color
                current_button.removeClass('btn-default').addClass('btn-danger');

                // Stop the progress bar loading and show danger
                clearInterval(progressbar_interval);
                updateProgressbar(current_progressbar, 'completed', 'danger', 'crashed');
            })
            .always(function() {
                // Enable all buttons after the procedure finished running
                this_div.find('button.procedure_run_button').removeClass('disabled');
                enable_run = true;
            })

        }

    });

});
