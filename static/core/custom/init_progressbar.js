$(document).ready(function() {

    // NProgress
    if (typeof NProgress != 'undefined') {
        $(document).ready(function() {
            NProgress.start();
        });

        $(window).load(function() {
            NProgress.done();
        });
    }

    // Progressbar
    if ($(".progress .progress-bar")[0]) {
        $('.progress .progress-bar').progressbar();
    }

});
