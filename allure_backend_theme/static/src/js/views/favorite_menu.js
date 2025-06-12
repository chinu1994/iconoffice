odoo.define('allure_backend_theme.FavoriteMenu', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var session = require('web.session');
    var rpc = require('web.rpc');
    var config = require('web.config');
    var QWeb = core.qweb;

    return Widget.extend({
        template: 'menu.FavoriteMenu',
        events: {
            'click .oe_apps_menu .o_app': '_onOpenMenu',
            'click .oe_apps_menu': '_onMenuFocus',
        },
        init: function () {
            this._super.apply(this, arguments);
            this._doInitMenu();
        },
        willStart: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self._doInitMenu().then(function (menu_data) {
                    var debug = config.debug ? '?debug' : '';
                    self.$el.append($(QWeb.render('menu.FavoriteMenuItem', {
                        menu_data: menu_data,
                        debug: debug,
                    })));
                });
            });
        },
        _doInitMenu: function() {
            var self = this;
            return rpc.query({
                model: 'ir.favorite.menu',
                method: 'search_read',
                args: [[['user_id', '=', session.uid]]],
                kwargs: {fields: ['id','favorite_menu_id','user_id','sequence','favorite_menu_xml_id','favorite_menu_action_id']}
            }).then(function (menu_data) {
                return menu_data;
            });
        },
        _onOpenMenu: function (event) {
            var self = this;
            var $el = $(event.currentTarget);
        },
        _onMenuFocus: function () {
            $('.o_search_menu .o_search_input').focus();
        },
    });
});