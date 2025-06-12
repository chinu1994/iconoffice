odoo.define('allure_backend_theme.Planner', function (require) {
    "use strict";

    var planner = require('web.planner.common');

    planner.PlannerLauncher.include({
        start: function () {
            var res = this._super.apply(this, arguments);
            this.$progress = this.$(".o_progress");
            this.$progress.tooltip({
                html: true,
                placement: 'bottom',
                delay: {'show': 500}
            });
            this._loadPlannerDef = this._fetch_planner_data();
            return res
        },
        _update_parent_progress_bar: function (percent) {
            this.$progress.toggleClass("o_hidden", percent >= 100);
            this.$progress.addClass('p' + percent);
            this.$progress.find('.o_text').text(percent + '%');
        },
    });
});
