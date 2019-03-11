function call_meassage(message, type){
    $("[data-switch=true]").bootstrapSwitch();
    let e = {message: message};
    let t = $.notify(e, {
        type: type,
        allow_dismiss: true,
        newest_on_top: true,
        mouse_over: true,
        showProgressbar: false,
        spacing: 10,
        timer: 2000,
        placement: {from: 'top', align: 'left'},
        offset: {x: 30, y: 30},
        delay: 1000,
        z_index: 5000,
        animate: {
            enter: "animated " + 'tada',
            exit: "animated " + 'rollOut'
        }
    });

}