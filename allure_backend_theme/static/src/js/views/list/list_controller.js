odoo.define('allure_backend_theme.ListController', function (require) {
    "use strict";

    var core = require('web.core');
    var ListController = require('web.ListController');
    var ListRenderer = require('web.ListRenderer');
    var Dialog = require('web.Dialog');
    var session = require('web.session');
    var QWeb = core.qweb;

    var _t = core._t;

    var CustomizeList = Dialog.extend({
        dialog_title: _t("Customize List"),
        template: 'CustomizeList',
        events: _.extend({}, ListRenderer.prototype.events, {
            'click .btn': '_onChangeView',
        }),
        init: function (parent, state) {
            this.parent = parent;
            var self = this;
            this.default_density = state.displayDensity &&
                state.displayDensity.display_density || false;
            this._super(parent, {
                title: "Customize List",
                size: 'medium',
                buttons: [{
                    text: _t("Apply"),
                    close: true,
                    classes: 'btn-primary',
                    click: this._onClickSaveSettings.bind(self),
                }, {
                    text: _t('Cancel'),
                    close: true,
                }],
            });
        },
        _onChangeView: function (ev) {
            ev.preventDefault();
            this.default_density = $(ev.target).data('value');
            this.$('.o_density_image img').attr('src', '/allure_backend_theme/static/src/img/' + this.default_density + '.png')
        },
        _onClickSaveSettings: function (ev) {
            var self = this;
            return this._rpc({
                model: 'res.users',
                method: 'write',
                args: [session.uid, {display_density: self.default_density}],
            }).then(function (value) {
                self.parent.update({}, {reload: true})
            })
        },
    });

    ListController.include({
        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
            this.group_display_density = false;
        },
        willStart: function () {
            var self = this;
            return this.getSession().user_has_group('allure_backend_theme.group_display_density').then(function (has_group) {
                self.group_display_density = has_group;
            });
        },
        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            var state = this.model.get(this.handle);
            state.group_display_density = this.group_display_density;
            this.state = state;
            if (this.$buttons) {
                this.$buttons.on('click', '.o_display_density', this._onOpenSetting.bind(this));
            }
        },
        _reRenderAttachments: function(state, recordID){
            var record = _.findWhere(state.data, {id: recordID});
            if(record) {
                var rowIndex = _.findIndex(state.data, {id: recordID});
                var attachmentsData = _.filter(this.state.attachmentsData, function (rec) {
                    return rec[record.res_id];
                });
                var nbAttahments = _.filter(this.state.nbAttahments, function (rec) {
                    return rec[record.res_id];
                });
                if (attachmentsData.length !== 0) {
                    var $row = this.$('.o_data_row:nth(' + rowIndex + ')');
                    var $attech = $('<td/>', {class: 'o_attachment'});
                    if (this.state.displayDensity) {
                        $row.addClass('o_' + this.state.displayDensity.display_density);
                    }
                    $row.data('res_id', record.res_id);
                    $row.find('td:nth-child(2)').append($attech);
                    $row.find('.o_attachment').append(QWeb.render('ListView.Attachment', {
                        values: attachmentsData[0][record.res_id],
                    }));
                    if (nbAttahments.length !== 0 && nbAttahments[0][record.res_id] && nbAttahments[0][record.res_id] > 3) {
                        $row.find('.o_attachment').append('<div class="attachment-counter">' + (nbAttahments[0][record.res_id] - 3) + '</div>')
                    }
                }
            }
        },
        _onSaveLine: function (ev) {
            var recordID = ev.data.recordID;
            var state = this.model.get(this.handle);
            var default_density = state.displayDensity &&
                state.displayDensity.display_density || false;
            this.saveRecord(recordID)
                .done(ev.data.onSuccess)
                .fail(ev.data.onFailure);
            if(default_density && default_density === 'default') {
                this._reRenderAttachments(state, recordID);
            }
        },
        _confirmSave: function (id) {
            var self = this;
            var state = this.model.get(this.handle);
            var default_density = state.displayDensity &&
                state.displayDensity.display_density || false;
            return this._super.apply(this, arguments).then(function () {
                if(default_density && default_density === 'default'){
                    self._reRenderAttachments(state, id);
                }
            });
        },
        _onOpenSetting: function () {
            var state = this.model.get(this.handle);
            var default_density = state.displayDensity &&
                state.displayDensity.display_density || false;
            var $customize_list = new CustomizeList(this, state);
            $customize_list.open();
            $customize_list.opened().then(function () {
                $customize_list.$el.find('datavalue').focus();
                $customize_list.$('button[data-value = ' + default_density + ']').focus();
            });
        },
        _doUpdateSidebar: function () {
            if (this.selectedRecords.length > 0 && this.sidebar.$el.hasClass('o_drw_in')) {
                $('body').find('.ad_rightbar').addClass('o_open_sidebar');
            } else {
                $('body').find('.ad_rightbar').removeClass('o_open_sidebar');
            }
        },
        _toggleSidebar: function () {
            var self = this;
            this._super.apply(this, arguments);
            if (this.sidebar) {
                this.sidebar.do_toggle(this.selectedRecords.length > 0);
                this.sidebar.$el.addClass('o_drw_in');
                this._doUpdateSidebar();
            }
        },
    });
});
