odoo.define('advanced_search_functionality.ListController', function(require) {
    "use strict";
    var core = require('web.core');
    var BasicController = require('web.BasicController');
    var ListController = require('web.ListController');
    var _t = core._t;
    ListController.include({
        events: _.extend({}, BasicController.prototype.events, {
            'change thead .odoo_field_search_expan': '_change_odoo_field_search_expan',
            'click .ba_search_field_erase': '_erase_search',
        }),
        _change_odoo_field_search_expan: function(event) {
            event.preventDefault();
            event.stopPropagation();
            var search = this.searchView.build_search_data();
            this.trigger_up('search', search);
        },
        _erase_search: function(event) {
            $('input.odoo_field_search_expan').val('');
            $('select.odoo_field_search_expan').val('');
            event.preventDefault();
            event.stopPropagation();
            var search = this.searchView.build_search_data();
            this.trigger_up('search', search);
        },
    });
});