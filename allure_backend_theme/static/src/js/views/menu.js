// odoo Menu inherit Open time has Children submenu add.
odoo.define('allure_backend_theme.Menu', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var Menu = require('web.Menu');
    var UserMenu = require('web.UserMenu');
    var FavoriteMenu = require('allure_backend_theme.FavoriteMenu');
    var config = require('web.config');
    var session = require('web.session');
    var AppsMenu = require('web.AppsMenu');
    var SystrayMenu = require('web.SystrayMenu');
    var rpc = require('web.rpc');
    var dom = require('web.dom');

    var QWeb = core.qweb;
    var LogoutMessage = Widget.extend({
        template: 'LogoutMessage',
        events: {
            'click  a.oe_cu_logout_yes': '_onClickLogout',
            'click  .mb-control-close': '_onClickClose',
        },
        init: function (parent) {
            this._super(parent);
        },
        _onClickLogout: function (e) {
            var self = this;
            self.getParent()._onMenuLogout();
        },
        _onClickClose: function (e) {
            this.$el.remove();
        }
    });

    UserMenu.include({
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                var $avatar = self.$('.oe_topbar_avatar');
                var avatar_src = session.url('/web/image', {
                    model: 'res.users',
                    field: 'image',
                    id: session.uid,
                });
                $avatar.attr('src', avatar_src);
                self.$el.on('click', 'a.o_menu_logout', function (ev) {
                    ev.preventDefault();
                    return new LogoutMessage(self).appendTo(self.$el.closest('body'));
                });
            });
        },
    });

    Menu.include({
        events: _.extend({}, Menu.prototype.events, {
            'click #menu_toggle': '_onMenuToggleClicked',
            'click #children_toggle': '_onSubmenuToggleClicked',
            'click #av_full_view': '_onFullViewClicked',
            'click a[data-action]': '_onMenuClose',
            'click .o_app': '_onSubmenuClose',
            'click a[data-menu]': '_onMenuClose',
            'click .o_mail_preview': '_onMenuClose',
            'click .oe_full_button': '_onFullScreen',
            'click .o_mobile_menu_toggle': '_onMobileMenu',
            'click .main_menu': '_onFocusSearch',
            'click .user_menu': '_onSystrayOpen',
            'dragstop .main_menu .oe_apps_menu .dropdown-item': '_ondragStop',
            'dragstart .main_menu .oe_apps_menu .dropdown-item': '_ondragStart',
        }),
        init: function (parent, menu_data) {
            this._super.apply(this, arguments);
            this.company_id = session.company_id;
            this.user_id = session.uid;
            this.menu_id = true;
            this.themeData = {};
        },
        willStart: function () {
            var self = this;
            return self._rpc({
                model: 'res.users',
                method: 'search_read',
                domain: [['id', '=', session.uid]],
                fields: ['base_menu'],
            }).then(function (results) {
                self.themeData = results[0];
            });
        },
        start: function () {
            var self = this;
            if (this.themeData && this.themeData.base_menu === 'base_menu') {
                $('body').addClass('oe_base_menu');
                this.$('.o_main_navbar').replaceWith($(QWeb.render('MenuTitle')));
            }
            this.$av_full_view = this.$('#av_full_view');
            this.$menu_toggle = this.$('#menu_toggle');
            this.$menu_brand_placeholder = this.$('.o_menu_brand');
            this.$section_placeholder = this.$('.o_menu_sections');
            this.$menu_apps = this.$('.o_menu_apps');
            if (this.themeData && this.themeData.base_menu === 'base_menu' && !config.device.touch) {
                dom.initAutoMoreMenu(this.$section_placeholder, {
                    maxWidth: function () {
                        return self.$el.width() - (self.$av_full_view.outerWidth(true) + self.$menu_toggle.outerWidth(true) + self.$menu_brand_placeholder.outerWidth(true) + self.systray_menu.$el.outerWidth(true));
                    },
                    sizeClass: 'SM',
                });
            }
            // Navbar's menus event handlers
            var on_secondary_menu_click = function (ev) {
                ev.preventDefault();
                var menu_id = $(ev.currentTarget).data('menu');
                var action_id = $(ev.currentTarget).data('action-id');
                self._on_secondary_menu_click(menu_id, action_id);
            };
            var menu_ids = _.keys(this.$menu_sections);
            var primary_menu_id, $section;
            for (var i = 0; i < menu_ids.length; i++) {
                primary_menu_id = menu_ids[i];
                $section = this.$menu_sections[primary_menu_id];
                $section.on('click', 'a[data-menu]', self, on_secondary_menu_click.bind(this));
            }

            // Apps Menu
            this._appsMenu = new AppsMenu(self, this.menu_data, this.themeData);
            this._appsMenu.appendTo(this.$menu_apps);

            // Systray Menu
            this.systray_menu = new SystrayMenu(this);
            this.systray_menu.attachTo(this.$('.o_menu_systray'));
            this._loadQuickMenu();
        },
        _onMenuToggleClicked: function (e) {
            var key = jQuery.Event("keydown");
            key.which = 13;
            $('body').removeClass('ad_open_childmenu').toggleClass('nav-sm');
            $(this).toggleClass('active');
            this.$el.find('.o_search_menu .o_search_input').focus().val('');
            this.$el.find('.o_search_menu .o_search_input').trigger(key);
        },
        _onFocusSearch: function () {
            this.$el.find('.o_search_menu .o_search_input').focus();
        },
        _onSubmenuToggleClicked: function (e) {
            $('body').removeClass('nav-sm').toggleClass('ad_open_childmenu');
            $(this).toggleClass('active');
        },
        _onMobileMenu: function (e) {
            $('body').toggleClass('open_mobile_menu');
        },
        _onMobileMenuClose: function (e) {
            $('body').removeClass('open_mobile_menu');
        },
        _onSubmenuClose: function (e) {
            $('body').removeClass('nav-sm');
        },
        change_menu_section: function (primary_menu_id) {
            var self = this;
            if (!this.$menu_sections[primary_menu_id]) {
                this._updateMenuBrand();
                return; // unknown menu_id
            }

            if (this.current_primary_menu === primary_menu_id) {
                return; // already in that menu
            }

            if (this.current_primary_menu) {
                this.$menu_sections[this.current_primary_menu].detach();
            }

            // Get back the application name
            for (var i = 0; i < this.menu_data.children.length; i++) {
                if (this.menu_data.children[i].id === primary_menu_id) {
                    this._updateMenuBrand(this.menu_data.children[i].name);
                    break;
                }
            }
            if (this.themeData && this.themeData.base_menu === 'base_menu') {
                this.$menu_sections[primary_menu_id].appendTo(this.$section_placeholder);
                this.current_primary_menu = primary_menu_id;
            } else {
                // Selcted Menu
                var submenu_data = _.findWhere(this.menu_data.children, {id: primary_menu_id});
                this.menu_id = submenu_data;
                var $submenu_title = $(QWeb.render('SubmenuTitle', {
                    selected_menu: submenu_data,
                }));
                this.$section_placeholder.html($submenu_title);
                $('<div>', {
                    class: 'o_submenu_list',
                }).append(this.$menu_sections[primary_menu_id]).appendTo(this.$section_placeholder);
                this.current_primary_menu = primary_menu_id;
                $('body').toggleClass('ad_nochild', !submenu_data.children.length);

                if ($('body').hasClass('ad_open_childmenu') && !submenu_data.children.length) {
                    $('body').removeClass('ad_open_childmenu')
                }
            }
            core.bus.trigger('resize');

            if (!config.device.touch){
                self._onAddElement();
                self._onRemoveElement();
                self._onSortableElement();
                self._onDraggableElement();
            }
        },
        renderFavoriteMenuElement: function () {
            var self = this;
            rpc.query({
                model: 'ir.favorite.menu',
                method: 'search_read',
                args: [[['user_id', '=', session.uid]]],
                kwargs: {fields: ['favorite_menu_id', 'user_id', 'sequence', 'favorite_menu_xml_id', 'favorite_menu_action_id']}
            }).then(function (menu_data) {
                var debug = config.debug ? '?debug' : '';
                self.$el.find('.oe_favorite_menu').html(QWeb.render("menu.FavoriteMenuItem", {
                    menu_data: menu_data,
                    debug: debug
                }));
                self._onSortableElement();
                self._onDraggableElement();
            });
        },
        _onSortableElement: function () {
            self = this;
            self.$el.find('#oe_shorting').sortable({
                start: function(event, ui){
                    self.$el.find('.oe_apps_menu').addClass('oe_view_delete');
                },
                stop: function (event, ui) {
                    self.$el.find('.oe_apps_menu').removeClass('oe_view_delete');
                    ui.item.trigger('drop', ui.item.index());
                    var dragMenu = parseInt($(ui.item).attr('data-menu-sequence'));
                    var nextMenu = $(ui.item).nextAll();
                    nextMenu.each(function () {
                        var vals = {}
                        dragMenu = dragMenu + 1;
                        var menu_id = $(this).attr('data-favorite-menu');
                        vals['sequence'] = dragMenu;
                        vals['favorite_menu_id'] = $(this).attr('data-menu-id');
                        self._rpc({
                            model: 'ir.favorite.menu',
                            method: 'write',
                            args: [[menu_id], vals],
                        });
                    });
                }
            });
        },
        _onDraggableElement: function () {
            self.$el.find('.main_menu .oe_apps_menu .o_app').draggable({
                helper: "clone",
            });
        },
        _onRemoveElement: function () {
            $('.main_menu .oe_apps_menu').droppable({
                tolerance: 'pointer',
                drop: _.bind(function (event, ui) {
                    if ($(ui.draggable).hasClass('oe_favorite')) {
                        var data = $(ui.draggable).attr('data-menu-id');
                        var user = session.uid;
                        self._rpc({
                            model: 'ir.favorite.menu',
                            method: 'unlink_menu_id',
                            args: [[], user, parseInt(data)],
                        }).then(function (data) {
                            self.renderFavoriteMenuElement();
                        });
                    }
                }, this),
            });
        },
        _ondragStop: function(){
            if (!config.device.touch){
                self.$el.find('.oe_favorite_menu').removeClass('oe_dropable_view');
                $('body').removeClass('position-fixed');
            }
        },
        _ondragStart: function(){
            if (!config.device.touch){
                self.$el.find('.oe_favorite_menu').addClass('oe_dropable_view');
                $('body').addClass('position-fixed');
            }
        },
        _onAddElement: function () {
            $('.oe_favorite_menu').droppable({
                tolerance: 'pointer',
                drop: _.bind(function (event, ui) {
                    var has_icon = true;
                    var data = $(ui.draggable).attr('data-menu-id');
                    var data_xml = $(ui.draggable).attr('data-menu-xmlid');
                    var data_action_id = $(ui.draggable).attr('data-action-id');
                    var user = session.uid;
                    var object = $(event.target).find('.oe_apps_menu').children();
                    var sequence = $(ui.draggable).attr('data-menu-sequence');
                    $(object).each(function () {
                        var menu_ids = $(this).attr('data-menu-id');
                        if (menu_ids == data) {
                            has_icon = false;
                        }
                    });
                    if (has_icon) {
                        this._rpc({
                            model: 'ir.favorite.menu',
                            method: 'create',
                            args: [{
                                favorite_menu_id: data,
                                favorite_menu_xml_id: data_xml,
                                favorite_menu_action_id: data_action_id,
                                user_id: user
                            }],
                        }).then(function (ID) {
                            if (ID) {
                                self.renderFavoriteMenuElement();
                            }
                        });
                    }
                }, this),
            });
        },
        _onFullViewClicked: function (e) {
            $('body').toggleClass('ad_full_view');
        },
        _onFullScreen: function (e) {
            document.fullScreenElement && null !== document.fullScreenElement || !document.mozFullScreen &&
            !document.webkitIsFullScreen ? document.documentElement.requestFullScreen ? document.documentElement.requestFullScreen() :
                document.documentElement.mozRequestFullScreen ? document.documentElement.mozRequestFullScreen() :
                    document.documentElement.webkitRequestFullScreen && document.documentElement.webkitRequestFullScreen(Element.ALLOW_KEYBOARD_INPUT) :
                document.cancelFullScreen ? document.cancelFullScreen() :
                    document.mozCancelFullScreen ? document.mozCancelFullScreen() :
                        document.webkitCancelFullScreen && document.webkitCancelFullScreen()
        },
        _onMenuClose: function (e) {
            $('body').removeClass('open_mobile_menu');
            $('.o_menu_systray').removeClass('show');
            if (config.device.touch || config.device.size_class <= config.device.SIZES.MD){
                $('body').removeClass('ad_open_childmenu').removeClass('nav-sm');
            }
        },
        _onSystrayOpen: function (e) {
            $('body').removeClass('ad_open_childmenu').removeClass('nav-sm');
            $('body').removeClass('open_mobile_menu');
        },
        _loadQuickMenu: function () {
            var self = this;
            new FavoriteMenu(self).appendTo(this.$el.parents('.o_web_client').find('.oe_menu_layout.oe_theme_menu_layout'));
            this.$el.parents('.o_web_client').find('.o_menu_systray li.o_global_search').remove();
        },
    });
});