/*
Function to control selectpicker (bootstrap-select)
*/
$(document).ready(function () {

    // Variable definition
    var current_page_container = $('#content .container_reference.is_loaded.active');

    var selectpicker_divs = current_page_container.find('.selectpicker_container.load-js-controller');
    selectpicker_divs.removeClass('load-js-controller');

    var x_content = selectpicker_divs.parent();
    var url_load = x_content.find('.url_load').first();
    var url = url_load.attr('url');
    var url_action = url_load.attr('url_action');

    var termTemplate = "<span class='ui-autocomplete-term'>%s</span>";
    var term, acData, styledTerm;


    // Instanciate selectpickers
    selectpicker_divs.find('.selectpicker').selectpicker();

    // Instanciate tokenfields
    selectpicker_divs.find('.tokenfield_item').each(function() {
        var tokenfield_url = $(this).attr('url');

        $(this).tokenfield({
            autocomplete: {

                // Minimum length of search keyword
                minLength: 2,

                // Source JSON array for loading search results when keyword is sent (including caching)
                source: function (request, response) {
                    term = request.term;

                    $.get(tokenfield_url, request, function(data, status, xhr) {
                        response(data);
                    });
                },

                // Display the autocomplete results in the search bar
                open: function(e,ui) {
                    acData = $(this).data('ui-autocomplete');
                    styledTerm = termTemplate.replace('%s', acData.term);

                    acData
                        .menu
                        .element
                        .find('.ui-menu-item-wrapper')
                        .each(function() {
                            var me = $(this);
                            var pattern = new RegExp(acData.term, 'gi');
                            me.html(me.text().replace(pattern, styledTerm));
                            // me.html(me.text().replace(acData.term, styledTerm));
                        });
                },

                // close : function (event, ui) {
                //     if (!$("ul.ui-autocomplete").is(":visible")) {
                //         $("ul.ui-autocomplete").show();
                //     }
                // },

                delay: 100
            },
            showAutocompleteOnFocus: true,
            delimiter: '|',
            beautify: false
        })
        .on('tokenfield:createtoken', function (event) {
            var existingTokens = $(this).tokenfield('getTokens');
            $.each(existingTokens, function(index, token) {
                if (token.value === event.attrs.value) {
                    event.preventDefault();
                }
            });

        })

    });

});
