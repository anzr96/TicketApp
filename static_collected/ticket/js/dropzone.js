var DropzoneDemo = {
    init: function () {
        Dropzone.options.mDropzoneTwo = {
            paramName: "file",
            maxFiles: 5,
            maxFilesize: 5,
            addRemoveLinks: true,
            acceptedFiles: "image/*",
            accept: function (e, o) {
                "justinbieber.jpg" == e.name ? o("Naha, you don't.") : o()
            }
        }
    }
};
DropzoneDemo.init();