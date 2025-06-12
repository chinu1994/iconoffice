odoo.define('ks_ecommerce_theme.ks_cart_hover', function (require) {
   'use strict';

    var ks_core = require('web.core');
    var ks_ajax = require('web.ajax');
    var _t = ks_core._t;

    $(document).on('blur', '.mycart-popover input.js_quantity[data-product-id]', function (ev) {
        var $input = $(ev.currentTarget);
        var qty = parseInt($input.val());
        if (isNaN(qty)) qty = 1;
        var max_qty = parseFloat($input.data("limit_max"));
        var $td = $input.closest('td');
        var $error = $td.find('.qty_limit_error');

        var string_show = 'Can\'t order more than ' + max_qty + ' quantity!'
        if (qty > max_qty) {
            $error.html('<div class="text-danger err_msg"><sup>*</sup> ' + string_show + '</div>');
        } else {
            var line_id = parseInt($input.data('line-id'), 10);
            var value = parseInt($input.val() || 0, 10);
            var $q = $(".my_cart_quantity");

            ks_ajax.jsonRpc("/shop/cart/update_json", 'call',{
                line_id: line_id,
                product_id: parseInt($input.data('product-id'), 10),
                set_qty: value
            }).then(function (data) {
                $input.data('update_change', false);
                if(data.cart_quantity){
                    $(".view_cart_button").html(data.cart_quantity+" )"+ _t(" items"));
                }
                $q.html(data.cart_quantity).hide().fadeIn(600);
                $('.js_quantity[data-line-id='+line_id+']').val(data.quantity).html(data.quantity);
                $(".js_cart_summary").first().before(data['website_sale.short_cart_summary']).end().remove();
                if(value===0){
                      $tr.hide(300, function () {
                         $tr.remove();
                      });
                }
                $error.html('');
            });
        }
    });

    $(document).on('click', '.hover-cart', function(ev) {
        ev.preventDefault();
        var $link = $(ev.currentTarget);
        var $tr = $(ev.currentTarget.closest("tr"));
        var $input = $link.closest('.input-group').find("input");
        var min = parseFloat($input.data("min") || 0);
        var max = parseFloat($input.data("max") || Infinity);
        var quantity = ($link.has(".fa-minus").length ? -1 : 1) + parseFloat($input.val() || 0, 10);
        var newQty = quantity > min ? (quantity < max ? quantity : max) : min;
        $input.val(newQty).trigger('change');
        var $td = $input.closest('td');
        var $error = $td.find('.qty_limit_error');

        var line_id = parseInt($input.data('line-id'), 10);
        var value = parseInt($input.val() || 0, 10);
        var $q = $(".my_cart_quantity");

        var qty = parseFloat($input.val());
        var max_qty = $input.data("limit_max");
        var hasMaxQty = isNaN(max_qty) ? false : true;
        $error.html('');
        if (hasMaxQty) {
            max_qty = parseFloat($input.data("limit_max"));
            var string_show = 'Can\'t order more than ' + max_qty + ' quantity!'
            if (qty > max_qty || qty == max_qty) {
                $input.val(max_qty).trigger('change');
                $error.html('<div class="text-danger err_msg"><sup>*</sup> ' + string_show + '</div>');
                return;
            }
        }

        ks_ajax.jsonRpc("/shop/cart/update_json", 'call',{
                line_id: line_id,
                product_id: parseInt($input.data('product-id'), 10),
                set_qty: value
            }).then(function (data) {
                $input.data('update_change', false);
                if(data.cart_quantity){
                    $(".view_cart_button").html(data.cart_quantity+" )"+ _t(" items"));
                }
                else{
                   location.reload();
                }
                $q.html(data.cart_quantity).hide().fadeIn(600);
                $('.js_quantity[data-line-id='+line_id+']').val(data.quantity).html(data.quantity);
                $(".js_cart_summary").first().before(data['website_sale.short_cart_summary']).end().remove();
                if(value===0){
                      $tr.hide(300, function () {
                         $tr.remove();
                      });
                }
            });
        return false;
    });
    $(document).on('click', '.js_delete_from_popup', function(ev){
        ev.preventDefault();
        var $link = $(ev.currentTarget);
        var $tr = $(ev.currentTarget.closest("tr"));
        var $input = $tr.find(".td-qty .input-group input")
        $(ev.currentTarget).closest('tr').find('.js_quantity').val(0).trigger('change');
         $input.data('update_change', false);
         $input.trigger('change');
         var line_id = parseInt($input.data('line-id'), 10);
         var value = parseInt($input.val() || 0, 10);
         var $q = $(".my_cart_quantity");

         ks_ajax.jsonRpc("/shop/cart/update_json", 'call',{
                line_id: line_id,
                product_id: parseInt($input.data('product-id'), 10),
                set_qty: value
            }).then(function (data) {
                 $input.data('update_change', false);
                $q.html(data.cart_quantity).hide().fadeIn(600);
                $tr.hide(300, function () {
                         $tr.remove();
                });
                if(data.cart_quantity){
                    $(".view_cart_button").html(data.cart_quantity+" )"+ _t("items"));
                }
                else{
                    location.reload();
                }
                $('.js_quantity[data-line-id='+line_id+']').val(data.quantity).html(data.quantity);
                $(".js_cart_lines").first().before(data['website_sale.cart_lines']).end().remove();
                $(".js_cart_summary").first().before(data['website_sale.short_cart_summary']).end().remove();
            });
    });

});


