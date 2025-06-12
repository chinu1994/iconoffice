odoo.define('allure_backend_theme.Discuss', function (require) {
"use strict";

var Discuss = require('mail.Discuss');
var SearchView = require('web.SearchView');

Discuss.include({
    _renderSearchView: function () {
        var self = this;
        var options = {
            $buttons: $('<div class="ad_has_options">'),
            action: this.action,
            disable_groupby: true,
        };
        this.searchview = new SearchView(this, this.dataset, this.fields_view, options);
        return this.alive(this.searchview.appendTo($('<div>')))
            .then(function () {
                self.$searchview_buttons = self.searchview.$buttons;
                // manually call do_search to generate the initial domain and filter
                // the messages in the default thread
                self.searchview.do_search();
            });
    },
});

});
