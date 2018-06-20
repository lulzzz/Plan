/*
DATA TABLES
*/
$(document).ready(function() {

    // Variable definition
    var current_page_container = $('#content .container_reference.is_loaded.active');

    var this_div = current_page_container.find('.datatable.load-js-controller').first();
    this_div.removeClass('load-js-controller');
    this_div.parent().find('.loading_icon_small').hide();

    var page_length = this_div.attr('page_length');
    var has_pagination = true;
    if (page_length == 'unlimited') {
        has_pagination = false;
    } else {
        page_length = parseInt(page_length);
    }

    var handleDataTableButtons = function() {
        if (this_div.length) {
            this_div.DataTable({
                dom: 'Bfrtip',
                pageLength: page_length,
                bPaginate: has_pagination,
                bInfo: has_pagination,
                autoWidth: false,
                responsive: false,
                buttons: [{
                        extend: 'copy',
                        className: 'btn-sm'
                    },
                    {
                        extend: 'csv',
                        className: 'btn-sm'
                    },
                    {
                        extend: 'excel',
                        className: 'btn-sm'
                    },
                    {
                        extend: 'pdfHtml5',
                        className: 'btn-sm'
                    },
                    {
                        extend: 'print',
                        className: 'btn-sm'
                    },
                ],
                footerCallback: function ( row, data, start, end, display ) {

                    // If table has summary footer
                    if(this_div.attr('tfoot')) {

                        // Datatable preparations
                        var api = this.api(), data;

                        // Fields to format (starts at 0)
                        var column_idx_to_sum_list = this_div.attr('tfoot').split(',');

                        // Remove the formatting to get integer data for summation
                        var intVal = function ( i ) {

                            // Extract text from input field
                            if ( $(i).is('input') ) {
                                i = $(i).val();
                            }

                            // Return numeric variable
                            return typeof i === 'string' ?
                                i.replace(/[\$,\%]/g, '')*1 :
                                typeof i === 'number' ?
                                    i : 0;
                        };

                        for (column_idx = 0; column_idx < column_idx_to_sum_list.length; column_idx++) {

                            column_idx_to_sum = column_idx_to_sum_list[column_idx];
                            // Total over all pages
                            var total = api
                                .column( column_idx_to_sum )
                                .data()
                                .reduce( function (a, b) {
                                    return intVal(a) + intVal(b);
                                }, 0 );

                            // Total over this page
                            var pageTotal = api
                                .column( column_idx_to_sum, { page: 'current'} )
                                .data()
                                .reduce( function (a, b) {
                                    return intVal(a) + intVal(b);
                                }, 0 );

                            // Update footer
                            if (pageTotal == total) {
                                $(api.column(column_idx_to_sum).footer() ).html(
                                    pageTotal.toLocaleString()
                                );
                            } else {
                                $(api.column(column_idx_to_sum).footer() ).html(
                                    pageTotal.toLocaleString() + ' (&Sigma; '+ total.toLocaleString() +')'
                                );
                            }

                        }
                    }

                }
            });
        }
    };

    TableManageButtons = function() {
        'use strict';
        return {
            init: function() {
                handleDataTableButtons();
            }
        };
    }();

    TableManageButtons.init();

});
