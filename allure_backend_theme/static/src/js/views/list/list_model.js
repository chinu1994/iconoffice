odoo.define('allure_backend_theme.ListModel', function (require) {
    "use strict";

    var BasicModel = require('web.BasicModel');

    var ListModel = BasicModel.extend({
        get: function () {
            var result = this._super.apply(this, arguments);
            var dp = result && this.localData[result.id];
            if (dp) {
                if (dp.attachmentsData) {
                    result.attachmentsData = $.extend(true, {}, dp.attachmentsData);
                }
                if (dp.nbAttahments) {
                    result.nbAttahments = $.extend(true, {}, dp.nbAttahments);
                }
                if (dp.displayDensity) {
                    result.displayDensity = $.extend(true, {}, dp.displayDensity);
                }
            }
            return result;
        },
        _load: function (dataPoint, options) {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                if (dataPoint) {
                    return self._loadAttachemts(dataPoint);
                }
            });
        },
        _loadAttachemts: function (dataPoint) {
            var self = this;
            return self._rpc({
                model: 'ir.attachment',
                method: 'get_attachments',
                args: [[], dataPoint.model, dataPoint.domain, dataPoint.context]
            }).then(function (record) {
                _.extend(dataPoint, record);
                return record;
            });
        }
    });
    return ListModel;
});
