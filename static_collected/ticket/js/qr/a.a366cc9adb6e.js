
import QrScanner from "https://www.bs29.ir/js/qr/qr-scanner.min.js";
const video = document.getElementById('qr-video');
camQrResult = document.getElementById('cam-qr-result');
camQrResult.textContent = "None";
var search;
function setResult(label, result) {
    play_sound();
    label.textContent = result;
    label.style.color = 'teal';
    clearTimeout(label.highlightTimeout);
    label.highlightTimeout = setTimeout(() => label.style.color = 'inherit', 100);

    search = result;
    //$('#customer_username').val(result);
    $('#modal_close').click();
}
scanner = new QrScanner(video, result => setResult(camQrResult, result));
$('#scanbtn').on('click', function () {

    //const debugCheckbox = document.getElementById('debug-checkbox');
    //const debugCanvas = document.getElementById('debug-canvas');
    // const debugCanvasContext = debugCanvas.getContext('2d');

    //const fileSelector = document.getElementById('file-selector');
    //const fileQrResult = document.getElementById('file-qr-result');
    $('#invoice_field').css('display', 'none');
    document.getElementById('invoice_name').textContent = "";
    document.getElementById('cam-qr-result').textContent = "None";

    scanner.start();

});

//    	srch_str.textContent=result;

$('#modal_close').on('click', function () {
    /*if (scanner!=null)
    {
        $('#cam-qr-result').html("");
        scanner.stop();
    }*/
    searchbyqr(search);
});
//////////////////////////////////////////////////////////////
function searchbyqr(search_item) {
    $.ajax({
        type: "post",
        url: '/searchbyqrcode',
        data: {
            "_token": "4i6WtNU4UNit3FnCKC5c1xokQotSH7BfFRuyfNb8",
            "search": search_item
        },
        dataType: "json",
        success: function (data) {


            if (data != '') {

                //swal.close();


                //alert(data);
                //window.location.href = "/invoice";
                //
                //var user =  $.parseJSON(data);
                //console.log(data);
                //console.log(data[0]['customer_name']);
                //console.log("ooooooooooooooo");
                const srch_str = document.getElementById('invoice_name');
                srch_str.textContent = data[0]['customer_name'] + ' ' + data[0]['customer_lastname'];
                $('#customer_username').val(search_item);
                $('#invoice_field').css('display', 'inline');

                //$('.error_qs_li').html(data);
                //$('.error_qs_ul').css('display','block');

                //$('html, body').animate({scrollTop: '0px'}, 300);
            } else {

                $('.error_qs_li').html('مشتری مورد نظر در لیست مشتریان حاضر در سالن نیستند، لطفا به پذیرش مراجعه نمایند.');
                $('.error_qs_ul').css('display', 'block');
                $('html, body').animate({ scrollTop: '0px' }, 300);
                setTimeout(function () { $('.error_qs_ul').fadeOut('slow'); }, 3000);

                //$("#checkQuickSaleformvalidion").submit();
            }

        },
        error: function () {
            //	alert('error handing here');
        }
    });
}

//////////////////////////////////////////////////////////////


$('#search').on('change', function () {
    //console.log("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT");

});

/*$('#cam-qr-result').on('DOMSubtreeModified',function(){
    console.log($('#cam-qr-result').html());
    const srch_str = document.getElementById('search');
    srch_str.value=$('#cam-qr-result').html();
    play_sound();
    $('#modal_close').click();

});*/



function play_sound() {
    var audio = new Audio('https://www.bs29.ir/sound/beep3.wav');
    audio.play();
}
