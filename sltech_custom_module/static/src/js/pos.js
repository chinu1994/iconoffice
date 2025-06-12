odoo.define('sltech_custom_pos.pos', function (require) {
    "use strict";

    var core    = require('web.core');
    var rpc    = require('web.rpc');
    var screens = require('point_of_sale.screens');
    var gui     = require('point_of_sale.gui');
    var pos_model = require('point_of_sale.models');

    var _t      = core._t;

    var PopupWidget = require('point_of_sale.popups');
    var ScreenWidget = screens.ScreenWidget;
    var PaymentScreenWidget = screens.PaymentScreenWidget;

    PaymentScreenWidget.include({
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.js_set_full_amt').click(function(){
                var sltech_amount = (self.pos.get_order().get_total_with_tax()-self.pos.get_order().get_total_paid()).toString();
//                $(".delete-button").click();
//                $('.numpad-backspace[data-action=BACKSPACE]')[0].click()
                for (var i = 0; i < sltech_amount.length; i++) {
                  if (sltech_amount.charAt(i) == "."){
                    $('.number-char[data-action=\'.\']')[0].click()
                  }
                  else{
                    $('.number-char[data-action='+sltech_amount.charAt(i)+']')[0].click()
                  }
                }
            });
        }
    });




    var core = require('web.core');
    var screens = require('point_of_sale.screens');
    var field_utils = require('web.field_utils');

    var BaseWidget = require('point_of_sale.BaseWidget');

    BaseWidget.include({
        sltech_remove_halala: function(price){
            return parseInt(price);
        }
    })

//    var widget_base = require('point_of_sale.BaseWidget');
//    widget_base.include({
//        format_currency: function(amount,precision){
//            var currency = (this.pos && this.pos.currency) ? this.pos.currency : {symbol:'$', position: 'after', rounding: 0.01, decimals: 2};
//
//            amount = this.format_currency_no_symbol(amount,precision);
//
//            if (currency.position === 'after') {
//                return parseInt(amount) + ' ' + (currency.symbol || '');
//            } else {
//                return (currency.symbol || '') + ' ' + parseInt(amount);
//            }
//        },
//    })

});