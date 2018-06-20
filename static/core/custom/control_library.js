/*
Function for refreshing dependent panels
*/
function refresh_dependent_panels(current_page_container, dependency_list_obj, url_pk){

    // Split string into list
    dependency_list = $.trim(dependency_list_obj).split(" ");

    // Iterate through list
    for(var i=0; i < dependency_list.length; i++) {

        if(dependency_list[i].replace(/\s+/g, '') != "") {
            var dependent_panel = current_page_container.find(".url_load[name=" + dependency_list[i] + "]");

            if(dependent_panel.length) {
                // Update url_pk
                if(url_pk){
                    dependent_panel.attr('url_pk', url_pk);
                }

                // Refresh div and show
                dependent_panel.parent().parent().find('.refresh-link').trigger('click');
            }
        }

    }
}


/*
Function for updating progressbar
*/
function updateProgressbar(progressbar_div, current_progress, bar_type, text){
    var str_progress, current_percentage, loading_percentage;

    // Calculate new percentage
    current_percentage = parseInt(progressbar_div.attr('aria-valuenow'));
    loading_percentage = current_percentage;
    if (current_progress == 'completed') {
        loading_percentage = 100;
    }
    else if (current_progress == 'init') {
        loading_percentage = 0;
    }
    else if (loading_percentage < 99) {
        loading_percentage = current_percentage + 1;
    }
    else {
        return;
    }
    str_progress = loading_percentage + '%';

    // Update bar div
    progressbar_div
        .removeClass('progress-bar-success progress-bar-info progress-bar-danger')
        .addClass('progress-bar-' + bar_type)
        .attr('aria-valuenow', loading_percentage)
        .width(str_progress)
        .html(str_progress + ' ' + text);

}
