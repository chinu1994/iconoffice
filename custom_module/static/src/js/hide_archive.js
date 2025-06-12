odoo.define('custom_module.BasicView', function (require) {
    "use strict";

    var session = require('web.session');
//    var BasicController = require('web.BasicController');
//    BasicController.include({
//            init: function(parent, model, renderer, params) {
//                var self = this;
//                this._super.apply(this, arguments);
//                var model = self.modelName in ['helpdesk.ticket'] ? 'True' : 'False';
//                if(model) {
//                    session.user_has_group('custom_module.hd_support_contractor_access').then(function(has_group) {
//                        if(has_group) {
//                            self.archiveEnabled = false;
//                        }
//                    });
//                }
//            },
//    });

    var BasicView = require("web.BasicView");
    BasicView.include({
        init: function (viewInfo, params) {
            var self = this;
            this._super.apply(this, arguments);
            var model = self.controllerParams.modelName == "helpdesk.ticket" ? true : false;
            if(model) {
                session.user_has_group('custom_module.hd_support_contractor_access').then(function(has_group) {
                    if(has_group) {
                        self.controllerParams.archiveEnabled = false;
                    }
                });
            }
        },
    });

});