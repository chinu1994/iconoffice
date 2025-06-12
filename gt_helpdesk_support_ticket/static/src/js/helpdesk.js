odoo.define('gt_helpdesk_support_ticket.helpdesk', function(require) {
    "use strict";


var ajax = require('web.ajax');
//var website = require('website.website');
var base = require('web_editor.base');
//require('website_sale.website_sale');



$('#send_form').click(function (event) {
        alert("DKDKDKDKKD")
        lol = document.getElementById('csrf_token').value;
        alert("Button"+lol)
        var $form = $(this).closest('form');
        event.preventDefault();	
        ajax.jsonRpc("/page/modal", 'call', {
                'team_id': lol
                }).then(function (result) {

                        return result;
                });



 });


//        $(".remove").click(function() {
//        var id = $(this).attr('id');
//        alert(id); // debug
//        // AJAX call here
//        });





});
