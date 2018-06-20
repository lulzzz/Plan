$(document).ready(function() {

    var current_page_container = $('#content .container_reference.is_loaded.active');

    var this_div = current_page_container.find('form.dropzone.load-js-controller').first();
    this_div.removeClass('load-js-controller');
    var url_action = this_div.parent().attr('url_action');
    var dependency_list = this_div.parent().attr('dependency_list');

    this_div.dropzone({
        url: url_action,
        // maxFiles: 1,
        maxFilesize: 15, // file size in Mb
        acceptedFiles: 'image/*,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        addRemoveLinks: true,
        init: function () {
            this.on("complete", function (file) {
                if (this.getUploadingFiles().length === 0 && this.getQueuedFiles().length === 0) {

                    // Eventually refresh connected panels and update url_pk
                    if (dependency_list) {
                        refresh_dependent_panels(current_page_container, dependency_list, null);
                    }

                }
            });

            // this.on("addedfile", function() {
            //     if (this.files[1]!=null){
            //         this.removeFile(this.files[0]);
            //     }
            // });
        }
    });


});
