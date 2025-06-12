odoo.define('allure_backend_theme.ActivityMenu', function (require) {
    "use strict";

    var core = require('web.core');
    var session = require('web.session');
    var ActivityMenu = require('mail.systray.ActivityMenu');
    var QWeb = core.qweb;


    ActivityMenu.include({
        _fileExists: function (filename) {
            filename = filename.trim();
            var response = jQuery.ajax({
                url: filename,
                type: 'HEAD',
                async: false
            }).status;
            return (response == "200");
        },
        _getActivityData: function () {
            var self = this;
            return self._rpc({
                model: 'res.users',
                method: 'systray_get_activities',
                args: [],
                kwargs: {context: session.user_context},
            }).then(function (data) {
                return self._rpc({
                    model: 'ir.web.theme',
                    method: 'get_icon_state',
                    kwargs: {context: session.user_context},
                }).then(function (result) {
                    self._activities = data;
                    if (result === '2d_icon') {
                        var iconPath = '/allure_backend_theme/static/src/img/menu_2d/';
                        self._activities = _.map(data, function (rec) {
                            var iconName = rec.icon.split('/')[1];
                            if (self._fileExists(iconPath + iconName + '.png')) {
                                rec.icon = iconPath + iconName + ".png"
                            } else {
                                rec.icon = iconPath + "/custom.png";
                                if (self._fileExists("/" + iconName + "/static/description/icon.png")) {
                                    rec.icon = "/" + iconName + "/static/description/icon.png";
                                }
                            }
                            return rec;
                        });
                    }else if(result === '3d_icon') {
                        var iconPath = '/allure_backend_theme/static/src/img/menu/';
                        self._activities = _.map(data, function (rec) {
                            var iconName = rec.icon.split('/')[1];
                            if (self._fileExists(iconPath + iconName + '.png')) {
                                rec.icon = iconPath + iconName + ".png"
                            } else {
                                rec.icon = iconPath + "/custom.png";
                                if (self._fileExists("/" + iconName + "/static/description/icon.png")) {
                                    rec.icon = "/" + iconName + "/static/description/icon.png";
                                }
                            }
                            return rec;
                        });
                    }
                    self.menuType = result;
                    self.activityCounter = _.reduce(data, function (total_count, p_data) {
                        return total_count + p_data.total_count || 0;
                    }, 0);
                    self.$('.o_notification_counter').text(self.activityCounter);
                    self.$el.toggleClass('o_no_notification', !self.activityCounter);
                });
            });
        },
        _updateActivityPreview: function () {
            var self = this;
            self._getActivityData().then(function (){
                self._$activitiesPreview.html(QWeb.render('mail.systray.ActivityMenu.Previews', {
                    activities : self._activities,
                    menuType: self.menuType
                }));
            });
        },
    });
});
