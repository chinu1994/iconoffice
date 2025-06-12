odoo.define('allure_backend_theme.AppsMenu', function (require) {
    "use strict";

    var AppsMenu = require('web.AppsMenu');
    var session = require('web.session');
    var core = require('web.core');
    var ajax = require('web.ajax');
    var QWeb = core.qweb;

    AppsMenu.include({
        events: _.extend({}, AppsMenu.prototype.events, {
            'input input.o_search_input': '_onChange',
            'keydown input[name=search_menu]': '_keyDown',
            'click .menuitem': '_initSearch',
            'click a.o_app': '_onClickApp',
        }),
        init: function (parent, menuData, menuConfiguration) {
            this._super.apply(this, arguments);
            // Menu search
            this.input_val = false;
            this.menu_items = [];
            this.current_result = null;
            this.count = 0;
            // Menu Search
            this._activeApp = undefined;
            this.company_id = session.company_id;
            this.menuType = menuConfiguration;
            this._apps = _.map(menuData.children, function (appMenuData) {
                return {
                    actionID: parseInt(appMenuData.action.split(',')[1]),
                    menuID: appMenuData.id,
                    name: appMenuData.name,
                    xmlID: appMenuData.xmlid,
                    menuIcon: '/web/image/ir.ui.menu/' + appMenuData.id + '/theme_icon_data/60x60'
                };
            });
        },

        start: function () {
            this._super.apply(this, arguments);
            this.menu_items = ajax.jsonRpc('/all/menu/search', 'call', {})
            this.menubox = $('.oe_apps_menu');
            this.inputval = this.$el.find('.o_search_input');
        },

        _onChange: function (e) {
            this.input_val = e.currentTarget.value;
            var input_val = this.input_val;
            var self = this;
            var menu_items = [];
            self.current_result = null;
            this.menu_items.then(function (data) {
                if (input_val) {
                    var search_menus = fuzzy.filter(input_val, _.pluck(data, 'name'));
                    var result_menu = _.map(search_menus, function (result) {
                        return data[result.index];
                    });
                    _.each(result_menu, function (all_menu) {
                        menu_items.push({
                            action: parseInt(all_menu.action.split(',')[1]),
                            id: all_menu.id,
                            name: all_menu.name,
                            complete_name: all_menu.complete_name.split('/').slice(0, -1).join(' / '),
                            parentID: all_menu.parent_path.split('/')[0],
                        });
                    });
                } else {
                    menu_items = [];
                }
            });
            this.$el.find('.oe_apps_menu').html(QWeb.render('AppsMenuFilter', {
                widget: this,
                menu_items: menu_items,
            }));
            self.$el.find('.oe_apps_menu .o_app').draggable({
                helper: "clone"
            });
        },

        _keyDown: function (e) {
            var self = this;
            var switchmenu = this.menubox.find(".menuitem_data"),
                pre_focused = switchmenu.filter(".active") || $(switchmenu[0]),
                offsetval = switchmenu.index(pre_focused);
            switch (e.which) {
                case $.ui.keyCode.ENTER:
                    var menu_id = pre_focused.attr('data-menu-id'),
                        action_id = pre_focused.attr('data-action-id'),
                        parent_id = pre_focused.attr('data-parent-id');
                    if (action_id) {
                        self.select_item(menu_id, action_id, parent_id);
                        this._initSearch(e);
                    }
                    this._onChange(e);
                    break;
                case $.ui.keyCode.DOWN:
                    offsetval++;
                    e.preventDefault();
                    break;
                case $.ui.keyCode.UP:
                    offsetval--;
                    e.preventDefault();
                    break;
                case $.ui.keyCode.RIGHT:
                    offsetval++;
                    e.preventDefault();
                    break;
                case $.ui.keyCode.LEFT:
                    offsetval--;
                    e.preventDefault();
                    break;
                case $.ui.keyCode.TAB:
                    offsetval++;
                    e.preventDefault();
                    break;
            }
            var new_focused = $(switchmenu[offsetval]);
            var $main_menu = $('.main_menu');
            pre_focused.removeClass("active");
            new_focused.addClass("active");
            if (new_focused.length) {
                $main_menu.scrollTo(new_focused, {
                    offset: {
                        top: $main_menu.height() * -0.5,
                    },
                });
            }
        },

        _initSearch: function (e) {
            $('body').removeClass('ad_open_childmenu').toggleClass('nav-sm');
            this.inputval.focus().val('');
            this._onChange(e);
        },

        _onClickApp: function (e) {
            this._initSearch(e);
        },

        /**
         * @returns {Object[]}
         */
        getApps: function () {
            if (this.input_val) {
                var installed_apps = this._apps;
                var search_apps = fuzzy.filter(this.input_val, _.pluck(installed_apps, 'name'));
                var filtered_apps = []
                _.each(search_apps, function (app) {
                    _.each(installed_apps, function (all_app) {
                        if (app['string'] === all_app['name'])
                            filtered_apps.push(all_app);
                    })
                });
                return filtered_apps;
            } else {
                return this._apps;
            }
        },

        move: function (direction) {
            var $next;
            if (direction === 'down') {
                this.count = this.count + 1;
                $next = this.$('li.o-selection-focus').next();
                if (!$next.length) $next = this.$('li').first();
            } else {
                $next = this.$('li.o-selection-focus').prev();
                this.count = this.count - 1;
                if (!$next.length) $next = this.$('li').last();
            }

            var elHeight = $next.height();
            var scrollTop = this.$('ul.menu_item_list').scrollTop();
            var viewport = scrollTop + this.$('ul.menu_item_list').height();
            var elOffset = elHeight * this.count;

            this.focus_element($next);

            if (elOffset < scrollTop || (elOffset + elHeight) > viewport) {
                this.$('ul.menu_item_list').animate({scrollTop: elOffset}, 50);
            }
        },

        focus_element: function ($li) {
            this.remove_focus($li);
            $li.addClass('o-selection-focus selected');
            if ($li.length) {
                this.current_result = $li[0].dataset;
            }
        },

        remove_focus: function ($li) {
            this.$('li').removeClass('o-selection-focus selected');
            this.current_result = null;
        },

        select_item: function (menu_id, action_id, parent_id) {
            this.trigger_up('menu_clicked', {
                id: menu_id,
                action_id: action_id,
            });
            core.bus.trigger("change_menu_section", parseInt(parent_id));
        },
    });
});