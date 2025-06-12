odoo.define('allure_backend_theme.ListView', function (require) {
    "use strict";
    var ListModel = require('allure_backend_theme.ListModel');
    var ListView = require('web.ListView');

    ListView.include({
        config: _.extend({}, ListView.prototype.config, {
            Model: ListModel,
        }),
        init: function (viewInfo, params) {
            this._super.apply(this, arguments);
            this.loadParams.attachmentsData = [];
            this.loadParams.resDomain = params.domain;
        },
    });
    return ListView;

});
