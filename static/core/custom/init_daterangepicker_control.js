/*
DATERANGEPICKER
*/

$(document).ready(function() {

    // Variable definition
    var current_page_container = $('#content .container_reference.is_loaded.active');

    var this_div = current_page_container.find('.reportrange.load-js-controller').first();
    this_div.removeClass('load-js-controller');
    var url_load_div = this_div.closest('.filter_panels_area').find('.url_load');

    var daterange_start = url_load_div.attr('daterange_start');
    var start = moment(daterange_start);

    var daterange_end = url_load_div.attr('daterange_end');
    var end = moment(daterange_end);

    // Display init range
    function cb(start, end) {
        this_div.find('span').html(start.format('MM/DD/YYYY') + ' - ' + end.format('MM/DD/YYYY'));
    }

    // Call object
    this_div.daterangepicker({
        // firstDay: 1,
        startDate: start,
        endDate: end,
        ranges: {
            'Next 6 Weeks': [start, end],
            'Next 6 Months': [start, moment().add(3, 'M')],
            'Next 1 Year': [start, moment().add(1, 'y')],
        },
        locale: {
            format: 'MM/DD/YYYY'
        }
    }, cb);

    cb(start, end);

    // Catch change event
    this_div.on('apply.daterangepicker', function(ev, picker) {
        // Update div date range attributes
        url_load_div.attr('daterange_start', picker.startDate.format('YYYY-MM-DD'));
        url_load_div.attr('daterange_end', picker.endDate.format('YYYY-MM-DD'));
    });

});
