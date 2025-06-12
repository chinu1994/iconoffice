odoo.define('allure_backend_theme.DashboardCustomizeTheme', function (require) {
    "use strict";

    var core = require('web.core');
    var web_settings_dashboard = require('web_settings_dashboard');
    var Widget = require('web.Widget');
    var Dialog = require('web.Dialog');
    var ajax = require('web.ajax');
    var session = require('web.session');
    var SystrayMenu = require('web.SystrayMenu');
    var framework = require('web.framework');
    var _t = core._t;

    var fields = {
        'leftbar_color': 'LeftBar',
        'menu_color': 'Menu',
        'buttons_color': 'Button',
        'button_box': 'Button Box',
        'heading_color': 'Heading',
        'label_color': 'Label',
        'label_value_color': 'Label Value',
        'link_color': 'Link Color',
        'panel_title_color': 'Panel Title',
        'tooltip_color': 'Tooltip',
        'border_color': 'Border',
        'base_form_tabs': 'Form Tab',
        'font_type_values': 'Font Value',
        'base_menu_icon': 'Icon Value',
        'tab_configration': 'Tab Configration',
        'base_menu': 'Menu Configration',
        'mode': 'Mode',
    };

    var status_colors = {
        'tag_info': '#00b3e5',
        'tag_danger': '#ca0c05',
        'tag_success': '#00aa00',
        'tag_warning': '#e47e01',
        'tag_primary': '#005ba9',
        'tag_muted': '#717171',
    };

    web_settings_dashboard.Dashboard.include({
        load: function (dashboards) {
            var self = this;
            var loading_done = new $.Deferred();
            this._rpc({route: '/web_settings_dashboard/data'})
                .then(function (data) {
                    // Load each dashboard
                    var all_dashboards_defs = [];
                    _.each(dashboards, function (dashboard) {
                        var dashboard_def = self['load_' + dashboard](data);
                        if (dashboard_def) {
                            all_dashboards_defs.push(dashboard_def);
                        }
                    });
                    var dashboard_def = self['load_customize_theme'](data);
                    if (dashboard_def) {
                        all_dashboards_defs.push(dashboard_def);
                    }
                    // Resolve loading_done when all dashboards defs are resolved
                    $.when.apply($, all_dashboards_defs).then(function () {
                        loading_done.resolve();
                    });
                });
            return loading_done;
        },
        load_customize_theme: function () {
        },
    });
    var CustomizeThemeDialog = Dialog.extend({
        dialog_title: _t('Customize Theme'),
        template: "CustomizeTheme",
        events: {
            'click .o_add_theme': '_onClickAddRecord',
            'click ul.oe_theme_colorpicker li .o_view': '_onClickSelectTheme',
            'click ul.oe_theme_colorpicker li .o_remove': '_onClickRemoveTheme',
            'click .o_radio_input': '_ontabClickOption',
            'click .o_switch_menu span': '_checkMenuOption',
            'click .nav-link': '_ontabClickOption',
        },
        init: function (parent, result, themeData) {
            var self = this;
            this.result = result;
            this.parent = parent;
            this.theme_id = parent.theme_id;
            this.themeData = themeData;
            this.group_system = parent.group_system;
            $('body').addClass('open_customize_theme');
            this._super(parent, {
                title: _t('Customize Theme'),
                buttons: [{
                    text: _t('Apply'),
                    classes: 'btn-primary',
                    click: function () {
                        self._onClickSaveTheme();
                    },
                }, {
                    text: _t('Cancel'),
                    close: true,
                }],
            });
        },
        start: function () {
            var self = this;
            this.form_values = {};
            this.invalidFields = [];
            var themeData;

            this.$('.o_colorpicker').each(function () {
                $(this).minicolors({
                    control: 'hue',
                    inline: false,
                    letterCase: 'lowercase',
                    opacity: false,
                    theme: 'bootstrap'
                });
            });
            if (!_.isEmpty(this.result)) {
                this.current_theme = _.findWhere(this.result, {'selected': true});
                if (!_.isUndefined(this.current_theme)) {
                    self._fetchThemeData(self.current_theme.id);
                }
            }
            if (self.themeData && self.themeData.mode === 'night_mode_on') {
                self.$el.addClass('night_mode_on');
            }
            return this._super.apply(this, arguments);
        },
        close: function () {
            this.parent.customizeDialog = false;
            $('body').removeClass('open_customize_theme');
            this._super.apply(this, arguments);
        },
        destroy: function (options) {
            this.parent.customizeDialog = false;
            $('body').removeClass('open_customize_theme');
            this._super.apply(this, arguments);
        },
        _onClickAddRecord: function () {
            this.$el.addClass('o_new_record');
            this.$('.o_control_form').find('input.minicolors-input').minicolors('value', '');
            this.$('.o_breadcrumb_form').find('input').minicolors('value', '');
        },
        _setSelectedTheme: function (result) {
            var self = this;
            this.$el.removeClass('o_new_record');
            _.each(result, function (value, field) {
                if (!_.contains(['base_form_tabs', 'font_type_values', 'base_menu_icon',
                    'tab_configration', 'base_menu', 'mode'], field)) {
                    self.$('input[name=' + field + ']').minicolors('value', value);
                } else {
                    if (!_.contains(['base_form_tabs', 'tab_configration', 'base_menu', 'font_type_values', 'mode'], field)) {
                        self.$('input[value="' + value + '"]').prop("checked", true);
                    } else if (self.themeData) {
                        self.$('input[value="' + self.themeData.tab_type + '"]').prop("checked", true);
                        self.$('input[value="' + self.themeData.tab_configration + '"]').prop("checked", true);
                        self.$('input[value="' + self.themeData.base_menu + '"]').prop("checked", true);
                        self.$('input[value="' + self.themeData.font_type_values + '"]').prop("checked", true);
                        self.$('input[value="' + self.themeData.mode + '"]').prop("checked", true);
                        self.$('input[value="' + self.themeData.base_menu_icon + '"]').prop("checked", true);
                    }
                    self.$el.find('.tab_configration_data').toggle(value == 'vertical_tabs');
                }
            });
            this._ontabClickOption(result);
        },
        _fetchThemeData: function (theme_id) {
            var self = this;
            var form_fields = _.keys(fields);
            this._rpc({
                model: 'ir.web.theme',
                method: 'search_read',
                domain: [['id', '=', theme_id]],
                fields: form_fields,
            }).then(function (result) {
                self._setSelectedTheme(result[0]);
            });
        },
        _removeTheme: function ($li, res_id) {
            var self = this;
            self._rpc({
                model: 'ir.web.theme',
                method: 'unlink',
                args: [parseInt(res_id, 10)],
            }).then(function (value) {
                $li.remove();
                self.do_notify(_t("Sucsess"), _t("Theme removed successfully."));
            })
        },
        _onClickSelectTheme: function (e) {
            var self = this;
            this.$el.find('ul li').removeClass('selected');
            $(e.currentTarget).parents('li').addClass('selected');
            var res_id = $(e.currentTarget).parents('li').find('span').data('id');
            if (res_id !== 0) {
                self._fetchThemeData(res_id);
            }
        },
        _onClickRemoveTheme: function (e) {
            var self = this;
            var res = confirm(_t("Do you want to delete this record?"));
            if (res) {
                var res_id = $(e.currentTarget).parents('li').find('span').data('id');
                if (res_id !== 0) {
                    var $li = $(e.currentTarget).parents('li');
                    self._removeTheme($li, res_id);
                }
            }
        },
        _checkMenuOption: function (e) {
            var $data = $(e.currentTarget).parents('.o_switch_menu')
            $data.toggleClass("css_horizontal_menu");
        },
        _createRecord: function (form_values) {
            return this._rpc({
                model: 'ir.web.theme',
                method: 'create',
                args: [form_values],
                kwargs: {context: session.user_context},
            });
        },
        _updateRecord: function (theme_id, form_values) {
            var self = this, user_vals = {};
            if (form_values) {
                user_vals = {
                    'tab_type': form_values.base_form_tabs,
                    'tab_configration': form_values.tab_configration,
                    'base_menu': form_values.base_menu,
                    'font_type_values': form_values.font_type_values,
                    'mode': form_values.mode,
                };
            }
            return this._rpc({
                model: 'ir.web.theme',
                method: 'write',
                args: [[theme_id], form_values],
            }).then(function (value) {
                return self._rpc({
                    model: 'res.users',
                    method: 'write',
                    args: [[session.uid], user_vals],
                })
            });
        },
        _changeCurrentTheme: function (theme_id) {
            var self = this;
            return this._rpc({
                model: 'ir.web.theme',
                method: 'set_customize_theme',
                args: [[], theme_id, self.form_values],
            }).then(function () {
                location.reload();
            });
        },
        _notifyInvalidFields: function (invalidFields) {
            var warnings = invalidFields.map(function (fieldName) {
                var fieldStr = fields[fieldName];
                return _.str.sprintf('<li>%s</li>', _.escape(fieldStr));
            });
            warnings.unshift('<ul>');
            warnings.push('</ul>');
            this.do_warn(_t("The following fields are invalid:"), warnings.join(''));
        },
        _doChangeTheme: function (theme_id) {
            var self = this;
            self._changeCurrentTheme(theme_id).then(function () {
                self.do_notify(_t("Sucsess"), _t("Theme customized successfully."));
                self.close(true);
                return;
            });
        },
        _onClickSaveTheme: function () {
            var self = this, theme_id;
            var form_fields = this.$('.o_control_form').serializeArray();
            _.each(form_fields, function (input) {
                if (input.value !== '') {
                    self.form_values[input.name] = input.value;
                } else if (!self.$el.hasClass('night_mode_on')) {
                    self.invalidFields.push(input.name);
                }
            });

            if (!_.isEmpty(self.invalidFields)) {
                self._notifyInvalidFields(self.invalidFields);
                self.invalidFields = [];
                return false;
            } else {
                if (self.$el.hasClass('o_new_record') && !self.$el.hasClass('night_mode_on')) {
                    self._createRecord(self.form_values).then(function (theme_id) {
                        self._doChangeTheme(theme_id);
                    })
                } else {
                    theme_id = this.$el.find('ul li.selected span').data('id');
                    theme_id = theme_id || self.theme_id;
                    if (theme_id && !_.isUndefined(theme_id) && theme_id !== 0) {
                        self._updateRecord(parseInt(theme_id), self.form_values).then(function () {
                            self._doChangeTheme(parseInt(theme_id));
                        })
                    }
                }
            }
            if (self.group_system) {
                self._create_icon(self.form_values);
            }
        },
        _create_icon: function (form_values) {
            var self = this;
            return this._rpc({
                model: 'ir.ui.menu',
                method: 'icon_menu_chnange',
                args: [[], self.form_values],
            });
        },
        _ontabClickOption: function (event) {
            var self = this;
            var $activetab = $(event.target).closest('.oe_teb_view').attr('value');
            var form_fields = this.$('.o_control_form').serializeArray();
            var imagePath = '/allure_backend_theme/static/src/img/';
            var $night_mode = _.findWhere(form_fields, {'name': 'mode'})
            var $tab_data = _.findWhere(form_fields, {'name': 'base_form_tabs'})
            if ($activetab) {
                var data = _.findWhere(form_fields, {'name': $activetab});
                self.$el.find('.uc_menu_image').attr('src', imagePath + data["value"] + '.png');
            } else {
                self.$el.find('.uc_menu_image').attr('src', '/allure_backend_theme/static/src/img/theme_help.png');
            }
            self.$el.find('.tab_configration_data').toggle($tab_data["value"] == 'vertical_tabs');
            self.$el.toggleClass('night_mode_on', $night_mode["value"] == 'night_mode_on');
        },
    });
    var DashboardCustomizeTheme = Widget.extend({
        template: 'DashboardThemeColors',
        events: {
            'click .o_setup_theme': '_onClickSetupTheme',
        },
        init: function (parent) {
            this.parent = parent;
            this.group_system = false;
            this.customizeDialog = false;
            this.group_theme_config = false;
            this._super.apply(this, arguments);
        },
        willStart: function () {
            var self = this;
            return self._rpc({
                model: 'res.users',
                method: 'search_read',
                domain: [['id', '=', session.uid]],
                fields: ['mode'],
            }).then(function (results) {
                self.nightMode = results[0] && results[0].mode || false;
                self.getSession().user_has_group('base.group_system').then(function (has_group) {
                    self.group_system = has_group;
                });
                return self.getSession().user_has_group('allure_backend_theme.group_theme_setting_user').then(function (is_theme_access) {
                    self.group_theme_config = is_theme_access
                });
            });
        },
        start: function () {
            this._super.apply(this, arguments);
            if (this.nightMode && this.nightMode === 'light_mode_on') {
                $('body').addClass('light_mode_on');
            }
            if (this.nightMode && this.nightMode === 'night_mode_on') {
                return this.load_xml_data();
            }
        },
        _doNightModeEnable: function () {
            if (this.nightMode && this.nightMode === 'night_mode_on') {
                $('body').addClass('oe_night_mode');
            }
        },
        load_xml_data: function () {
            var self = this;
            return ajax.jsonRpc('/web/theme_customize_backend_get', 'call', {
                'xml_ids': ['allure_backend_theme.night_mode_on']
            }).done(function (data) {
                if (self.nightMode && (data[0].length === 0 && data[1].length === 1 && self.nightMode === 'night_mode_on')
                    || (data[0].length === 1 && data[1].length === 0 && self.nightMode === 'night_mode_off')) {
                    self._onClickNightTheme(data);
                } else {
                    self._doNightModeEnable();
                }
            });
        },
        _onClickNightTheme: function (data) {
            var self = this;
            framework.blockUI();
            return this._rpc({
                model: 'ir.ui.view',
                method: 'set_night_mode',
                args: [[], {
                    enable: data[1],
                    disable: data[0],
                    get_bundle: true
                }],
            }).then(function (bundleHTML) {
                framework.blockUI();
                var $links = $('link[href*=".assets_backend"]');
                var $newLinks = $(bundleHTML).filter('link');
                var linksLoaded = $.Deferred();
                var nbLoaded = 0;
                $newLinks.on('load', function (e) {
                    if (++nbLoaded >= $newLinks.length) {
                        linksLoaded.resolve();
                    }
                });
                $links.last().after($newLinks);
                return linksLoaded.then(function () {
                    $links.remove();
                    self._doNightModeEnable();
                    framework.unblockUI();
                });
            });
        },
        _onClickSetupTheme: function (event) {
            event.stopPropagation();
            event.preventDefault();
            var self = this;
            if (!this.customizeDialog) {
                self.customizeDialog = true;
                var form_fields = _.keys(fields);
                self._rpc({
                    model: 'ir.web.theme',
                    method: 'search_read',
                    fields: form_fields,
                }).then(function (result) {
                    self._rpc({
                        model: 'ir.web.theme',
                        method: 'get_current_theme',
                        args: []
                    }).then(function (theme_id) {
                        self.theme_id = theme_id;
                        _.each(result, function (rec, i) {
                            result[i]['selected'] = (rec.id === parseInt(theme_id));
                        });
                        self._rpc({
                            model: 'res.users',
                            method: 'search_read',
                            domain: [['id', '=', session.uid]],
                            fields: ['id', 'tab_type', 'tab_configration', 'base_menu', 'font_type_values', 'mode'],
                        }).then(function (results) {
                            var themeData = results[0];
                            return new CustomizeThemeDialog(self, result, themeData).open();
                        });
                    });
                })
            } else {
                $('footer.modal-footer .btn-secondary').click();
            }
        },
    });

    SystrayMenu.Items.push(DashboardCustomizeTheme);
    return SystrayMenu;
});
