odoo.define('gt_helpdesk_support_ticket.website_support', function(require) {
    'use strict';



    var ajax = require('web.ajax');
    var tour = require('web_tour.tour');
    var base = require('web_editor.base');
//    var website = require('website.website');
    var base = require('web_editor.base');

//    alert("DDDDDDDDDDDDD")

//    $('.o_website_attachment_message').on("click", function () {
//        debugger;
//        var fake_path = document.getElementById('base64').value,
//            ticket_id = $('#ticket_id').val(),
//            file_name = document.getElementById('attachment_tdocs').files[0],
//            mimetype = document.getElementById('attachment_tdocs').files[0].type;
//        $(".message_preloader").css("display", "block");
//        ajax.jsonRpc("/send/attachment", 'call', {
//            'fake_path': fake_path,
//            'ticket_id': ticket_id,
//            'file_name': file_name,
//            file_name,
//            }).then(function (result) {
//            var response = JSON.parse(result).name;
//            $('.attchmntsLinks')[0].innerHTML = response + "<br/>" + $('.attchmntsLinks')[0].innerHTML;
//            $(".message_preloader").css("display", "none");
//        });
//    });


    $('.send_customer_message').on("click", function () {
        var sendMessage = $('#customer_message').val(),
            ticket_id = $('#ticket_id').val();
        $(".message_preloader").css("display", "block");
        ajax.jsonRpc("/send/message", 'call', {
            'sendMessage': sendMessage,
            'ticket_id': ticket_id,
            }).then(function (result) {
            var response = JSON.parse(result).last_message;
            var append_html = "<hr/>"+
                                "<div class='o_thread_message  o_mail_discussion'>"+
                                    "<div class='o_thread_message_core'>"+
                                        "<p class='o_mail_info text-muted'>"+
                                            "<strong class='o_thread_author'>"+response['email_from']+
                                            "</strong>"+
                                            "-"+
                                            "<small class='o_mail_timestamp'"+
                                                   "-att-title='"+response['create_date']+"'>"+
                                                response['date']+
                                            "</small>"+
                                        "</p>"+
                                        "<div class='o_thread_message_content'>"+
                                        response['message']+
                                        "</div>"+
                                    "</div>"+
                                   "</div>";
                $('.o_mail_thread')[0].innerHTML = append_html + $('.o_mail_thread')[0].innerHTML;
                $(".message_preloader").css("display", "none");
        }).fail(function () {
            $(".message_preloader").css("display", "none");
        });
    });




    $('#send_form').click(function (event) {

            var userPass = document.getElementById('dev_msg').value;
            var rc_no = document.getElementById('rc_id').value;
//            alert("Button"+userPass)


            ajax.jsonRpc("/page/modal", 'call', {
                    'dev_id': userPass,
                    'rc_id': rc_no
                    }).then(function (result) {
                    window.location.reload();
                    document.getElementById('dev_msg').value = "";
                    document.getElementById('rc_id').value = "";

                });


     });





    tour.register('website_support', {
        test: true,
        url: '/page/helpdesk_detail',
        wait_for: base.ready(),
    }, [{
        content: "Customer name",
        trigger: "input[name=customer]",
        run: "text John Smith",
    }, {
        content: "Complete Email",
        trigger: "input[name=email_id]",
        run: "text john@smith.com"
    }, {
        content: "Complete phone number",
        trigger: "input[name=phone]",
        run: "text 118.218"
    }, {
        content: "Send the form",
        trigger: ".o_website_form_send"
    }, {
        content: "Check we were redirected to the success page",
        trigger: "#wrap:has(h1:contains('Thanks')):has(div.alert-success)"
    }]);





    return {};
});


$(document).ready(function () {
    $('.material-button-toggle').on("click", function () {
        $(this).toggleClass('open');
        $('.option').toggleClass('scale-on');
    });


//
//    $('#send_form').click(function (event) {
//
//        var msg_val = document.getElementById('csrf_token').value
//        alert(msg_val)
//        var $form = $(this).closest('form');
//        event.preventDefault();
//        ajax.jsonRpc("/page/modal1", 'call', {
//                'team_id': msg_val,
//                });
//
//
// });
//




});
