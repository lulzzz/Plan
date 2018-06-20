

/*
*   Search
*/

$(document).ready(function() {

    var search_url = $('#search').attr('url');
    var termTemplate = "<span class='ui-autocomplete-term'>%s</span>";
    var term, acData, styledTerm;
    var cache = {};

    // AJAX Search Bar with Autocomplete
    $('#search').autocomplete({

        // Minimum length of search keyword
        minLength: 2,

        // Source JSON array for loading search results when keyword is sent (including caching)
        source: function (request, response) {
            term = request.term;
            if (term in cache) {
                response(cache[term]);
                return;
            }

            $.get(search_url, request, function(data, status, xhr) {
                cache[term] = data;
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

        // Load the search result content in the respective container
        select: function(event, ui) {

            // Prevent default entire page load
            event.preventDefault();

            // Display result label in search field
            $('#search').val(ui.item.label);

            // Store in history and update URL hash
            window.location.hash = ui.item.url;
        },

        // Refresh the value shown in the search bar when going through autocomplete results with the arrow keys
        focus: function(event, ui) {
            event.preventDefault();
            $('#search').val(ui.item.label);
        }
    });

});
