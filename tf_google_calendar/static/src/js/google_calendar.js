odoo.define('tf_google_calendar.google_calendar', function (require) {
    "use strict";

//    var core = require('web.core');
//    var Dialog = require('web.Dialog');
//    var framework = require('web.framework');
//    var CalendarRenderer = require('web.CalendarRenderer');
//    var CalendarController = require('web.CalendarController');
//
//    var _t = core._t;
//
//    CalendarRenderer.include({
//        _initSidebar: function () {
//            var self = this;
//            this._super.apply(this, arguments);
////            this.$googleButton = $();
////            if (this.model === "calendar.event") {
////                this.$googleButton = $('<button/>', {type: 'button', html: _t("Sync with <b>Google</b>")})
////                                    .addClass('tf_google_calendar o_google_sync_button oe_button btn btn-secondary')
////                                    .prepend($('<img/>', {
////                                        src: "/google_calendar/static/src/img/calendar_32.png",
////                                    }))
////                                    .appendTo(self.$sidebar);
////            }
//            $("div").find(".o_notification").css( "display", "none" );
//        },
//    });
    var Notification = require('web.Notification');

    Notification.include({
        start: function () {
            var self = this;
            var return_obj = this._super.apply(this, arguments);

            var current_url = window.location.href;
            var searchParams = new URLSearchParams(current_url);
            var model_name = searchParams.get('model');
            if (model_name == 'calendar.event' || model_name == 'helpdesk.ticket' || searchParams.get('active_id') == 'mailbox_inbox'){
                this.$el.animate({opacity: 0.0, height: 0}, this._animationDelay, "swing", self.destroy.bind(self));
            }
            return return_obj;


//            return this._super.apply(this, arguments).then(function () {
//                var current_url = window.location.href;
//                var searchParams = new URLSearchParams(current_url);
//                var model_name = searchParams.get('model');
//                if (model_name != 'calendar.event'){
//                    self.$el.animate({opacity: 1.0}, self._animationDelay, "swing", function () {
//                        if(!self.sticky) {
//                            setTimeout(function () {
//                                self.close();
//                            }, self._autoCloseDelay);
//                        }
//                    });
//                }
//            });


        },
    });

    var CalendarModel = require('web.CalendarModel');
    var AbstractModel = require('web.AbstractModel');
    var Context = require('web.Context');
    var core = require('web.core');
    var fieldUtils = require('web.field_utils');
    var session = require('web.session');

    var _t = core._t;

    CalendarModel.include({
        _loadFilter: function (filter) {
            if (!filter.write_model) {
                return;
            }

            var field = this.fields[filter.fieldName];
            return this._rpc({
                    model: filter.write_model,
                    method: 'search_read',
                    domain: [["user_id", "=", session.uid]],
                    fields: [filter.write_field],
                })
                .then(function (res) {
                    var records = _.map(res, function (record) {
                        var _value = record[filter.write_field];
                        var value = _.isArray(_value) ? _value[0] : _value;
                        var f = _.find(filter.filters, function (f) {return f.value === value;});
                        var formater = fieldUtils.format[_.contains(['many2many', 'one2many'], field.type) ? 'many2one' : field.type];
                        return {
                            'id': record.id,
                            'value': value,
                            'label': formater(_value, field),
                            'active': !f || f.active,
                        };
                    });
                    records.sort(function (f1,f2) {
                        return _.string.naturalCmp(f2.label, f1.label);
                    });

                    // add my profile
                    if (field.relation === 'res.partner' || field.relation === 'res.users') {
                        var value = field.relation === 'res.partner' ? session.partner_id : session.uid;
                        var me = _.find(records, function (record) {
                            return record.value === value;
                        });
                        if (me) {
                            records.splice(records.indexOf(me), 1);
                        } else {
                            var f = _.find(filter.filters, function (f) {return f.value === value;});
                            me = {
                                'value': value,
                                'label': session.name + _t(" [Me]"),
                                'active': !f || f.active,
                            };
                        }
                        records.unshift(me);
                    }
                    // add all selection
                    if (session.is_admin){
                        records.push({
                            'value': 'all',
                            'label': field.relation === 'res.partner' || field.relation === 'res.users' ? _t("Everybody's calendars") : _t("Everything"),
                            'active': filter.all,
                        });
                    }

                    filter.filters = records;
                });
        },
    });

});
