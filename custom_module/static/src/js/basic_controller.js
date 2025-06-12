odoo.define('custom_module.basic_controller', function (require) {
    "use strict";

    var BasicController = require('web.BasicController');

    BasicController.include({

        _updatePager: function () {
            this._super.apply(this, arguments);
            if (this.pager) {
                var data = this.model.get(this.handle, {raw: true});
                if (this.mode == "readonly" && this.modelName == "helpdesk.ticket" && data.data.state == "closed") {
                    if ($('.o_control_panel').length>0 && $('.o_control_panel')[0].children.length>0 && $('.o_control_panel')[0].children[0].children.length>0){
                        $('.o_control_panel')[0].children[0].children[0].click();
                    }
                }
            }
        }

    });

//    _updatePager: function () {
//        if (this.pager) {
//            var data = this.model.get(this.handle, {raw: true});
//            this.pager.updateState({
//                current_min: data.offset + 1,
//                size: data.count,
//            });
//            var isRecord = data.type === 'record';
//            var hasData = !!data.count;
//            var isGrouped = data.groupedBy ? !!data.groupedBy.length : false;
//            var isNew = this.model.isNew(this.handle);
//            var isPagerVisible = isRecord ? !isNew : (hasData && !isGrouped);
//
//            this.pager.do_toggle(isPagerVisible);
//            if (this.mode == "readonly" && this.modelName == "helpdesk.ticket" && data.data.state == "closed") {
//                $('.o_control_panel')[0].children[0].children[0].click();
//            }
//        }
//    },

});